. config.inc

SUB='rendercontrol1'
SRV='urn:schemas-upnp-org:service:RenderingControl:1'
ACT='GetChannel'
MSG='<InstanceID>0</InstanceID><Channel>Master</Channel>'

URL='http://'$IP':59152/upnp/control/rendertransport1'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:GetChannelResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
# <CurrentChannel>0</CurrentChannel>
# </u:GetChannelResponse>
# </s:Body> </s:Envelope>
