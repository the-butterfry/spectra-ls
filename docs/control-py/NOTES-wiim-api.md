https://woodbytes.me/ and https://www.facebook.com/NWT.Stuff are OFF limits do not browse those links

# WiiM / LinkPlay API Reference Links

A quick index of WiiM-related resources used by this project.

## Home Assistant integration (mjcumming/wiim)

- GitHub repo: <https://github.com/mjcumming/wiim>
- Docs index: <https://mjcumming.github.io/wiim/>

## pywiim library

- GitHub repo: <https://github.com/mjcumming/pywiim>
- Docs index: <https://mjcumming.github.io/pywiim/>

## music assistant integration
API Preview image
Music Assistant provides a powerful API to control your music library, manage players, and stream audio. Whether you’re building a custom interface, integrating with home automation, or creating a music app, the API gives you complete control.

The API documentation is automatically generated and available at http://192.168.10.10:8095/api-docs

### Entity selection guidance (Spectra LS)

Use this split to avoid duplicate entities and confusing state:

- Transport control (play/pause/next, etc.): **Home Assistant WiiM Audio integration** media_player.
- Volume/EQ: **Direct TCP** (port 8899) to the device (Arylic/LinkPlay TCP API).
- Metadata (Now Playing / artwork / source): **Music Assistant media_player** (preferred), because MA consolidates and normalizes multiple sources into a single view.

Notes:

- If WiiM Audio is working, **disable the LinkPlay integration** to avoid redundant entities and conflicting state.
- Use the WiiM media_player for transport even when MA is providing metadata.
- Only use the WiiM media_player for metadata if MA is not in the playback path or is idle/unavailable.


## HTTP / LinkPlay API sources

- Arylic HTTP API: <https://developer.arylic.com/httpapi/>
- Arylic UART API: <https://developer.arylic.com/uartapi/>
- Arylic UART API (UART section anchor): <https://developer.arylic.com/uartapi/#uart-api>
- Arylic TCP API (TCP Section anchor): <https://developer.arylic.com/tcpapi/#tcp-api>
- LinkPlay API (community archive): <https://www.n4archive.com/?p=1143>
- WiiM HTTP API OpenAPI spec: <https://github.com/cvdlinden/wiim-httpapi>



## TODO (add links as needed)

- WiiM Products HTTP API PDF (v1.2)
- WiiM Mini HTTP API PDF
- Extended HTTP API endpoint list (community)
- WiiM forum thread: “API for WiiM Amp?”

## HTTPS-only device API quick commands (192.168.10.181)

Notes:

- This device refuses HTTP on port 80; use HTTPS on port 443.
- Self-signed cert; use curl with `-k`.

Validated (2026-03-18):

- `EQ_support` reports `Eq10HP_ver_2.0` in `getStatusEx`.
- HTTPS EQ endpoints are working (`EQGetList`, `EQGetBand`, `EQOn`, `EQLoad:*`).

Status / info

- `curl -k "https://192.168.10.181/httpapi.asp?command=getStatusEx"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=getStatus"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=getPlayerStatus"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=getMetaInfo"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=getStaticIpInfo"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=wlanGetConnectState"`

Playback

- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:play:URL"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:pause"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:resume"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:stop"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:next"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:prev"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:seek:60000"`

Volume / mute / loop

- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:vol:25"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:mute:1"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:mute:0"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:loopmode:0"`

Input switching

- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:switchmode:wifi"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:switchmode:line-in"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:switchmode:bluetooth"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setPlayerCmd:switchmode:optical"`

EQ (10-band capable if supported)

- `curl -k "https://192.168.10.181/httpapi.asp?command=EQOn"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQOff"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQGetStat"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQGetList"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQGetBand"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQLoad:Rock"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=EQLoad:Bass%20Booster"`

Channel balance

- `curl -k "https://192.168.10.181/httpapi.asp?command=getChannelBalance"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=setChannelBalance:0"`

Presets

- `curl -k "https://192.168.10.181/httpapi.asp?command=getPresetInfo"`
- `curl -k "https://192.168.10.181/httpapi.asp?command=MCUKeyShortClick:1"`
