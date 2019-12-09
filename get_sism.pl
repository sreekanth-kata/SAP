#!/usr/bin/perl

use strict;
use lib "/srv/apps/webservice";
use lib "/srv/www/httpd003/w3/corp-tools/sismapi";
use sism_request_emcp_interface;
use DBI;
use Socket;
use Rtrif_aw;
use Data::Dumper;
use feature 'say';

my $dbhost = "netsecdbp01.wdf.sap.corp";
my $DB_DSN = "DBI:mysql:database=iptool;host=$dbhost";
my $DB_USER = "iptool_ro";
my $DB_PASS = "\$u4NitoT";

my $dbh = DBI->connect($DB_DSN, $DB_USER, $DB_PASS) ||
        (err_exit ("Cannot connect to ipaddr DB\n"));

#use warnings;

use CGI qw (:standard);
my $query = new CGI;
my $host = $query->param("host");
my $sid = $query->param("sid");
my $network = $query->param("network");
my $netstat = $query->param("netstat");
my $switch = $query->param("switch");
#my $switch = "10.67.36.126"; 

my $rtrif = Rtrif->new();

my $ret;
my $srv;
my @hosts;
my %HOSTS;

# disable buffering
$| = 1;

print "Content-type:text/html\n\n";

print "<html>\n";
print "<head><title>Netsec interface to SISM</title>\n";
   #print "<script type=\"text / javascript\">\n";
   #print qq~
   #function doalert(obj){
   #      alert(document.getElementById("clkid").value(obj));
   #      #return false;
   #}
   #~;
   #print "</script>\n";
print "</head>\n";

