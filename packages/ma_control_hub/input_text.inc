## Description: MA control hub input_text helper defaults and target mappings.
## Version: 2026.04.17.1
## Last updated: 2026-04-17

ma_ambiguous_entities:
  name: MA Ambiguous Entities (force prompt)
  initial: "media_player.the_oracle_2"
  max: 255
  mode: text
ma_server_url:
  name: MA Server URL
  initial: !secret ma_server_url
  max: 255
  mode: text
ma_meta_override_entity:
  name: MA Meta Override Entity ID
  initial: ""
  max: 255
  mode: text
ma_last_valid_target:
  name: MA Last Valid Target
  initial: ""
  max: 255
  mode: text
spectra_ls_target_primary_entity:
  name: Spectra LS Target (Primary) Entity ID
  initial: "media_player.spectra_ls_2"
  max: 255
  mode: text
spectra_ls_target_primary_meta_entity:
  name: Spectra LS Target (Primary) Meta Entity ID
  initial: "media_player.spectra_ls"
  max: 255
  mode: text
spectra_ls_target_primary_tcp_host:
  name: Spectra LS Target (Primary) TCP Host
  initial: !secret spectra_ls_primary_tcp_host
  max: 255
  mode: text
spectra_ls_target_room_entity:
  name: Spectra LS Target (Room) Entity ID
  initial: ""
  max: 255
  mode: text
spectra_ls_target_room_meta_entity:
  name: Spectra LS Target (Room) Meta Entity ID
  initial: ""
  max: 255
  mode: text
spectra_ls_target_room_tcp_host:
  name: Spectra LS Target (Room) TCP Host
  initial: !secret spectra_ls_room_tcp_host
  max: 255
  mode: text
