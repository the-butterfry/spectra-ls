. config.inc

SUB='rendertransport1'
SRV='urn:schemas-upnp-org:service:AVTransport:1'
ACT='GetMediaInfo'
MSG='<InstanceID>0</InstanceID>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:GetMediaInfoResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
# <NrTracks>2</NrTracks>
# <MediaDuration>00:03:46</MediaDuration>
# <CurrentURI>http://192.168.0.132:11234/1545978271818987060</CurrentURI>
# <CurrentURIMetaData><?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.wiimu.com/song/" xmlns:custom="www.wiimu.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item><song:id>1545978271818987060</song:id><song:albumid></song:albumid><song:singerid></song:singerid><dc:title>See You Again</dc:title><upnp:artist>Wiz Khalifa</upnp:artist><upnp:album>Now That's What I Call Music! - 最心选</upnp:album><res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="0">http://192.168.0.132:11234/1545978271818987060</res><upnp:albumArtURI>http://192.168.0.132:11234/1545978271818987060_artwork</upnp:albumArtURI></item></DIDL-Lite></CurrentURIMetaData>
# <NextURI></NextURI>
# <NextURIMetaData></NextURIMetaData>
# <TrackSource>iPhone 2000_RemoteLocal</TrackSource>
# <PlayMedium>SONGLIST-NETWORK</PlayMedium>
# <RecordMedium>NOT_IMPLEMENTED</RecordMedium>
# <WriteStatus>NOT_IMPLEMENTED</WriteStatus>
# </u:GetMediaInfoResponse>
# </s:Body> </s:Envelope>

