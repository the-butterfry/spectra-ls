. config.inc

SUB='rendertransport1'
SRV='urn:schemas-upnp-org:service:AVTransport:1'
ACT='GetInfoEx'
MSG='<InstanceID>0</InstanceID>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:GetInfoExResponse xmlns:u="urn:schemas-upnp-org:service:AVTransport:1">
# <CurrentTransportState>PAUSED_PLAYBACK</CurrentTransportState>
# <CurrentTransportStatus>OK</CurrentTransportStatus>
# <CurrentSpeed>1</CurrentSpeed>
# <Track>1</Track>
# <TrackDuration>00:03:46</TrackDuration>
# <TrackMetaData><?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.wiimu.com/song/" xmlns:custom="www.wiimu.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item><song:id>1545978271818987060</song:id><song:albumid></song:albumid><song:singerid></song:singerid><dc:title>See You Again</dc:title><upnp:artist>Wiz Khalifa</upnp:artist><upnp:album>Now That's What I Call Music! - 最心选</upnp:album><res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="0">http://192.168.0.132:11234/1545978271818987060</res><upnp:albumArtURI>http://192.168.0.132:11234/1545978271818987060_artwork</upnp:albumArtURI></item></DIDL-Lite></TrackMetaData>
# <TrackURI>http://192.168.0.132:11234/1545978271818987060</TrackURI>
# <RelTime>00:00:07</RelTime>
# <AbsTime>NOT_IMPLEMENTED</AbsTime>
# <RelCount>2147483647</RelCount>
# <AbsCount>2147483647</AbsCount>
# <CurrentVolume>44</CurrentVolume>
# <CurrentChannel>0</CurrentChannel>
# <LoopMode>0</LoopMode>
# <SlaveList>{ "slaves": 1, "slave_list": [ { "name": "SoundSystem_05A4", "ssid": "SoundSystem_05A4", "mask": 0, "volume": 100, "mute": 0, "channel": 0, "battery": 0, "ip": "10.10.10.92", "version": "3.6.4715", "uuid": "uuid:FF31F012-E0F9-174F-40A0-0FF5FF31F012" } ] }</SlaveList>
# <PlayMedium>SONGLIST-NETWORK</PlayMedium>
# <TrackSource>iPhone 2000_RemoteLocal</TrackSource>
# <InternetAccess>1</InternetAccess>
# <VerUpdateFlag>0</VerUpdateFlag>
# <VerUpdateStatus>22</VerUpdateStatus>
# <BatteryFlag>0</BatteryFlag>
# <BatteryPercent>0</BatteryPercent>
# <AlarmFlag>0</AlarmFlag>
# <TimeStamp>2231447</TimeStamp>
# <SubNum>0</SubNum>
# <SpotifyActive>0</SpotifyActive>
# </u:GetInfoExResponse>
# </s:Body> </s:Envelope>
