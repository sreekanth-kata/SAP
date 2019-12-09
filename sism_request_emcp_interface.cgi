#!/usr/bin/perl -w
use strict;
use SOAP::Lite;
use Getopt::Long;
use Data::Dumper;
use feature 'say';
use IO::File ;

use open qw(:encoding(UTF-8) :std);            #Make UTF-8 default encoding   
use MIME::Base64 qw(decode_base64);
use IO::Uncompress::Gunzip qw(gunzip $GunzipError);
use XML::Twig;
use XML::XPath;
use XML::Simple;


BEGIN {
    sub SOAP::Transport::HTTP::Client::get_basic_credentials {
        return 'WS_GNS' => 'Welcome@1';
    }
}


use constant VERSION => 0.1;

my $soapObject;
my $soapObjectP;

my $proxyURL = 'https://pi-internal.wdf.sap.corp:443/XISOAPAdapter/MessageServlet?senderParty=&senderService=generic_client&receiverParty=&receiverService=&interface=SI_QueryServicesOut&interfaceNamespace=http://sap-it.com/sism/services';# The endpoint out of WSDL 
my $proxyURLP ='https://pi-internal.wdf.sap.corp:443/XISOAPAdapter/MessageServlet?senderParty=&senderService=virtualserver_frwk_client&receiverParty=&receiverService=&interface=SI_OB_Virtual_Server_sync&interfaceNamespace=http://sap-it.com/vsfrwk/generic';

my $ns1 = 'http://sap-it.com/sism/services';              #namespace of the service - URI-like identifier of the service
my $ns2 = 'http://sap-it.com/am_integration/sism';        #physical server - Responsibles

#------------------------------------------------------------------------------#
# function SOAPrequest --------------------------------------------------------#
#------------------------------------------------------------------------------#
sub SOAPrequest {
   my @params = (
                 SOAP::Data->name('ObjectType' => 'ZSISM_CL_PHYSICAL'),
                 SOAP::Data->name('Searchstring' => 'pwdf6336.wdf.sap.corp')
                );

   my $result  = $soapObject->call('MT_SismQuickSearch_Req' => @params);

   my $data = $result->{_content};
   my $hash = $data->[4];
   my $enc_val = $$hash{Body}->{MT_SismQuickSearch_Resp}->{item}->{Data}->{GzippedXmlLineItems};
   my $b64decoded = decode_base64($enc_val);

   my $buffer;
   gunzip \$b64decoded => \$buffer
        or die "unzip failed: $GunzipError.\n";

   my $parser = XML::XPath->new($buffer);
   my $object_key = $parser->findnodes('//OBJECT_KEY');
   print "Found OBJECT_KEY = $object_key \n";
   #if ($result->fault){
   #    print $result->faultdetail;
   #}
}


