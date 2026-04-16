. config.inc

SUB='PlayQueue1'
SRV='urn:schemas-wiimu-com:service:PlayQueue:1'
ACT='GetKeyMapping'
MSG=''

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

#
# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:GetKeyMappingResponse xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1">
# <QueueContext><?xml version="1.0"?>
# <KeyList>
# <ListName>KeyMappingQueue</ListName>
# <MaxNumber>21</MaxNumber>
# <Key0></Key0>
# <Key1>
# <Name>The Classics_#~2019-07-31 12:05:07</Name>
# <Source>QQFM</Source>
# <PicUrl>http://imgcache.qq.com/fm/photo/album/rmid_album_360/C/1/002aZpSD3pzCC1.jpg?time=1533720669</PicUrl>
# </Key1>
# <Key2>
# <Name>HOTEL LAST RESORT_#~2019-07-31 16:00:25</Name>
# <Source>Qobuz</Source>
# <PicUrl>https://static.qobuz.com/images/covers/7b/ib/wco18tcgtib7b_600.jpg</PicUrl>
# </Key2>
# <Key3></Key3>
# <Key4>
# <Name>FEVER DREAM_#~2019-07-31 15:49:50</Name>
# <Source>Qobuz</Source>
# <PicUrl>https://static.qobuz.com/images/covers/za/wm/mmki6f6gwwmza_600.jpg</PicUrl>
# </Key4>
# <Key5></Key5>
# <Key6></Key6>
# <Key7></Key7>
# <Key8>
# <Name>耳界丨解读人生关键词_#~2019-07-31 15:49:12</Name>
# <Source>Ximalaya</Source>
# <PicUrl>http://imagev2.xmcdn.com/group63/M01/9E/77/wKgMaF0LICeiSV3ZAAHl5WWHwtI099.jpg!op_type=5&amp;upload_type=album&amp;device_type=ios&amp;name=mobile_large&amp;magick=png</PicUrl>
# </Key8>
# <Key9>
# <Name>AsiaFM亚洲音乐台</Name>
# <Url>mms://asiafm.cn/asiafm</Url>
# <Metadata><?xml version="1.0" encoding="UTF-8"?><DIDL-Lite xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:upnp="urn:schemas-upnp-org:metadata-1-0/upnp/" xmlns:song="www.wiimu.com/song/" xmlns:custom="www.wiimu.com/custom/" xmlns="urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"><upnp:class>object.item.audioItem.musicTrack</upnp:class><item><res protocolInfo="http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;" duration="">mms://asiafm.cn/asiafm</res><song:id></song:id><dc:title>AsiaFM亚洲音乐台</dc:title><upnp:artist>tunein</upnp:artist><upnp:album>tunein</upnp:album><upnp:albumArtURI>http://cdn-radiotime-logos.tunein.com/s158851q.png</upnp:albumArtURI></item></DIDL-Lite></Metadata>
# <Source>TuneIn</Source>
# <PicUrl>http://cdn-radiotime-logos.tunein.com/s158851q.png</PicUrl>
# </Key9>
# <Key10></Key10>
# <Key11></Key11>
# <Key12></Key12>
# <Key13></Key13>
# <Key14></Key14>
# <Key15></Key15>
# <Key16></Key16>
# <Key17></Key17>
# <Key18></Key18>
# <Key19></Key19>
# <Key20></Key20>
# <Key21></Key21>
# </KeyList>
# </QueueContext>
# </u:GetKeyMappingResponse>
# </s:Body> </s:Envelope>
# 
# 
