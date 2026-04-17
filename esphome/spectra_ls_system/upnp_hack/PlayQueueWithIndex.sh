. config.inc

QUEUE_NAME=$1
QUEUE_INDEX=$2
if [ "$QUEUE_NAME" == "" ]; then
	echo 'need to specify queue name'
	exit 0
fi
if [ "$QUEUE_INDEX" == "" ]; then
	QUEUE_INDEX=1
fi

SUB='PlayQueue1'
SRV='urn:schemas-wiimu-com:service:PlayQueue:1'
ACT='PlayQueueWithIndex'
MSG='<QueueName>'$QUEUE_NAME'</QueueName><Index>'$QUEUE_INDEX'</Index>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

### SUCCESS
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:PlayQueueWithIndexResponse xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"></u:PlayQueueWithIndexResponse>
# </s:Body> </s:Envelope>

### FAIL
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
# <s:Body>
# <s:Fault>
# <faultcode>s:Client</faultcode>
# <faultstring>UPnPError</faultstring>
# <detail>
# <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
# <errorCode>501</errorCode>
# <errorDescription>Action Failed</errorDescription>
# </UPnPError>
# </detail>
# </s:Fault>
# </s:Body>
# </s:Envelope>