sub PHYSICALrequest{

   #Html for output on webpage
   print "content-type:text/html\n\n";
   print '<! doctype html public "- // w3c // dtd html 4.01 // en">', "\n";

   print "<html>\n";
   print "<head><title>testing output</title></head>\n";

   print "<body>\n";
   print "<frameset framespacing='0' border='false' frameborder='0' rows='100,*'>";

   print "<table border='0' cellpadding='0' cellspacing='2' width='100%'>";
   print "<tr><td align='center' height='60' bgcolor='#44697d' width='80%'>
          <font color='#ECF0F2' size='+1'>SISM Responsibles</font></td></tr>";
   print "</table>\n";

   use CGI::Carp qw(fatalsToBrowser);
   use CGI ':standard';
   my $cgi = new CGI;
      my $click_object = $cgi->param('id');
   #print $object;
   #print $cgi->header('text / plain');
   print "<p style='text-align: center;'>Object Key given as input: $click_object\n\n</p>";

   my @paramsp = (
                 SOAP::Data->name('items' => \SOAP::Data->value(
                 SOAP::Data->name('OBJECT_KEY' => $click_object)))
                 #SOAP::Data->name('OBJECT_KEY' => '00205495930014986818')))
   );


   my $resultp  = $soapObjectP->call('MT_Get_Physical_Server_Req' => @paramsp);
   my $xml_response = $resultp->{_context}{_transport}{_proxy}{_http_response}{_content};
   my $xp = XML::XPath->new($xml_response);

   my $SISM_ID = $xp->find('//SISM_ID');
   my $ADAM_ID = $xp->find('//ADAM_ID');
   my $EQUI_NO  = $xp->find('//EQUI_NO');
   my $SAP_STATUS  = $xp->find('//SAP_STATUS');
   my $SAP_DETAIL_STATUS = $xp->find('//SAP_DETAIL_STATUS');
   my $PURCHASE_STATUS = $xp->find('//PURCHASE_STATUS');
   my $PROCESSOR_TYPE = $xp->find('//PROCESSOR_TYPE');
   my $CPU_CLOCK_RATE = $xp->find('//CPU_CLOCK_RATE');
   my $CPU_CLOCK_RATE_UNIT = $xp->find('//CPU_CLOCK_RATE_UNIT');
   my $CPU_NUMBER = $xp->find('//CPU_NUMBER');
   my $CPU_CORE_NUMBER = $xp->find('//CPU_CORE_NUMBER');
   my $CPU_THREADS_PER_CORE = $xp->find('//CPU_THREADS_PER_CORE');
   my $MEMORY = $xp->find('//MEMORY');
   my $MEMORY_UNIT = $xp->find('//MEMORY_UNIT');

   my $PAGE_FILE_SIZE_UNIT = $xp->find('//PAGE_FILE_SIZE_UNIT');
   my $OPSYS = $xp->find('//OPSYS');
   my $SERIAL_NO = $xp->find('//SERIAL_NO');
   my $CONTRACT_TYPE = $xp->find('//CONTRACT_TYPE');
   my $HW_MAINT_COMPANY = $xp->find('//HW_MAINT_COMPANY');
   my $HW_MAINT_STARTDATE = $xp->find('//HW_MAINT_STARTDATE');
   my $HW_MAINT_ENDDATE = $xp->find('//HW_MAINT_ENDDATE');
   my $HW_MAINT_SLA = $xp->find('//HW_MAINT_SLA');
   my $MAINT_COST_HW = $xp->find('//MAINT_COST_HW');
   my $LOCATION = $xp->find('//LOCATION');
   my $DATACENTER = $xp->find('//DATACENTER');
   my $COUNTRY = $xp->find('//COUNTRY');
   my $ROOM = $xp->find('//ROOM');
   my $ROW = $xp->find('//ROW');
   my $RACK = $xp->find('//RACK');
   my $SHELF = $xp->find('//SHELF');
   my $ELECTRICAL_INPUT = $xp->find('//ELECTRICAL_INPUT');
   my $ELECTRICAL_INPUT_UNIT = $xp->find('//ELECTRICAL_INPUT_UNIT');
   my $IDLE_MODE = $xp->find('//IDLE_MODE');
   my $IDLE_MODE_UNIT = $xp->find('//IDLE_MODE_UNIT');
   my $FULL_LOAD = $xp->find('//FULL_LOAD');
   my $FULL_LOAD_UNIT = $xp->find('//FULL_LOAD_UNIT');
   my $HEIGHT = $xp->find('//HEIGHT');
   my $HEIGHT_UNIT = $xp->find('//HEIGHT_UNIT');
   my $WEIGHT = $xp->find('//WEIGHT');
   my $WEIGHT_UNIT = $xp->find('//WEIGHT_UNIT');
   my $POWER_SUPPLY = $xp->find('//POWER_SUPPLY');
   my $KOSTL_DEPR = $xp->find('//KOSTL_DEPR');
   my $AUFNR_DEPR = $xp->find('//AUFNR_DEPR');
   my $MANUFACTURER = $xp->find('//MANUFACTURER');
   my $MODEL = $xp->find('//MODEL');
   my $PROD_SPEC = $xp->find('//PROD_SPEC');
   my $SERVICE_UNIT = $xp->find('//SERVICE_UNIT');
   my $SERVICE_GROUP = $xp->find('//SERVICE_GROUP');
   my $SERVICE_TEAM = $xp->find('//SERVICE_TEAM');
   my $EQUIPMENT_TYPE = $xp->find('//EQUIPMENT_TYPE');
   my $SRC_USER = $xp->find('//SRC_USER');
   my $CUS_ID = $xp->find('//CUS_ID');
   my $SYSDESCR = $xp->find('//SYSDESCR');
   my $SUPPORT_TIME = $xp->find('//SUPPORT_TIME');
   my $SERVICE_TIME = $xp->find('//SERVICE_TIME');
   my $LICENSE_MODE = $xp->find('//LICENSE_MODE');

   my $TICKET = $xp->find('//TICKET_TYPE');
   my $RESPONSIBLE_PERSONS = $xp->find('//RESPONSIBLE_PERSONS');
   my $SUPPORT_INFO = $xp->find('//SUPPORT_INFO');
   my $Admin_Data = $xp->find('//Admin_Data');
   my $NETWORK_CONFIGURATION = $xp->find('//NETWORK_CONFIGURATION');
   my $SUPPLEMENT = $xp->find('//SUPPLEMENT');
      #my $xp = XML::XPath->new($xml_response);
   my $xml = XML::Simple->new();
   my $nodeset = $xp->findnodes('//RESPONSIBLE_PERSONS');

   my $ctr = 0;
   print "<table align='center' cellpadding=10 border=1>\n";
   foreach my $node ($nodeset->get_nodelist){
      my $data = $xml->XMLin($node->toString);
      foreach my $key(keys %$data){
         my $value = $$data{$key};
         $ctr += 1;
         if ($ctr%2 != 0){
            print "<tr><td>$key</td><td bgcolor='#A0A0A0'>$value</td>";
         }
         else{
            print "<td>$key</td><td>$value</td></tr>\n\n"
            }
       }
   }
   print "</table>\n";
   print "</body>\n</html>\n";
}