print "<body>\n";
if ($network){
        print "<table border=\"0\" cellpadding=\"0\" cellspacing=\"1\" width=\"750\">\n";
        my ($net,$mask) = (split(/\//,$network))[0];
        my $sth = $dbh->prepare("select h.name from ipaddr i,hosts h where i.net_addr=inet_aton('$net')
                                 and i.ip_addr=h.ip_addr");
        $sth->execute;
        while (my $host = $sth->fetchrow) { push (@hosts, $host);$HOSTS{$host} = 1 }
        $sth->finish;
}
elsif ($switch){
        print "<table border=\"0\" cellpadding=\"0\" cellspacing=\"1\" width=\"1500\">\n";
        $srv = $rtrif->getServers($switch);
        foreach my $key (keys %{$srv}){
                next unless $key;
                push (@hosts, $key);
                $HOSTS{$key} = 1;
        }
        #print keys %{$srv};

}
elsif ($host) {
        print "<table border=\"0\" cellpadding=\"0\" cellspacing=\"1\" width=\"750\">\n";
        @hosts = split(/\s+/,$host);
}

#call the soap_request method for getting hostnames corresponding object_keys
my %hashobj;
my @temparr;
foreach my $num (@hosts){
        push @temparr, MyObjs::SOAPrequest($num);
        $hashobj{$num} = shift(@temparr);
}
   #foreach my $k (keys(%hashobj)){
    #   say $k . ":" . $hashobj{$k};
    #}

#use sism package
use lib "/srv/apps/corp-tools/sism";
use SISM qw(getPhysicalHostbySID getSIDbyPhysicalHost);

if (defined @hosts){
        if ($switch){
        #say @hosts;
        print "<tr bgcolor=\"#FFFF66\"><th width=\"250\" height=\"40\">Hostname</th><th width=\"250\" height=\"40\">SID</th><th width=\"250\" height=\"30\">IP Address</th><th width=\"250\" height=\"40\">MAC Address</th><th width=\"250\" height=\"40\">MAC Age</th><th width=\"250\" height=\"40\">Switchport</th><th width=\"250\" height=\"40\">ObjectKey</th></tr>\n"
                } else {
                print "<tr bgcolor=\"#FFFF66\"><th width=\"250\" height=\"40\">Hostname</th><th width=\"250\" height=\"40\">SID</th><th width=\"250\" height=\"30\">IP Address</th></tr>\n";
        }
        $ret = getSIDbyPhysicalHost(@hosts);
        #print Dumper $ret;  #not printing
}
elsif ($sid) {
        print "<table border=\"0\" cellpadding=\"0\" cellspacing=\"1\" width=\"750\">\n";
        print "<tr bgcolor=\"#FFFF66\"><th width=\"250\" height=\"30\">SID</th><th width=\"250\" height=\"30\">Hostname</th><th width=\"250\" height=\"40\">IP Address</th></tr>\n";
        $sid = uc($sid);
        my @sids = split(/\s+/,$sid);
        $ret = getPhysicalHostbySID(@sids);
}

foreach my $key (keys %{$ret}){   #hash
        print "<h3>$key</h3><br>\n" if ($sid && $netstat);
        foreach my $item (@{$ret->{$key}}){ #array
                #print @{$ret->{$key}};

                if ($sid && $netstat){
                        print_report($item);
                } else {
                        my ($packip,$ip_addr);
                        if ($sid) {
                                $packip = gethostbyname($item)
                        } else {
                                $packip = gethostbyname($key)
                        }
                        $ip_addr = inet_ntoa($packip);
                        if ($switch){   #onclick=\"doalert(this); return false;\"
                                print "<tr bgcolor=\"#FFFF66\"><th width=\"250\" height=\"40\">$key</th><th width=\"250\" height=\"40\">$item</th><th width=\"250\" height=\"30\">$ip_addr</th><th width=\"250\" height=\"40\">$srv->{$key}{mac_addr}</th><th width=\"250\" height=\"40\">$srv->{$key}{mac_age}</th><th width=\"250\" height=\"40\">$srv->{$key}{port_name}</th><th width=\"250\" height=\"40\"><a href=\"https://netsec-test.wdf.sap.corp/corp-tools/sismapi/sism_request_emcp_interface_working.cgi?id=$hashobj{$key}\">$hashobj{$key}</a></th></tr>\n";
                        }
                        else {
                                print "<tr bgcolor=\"#D2D2D2\"><td align=\"center\" width=\"250\" height=\"20\">$key</td><td align=\"center\" width=\"250\" height=\"20\">$item</td><td align=\"center\" width=\"250\" height=\"20\">$ip_addr</td></tr>\n";
                        }
                        delete $HOSTS{$key};
                }
        }
}
if (defined @hosts){
foreach my $key (keys %HOSTS){
          next if ($key =~ /^nw/);
          my ($packip,$ip);
          ($packip = gethostbyname($key)) && ($ip = inet_ntoa($packip));
          print "<tr bgcolor=\"#D2D2D2\"><td align=\"center\" width=\"250\" height=\"20\">$key</td><td align=\"center\" width=\"250\" height=\"20\"></td><td align=\"center\" width=\"250\" height=\"20\">$ip</td></tr>\n";
        }
}

print "</table>\n";
print "</body>\n";
print "</html>\n";

exit 0;

sub print_report
{
        my $host = shift;

        my $packip = 0;
        my $ip_addr = 0;
        my $xgtype = "d";

        my $rtrif = Rtrif->new();

        ($packip = gethostbyname($host)) && ($ip_addr = inet_ntoa($packip));

        my $ret_gw = $rtrif->getRtrIf($ip_addr);
        my $ret_sw = $rtrif->getSwitchIf($ip_addr);

        print "<p><b>".$host." -- ".$ret_sw->{switchIP}."\t[ $ret_sw->{portIdx} ] $ret_sw->{switchPortName} $ret_sw->{switchSysLoc}</b><br>\n";

        my $portname_mstg = $ret_sw->{switchPortName};
        $portname_mstg =~ s/\//_/g;
        $ret_gw->{routerInterface} =~ s/\//_/g;


        if ($ret_sw->{switchTopo} &&  $ret_sw->{switchName} && $portname_mstg) {
                print "<p><img src=\"https://mstg.wdf.sap.corp/routers2.cgi?rtr=$ret_sw->{switchTopo}%2F$ret_sw->{switchName}.cfg&xgtype=$xgtype&page=image&if=".lc($portname_mstg)."_octets\"></img></p>";
                print "<p><img src=\"https://mstg.wdf.sap.corp/routers2.cgi?rtr=$ret_sw->{switchTopo}%2F$ret_sw->{switchName}.cfg&xgtype=$xgtype&page=image&if=".lc($portname_mstg)."_errors\"></img></p>";
        }

        if ($ret_gw->{routerTopo} && $ret_gw->{routerName} && $ret_gw->{routerInterface}) {
                print "<p><img src=\"https://mstg.wdf.sap.corp/routers2.cgi?rtr=$ret_gw->{routerTopo}%2F$ret_gw->{routerName}.cfg&xgtype=$xgtype&page=image&if=".lc($ret_gw->{routerInterface})."_octets\"></img></p>"
        }

        print "</p>\n";

        return
}
