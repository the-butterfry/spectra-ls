. config.inc

# 0:loop all
# 1:loop single
# 2:shuffle
# 3:?
# 4:?
# X:invalid

MODE=$1

if [ "$MODE" == "" ]; then
	MODE='0'
fi

SUB='PlayQueue1'
SRV='urn:schemas-wiimu-com:service:PlayQueue:1'
ACT='SetQueueLoopMode'
MSG='<LoopMode>'$MODE'</LoopMode>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"



