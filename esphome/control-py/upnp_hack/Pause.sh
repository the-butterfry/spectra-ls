. config.inc

SUB='rendertransport1'
SRV='urn:schemas-upnp-org:service:AVTransport:1'
ACT='Pause'
MSG='<InstanceID>0</InstanceID>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

#SUCCESS
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:PauseResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"></u:PauseResponse>
# </s:Body> </s:Envelope>

#FAIL
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
# <s:Body>
# <s:Fault>
# <faultcode>s:Client</faultcode>
# <faultstring>UPnPError</faultstring>
# <detail>
# <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
# <errorCode>701</errorCode>
# <errorDescription>Transition not allowed</errorDescription>
# </UPnPError>
# </detail>
# </s:Fault>
# </s:Body>
# </s:Envelope>