# Create the SOAP object ------------------------------------------------------#
$soapObject = undef;
if ( defined( &SOAP::Lite::ns )) {
    $soapObject = SOAP::Lite
        -> proxy( $proxyURL, ssl_opts => [ ssl_verify_mode => 0 ], ssl_opts => [ verify_hostname => 0 ] )
        -> ns( $ns1 );
}
else {
    $soapObject = SOAP::Lite
        -> proxy( $proxyURL, ssl_opts => [ ssl_verify_mode => 0 ], ssl_opts => [ verify_hostname => 0 ] )
        -> uri( $ns1 );
}

# SOAP object created? --------------------------------------------------------#
if ( ! defined( $soapObject ) ) {
    die "Unable to create SOAP object. Aborting.\n\n";
}

#######################
# Create the SOAP object for physical server ------------------------------------------------------#
$soapObjectP = undef;
if ( defined( &SOAP::Lite::ns )) {
    $soapObjectP = SOAP::Lite
        -> proxy( $proxyURLP, ssl_opts => [ ssl_verify_mode => 0 ], ssl_opts => [ verify_hostname => 0 ] )
        -> ns( $ns2 );
}
else {
    $soapObjectP = SOAP::Lite
        -> proxy( $proxyURLP, ssl_opts => [ ssl_verify_mode => 0 ], ssl_opts => [ verify_hostname => 0 ] )
        -> uri( $ns2 );
}

# SOAP object created? --------------------------------------------------------#
if ( ! defined( $soapObjectP ) ) {
    die "Unable to create SOAP object Physical. Aborting.\n\n";
}

#SOAPrequest();
PHYSICALrequest();



