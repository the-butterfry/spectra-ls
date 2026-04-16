. config.inc

SUB='rendercontrol1'
SRV='urn:schemas-upnp-org:service:RenderingControl:1'
ACT='GetControlDeviceInfo'
MSG='<InstanceID>0</InstanceID>'

URL='http://'$IP':59152/upnp/control/'$SUB
ENVS='<s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>'
ENVE='</s:Body></s:Envelope>'
DAT=$ENVS'<u:'$ACT' xmlns:u="'$SRV'">'$MSG'</u:'$ACT'>'$ENVE
HSA='SOAPACTION: "'$SRV'#'$ACT'"'

curl -s -X POST "$URL" -H "$HSA" -H 'Content-Type: text/xml;charset="utf-8"' -d "$DAT" | sed -e "s/&amp;/\&/g" | sed -e "s/&quot;/\"/g" | sed -e "s/&gt;/\>/g"| sed -e "s/&lt;/\</g" | sed -e "s/&apos;/\'/g"

# <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>
# <u:GetControlDeviceInfoResponse xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1">
# <MultiType>1</MultiType>
# <Router>49502D434F4D5F41505F322E3447</Router>
# <Ssid>SoundSystem_7478</Ssid>
# <SlaveMask>0</SlaveMask>
# <CurrentVolume>44</CurrentVolume>
# <CurrentMute>0</CurrentMute>
# <CurrentChannel>0</CurrentChannel>
# <SlaveList>{ "slaves": 1, "slave_list": [ { "name": "SoundSystem_05A4", "ssid": "SoundSystem_05A4", "mask": 0, "volume": 100, "mute": 0, "channel": 0, "battery": 0, "ip": "10.10.10.92", "version": "3.6.4715", "uuid": "uuid:FF31F012-E0F9-174F-40A0-0FF5FF31F012" } ] }</SlaveList>
# <Status>{ "language": "en_us", "ssid": "SoundSystem_7478", "hideSSID": "1", "SSIDStrategy": "2", "firmware": "4.2.7211", "build": "release", "project": "RP0003_D4", "priv_prj": "RP0003_D4", "Release": "20190711", "branch": "stable\/wiimu-4.2", "group": "0", "expired": "0", "internet": "1", "uuid": "FF31F09E6E1840A8C50876D8", "MAC": "00:22:6C:EA:74:78", "STA_MAC": "00:22:6C:EA:74:7A", "CountryCode": "CN", "CountryRegion": "1", "date": "2019:07:30", "time": "09:51:56", "tz": "8.000000", "dst_enable": "1", "netstat": "2", "essid": "49502D434F4D5F41505F322E3447", "apcli0": "192.168.0.140", "eth2": "0.0.0.0", "hardware": "A31", "VersionUpdate": "0", "NewVer": "0", "mcu_ver": "20", "mcu_ver_new": "0", "dsp_ver_new": "0", "ra0": "10.10.10.254", "temp_uuid": "F8CBBAE3E040D545", "cap1": "0x305200", "capability": "0x38490a00", "languages": "0x6", "dsp_ver": "0", "streams_all": "0x7ffffbfe", "streams": "0x7ffffbfe", "region": "unknown", "external": "0x0", "preset_key": "10", "plm_support": "0xe", "spotify_active": "0", "lbc_support": "0", "WifiChannel": "5", "RSSI": "-48", "battery": "0", "battery_percent": "0", "securemode": "0", "ali_pid": "RAKOIT_MA1", "ali_uuid": "", "upnp_version": "1005", "upnp_uuid": "uuid:FF31F09E-6E18-40A8-C508-76D8FF31F09E", "uart_pass_port": "8899", "communication_port": "8819", "web_firmware_update_hide": "0", "web_login_result": "-1", "ignore_talkstart": "0", "silenceOTATime": "", "ignore_silenceOTATime": "1", "iheartradio_new": "1", "security": "https\/2.0", "security_version": "2.0", "privacy_mode": "0", "user1": "307:524", "user2": "1896:2097", "DeviceName": "SoundSystem_7478", "GroupName": "SoundSystem_7478" }</Status>
# </u:GetControlDeviceInfoResponse>
# </s:Body> </s:Envelope>
