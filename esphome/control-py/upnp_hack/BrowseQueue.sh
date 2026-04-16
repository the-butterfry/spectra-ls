. config.inc

QUEUE_NAME=$1

if [ "$QUEUE_NAME" == "" ]; then
	QUEUE_NAME='TotalQueue'
fi

# USBDiskQueue

SUB='PlayQueue1'
SRV='urn:schemas-wiimu-com:service:PlayQueue:1'
ACT='BrowseQueue'
MSG='<QueueName>'$QUEUE_NAME'</QueueName><SkipQueue>0</SkipQueue>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:BrowseQueueResponse xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1">
# <QueueContext><?xml version="1.0"?>
# <PlayQueue>
# <TotalQueue>3</TotalQueue>
# <CurrentPlayList>
# <Name>MyFavouriteQueue__iPhone 2000_favorite</Name>
# </CurrentPlayList>
# <PlayListInfo>
# <List1>
# <Name>青春不老歌_#~169</Name>
# <ListInfo>
# <Source>QQFM</Source>
# <SearchUrl>http://api.fm.qq.com/v1/detail/get_album_show_list?album_id=rd003SNJNd1vwO3u&amp;appid=1105226088&amp;pagination_size=30&amp;sig=PRnADf45%2FkJMw4eDerqfxGB9pcU%3D&amp;pagination_cursor=0</SearchUrl>
# <PicUrl>http://imgcache.qq.com/fm/photo/album/rmid_album_360/3/u/003SNJNd1vwO3u.jpg?time=1520304888</PicUrl>
# <SrcParent>青春不老歌</SrcParent>
# <AutoGenerate>0</AutoGenerate>
# <StationLimit>0</StationLimit>
# <MarkSearch>0</MarkSearch>
# <Quality>0</Quality>
# <UpdateTime>58</UpdateTime>
# <LastPlayIndex>1</LastPlayIndex>
# <RealIndex>0</RealIndex>
# <TrackNumber>30</TrackNumber>
# <SwitchPageMode>0</SwitchPageMode>
# <PressType>0</PressType>
# <Volume>0</Volume>
# </ListInfo>
# </List1>
# <List2>
# <Name>爵士春秋 All That Jazz_#~350</Name>
# <ListInfo>
# <Source>QQFM</Source>
# <SearchUrl>http://api.fm.qq.com/v1/detail/get_album_show_list?album_id=rd003Ut1h20P0vvB&amp;appid=1105226088&amp;pagination_size=30&amp;sig=6%2FJrA6isGpQZvGYqyGZwnGR9OTg%3D&amp;pagination_cursor=0</SearchUrl>
# <PicUrl>http://imgcache.qq.com/fm/photo/album/rmid_album_360/v/B/003Ut1h20P0vvB.jpg?time=1539133198</PicUrl>
# <SrcParent>爵士春秋 All That Jazz</SrcParent>
# <AutoGenerate>0</AutoGenerate>
# <StationLimit>0</StationLimit>
# <MarkSearch>0</MarkSearch>
# <Quality>0</Quality>
# <UpdateTime>65</UpdateTime>
# <LastPlayIndex>13</LastPlayIndex>
# <RealIndex>0</RealIndex>
# <TrackNumber>30</TrackNumber>
# <SwitchPageMode>0</SwitchPageMode>
# <PressType>0</PressType>
# <Volume>0</Volume>
# </ListInfo>
# </List2>
# <List3>
# <Name>MyFavouriteQueue__iPhone 2000_favorite</Name>
# <ListInfo>
# <Source>iPhone 2000</Source>
# <Quality>0</Quality>
# <UpdateTime>1692</UpdateTime>
# <LastPlayIndex>1</LastPlayIndex>
# <RealIndex>0</RealIndex>
# <TrackNumber>6</TrackNumber>
# <TempQueue>1</TempQueue>
# </ListInfo>
# </List3>
# </PlayListInfo>
# </PlayQueue>
# </QueueContext>
# </u:BrowseQueueResponse>
# </s:Body> </s:Envelope>
