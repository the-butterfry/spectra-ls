# Description: Template entities for ma_control_hub runtime routing, metadata, and now-playing state surfaces.
# Version: 2026.04.17.1
# Last updated: 2026-04-17

- sensor:
    - name: Spectra LS Rooms JSON
      state: >-
        {% set rooms = state_attr('sensor.spectra_ls_rooms_raw','rooms') or [] %}
        {{ rooms | length }}
      attributes:
        rooms_json: >-
          {% set rooms = state_attr('sensor.spectra_ls_rooms_raw','rooms') or [] %}
          {{ rooms | tojson }}
    - name: MA API URL
      state: >-
        {% set base = states('input_text.ma_server_url') %}
        {% if base in ['unknown','unavailable','', none] %}
          {{ 'http://127.0.0.1:1/api' }}
        {% else %}
          {% set clean = base | regex_replace('/api/?$','') | regex_replace('/$','') %}
          {{ clean ~ '/api' }}
        {% endif %}
    - name: MA Active Target
      state: "{{ states('input_select.ma_active_target') }}"
    - name: MA Meta Candidates
      state: >-
        {% set ns = namespace(entities=[], names=[], scores=[], best_score=0, best='') %}
        {% set raw_users = states('input_text.plex_allowed_users') | lower %}
        {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
        {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
        {% set raw_players = states('input_text.plex_allowed_players') | lower %}
        {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
        {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
        {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
        {% for e in states.media_player %}
          {% set st = (e.state | lower) if e is not none else '' %}
          {% set active = st in ['playing','paused'] %}
          {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
          {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
          {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
          {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
          {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
          {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
          {% set ent_l = (e.entity_id | lower) %}
          {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
          {% set app_l = (app_name | lower) %}
          {% set source_l = (source | lower) %}
          {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
          {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
          {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
          {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
          {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
          {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
          {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
          {% set title_l = title | lower %}
          {% set content_l = content_id | lower %}
          {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                             (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
          {% set title_ok = title not in ['','None', none] and not url_like %}
          {% set score = 0 %}
          {% if title_ok %}{% set score = score + 3 %}{% endif %}
          {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
          {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
          {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
          {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
          {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
          {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
          {% if score > 0 and active and plex_ok %}
            {% set ns.entities = ns.entities + [e.entity_id] %}
            {% set ns.names = ns.names + [(e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id)] %}
            {% set ns.scores = ns.scores + [score] %}
          {% endif %}
          {% if score > ns.best_score and active and plex_ok %}
            {% set ns.best_score = score %}
            {% set ns.best = e.entity_id %}
          {% endif %}
        {% endfor %}
        {{ ns.entities | length }}
      attributes:
        entities: >-
          {% set ns = namespace(entities=[]) %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > 0 and active and plex_ok %}
              {% set ns.entities = ns.entities + [e.entity_id] %}
            {% endif %}
          {% endfor %}
          {{ ns.entities }}
        names: >-
          {% set ns = namespace(names=[]) %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ma_ids = [] %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if pid %}
              {% set ma_ids = ma_ids + [pid] %}
              {% set ma_ids = ma_ids + ['media_player.' ~ pid] %}
            {% endif %}
            {% if ent %}
              {% set ma_ids = ma_ids + [ent] %}
            {% endif %}
          {% endfor %}
          {% set ma_ids_l = ma_ids | map('lower') | list %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > 0 and active and plex_ok %}
              {% set ns.names = ns.names + [(e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id)] %}
            {% endif %}
          {% endfor %}
          {{ ns.names }}
        names_labeled: >-
          {% set ns = namespace(names=[]) %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ma_ids = [] %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if pid %}
              {% set ma_ids = ma_ids + [pid] %}
              {% set ma_ids = ma_ids + ['media_player.' ~ pid] %}
            {% endif %}
            {% if ent %}
              {% set ma_ids = ma_ids + [ent] %}
            {% endif %}
          {% endfor %}
          {% set ma_ids_l = ma_ids | map('lower') | list %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > 0 and active and plex_ok %}
              {% set base_name = (e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) %}
              {% set prefix = 'MA: ' if ent_l in ma_ids_l else 'HA: ' %}
              {% set ns.names = ns.names + [prefix ~ base_name] %}
            {% endif %}
          {% endfor %}
          {{ ns.names }}
        scores: >-
          {% set ns = namespace(scores=[]) %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > 0 and active and plex_ok %}
              {% set ns.scores = ns.scores + [score] %}
            {% endif %}
          {% endfor %}
          {{ ns.scores }}
        best_entity: >-
          {% set ns = namespace(best='', best_score=0) %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > ns.best_score and active and plex_ok %}
              {% set ns.best_score = score %}
              {% set ns.best = e.entity_id %}
            {% endif %}
          {% endfor %}
          {{ ns.best }}
        best_score: >-
          {% set ns = namespace(best_score=0) %}
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set allowed_users = raw_users.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set allowed_players = raw_players.split(',') | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set active = st in ['playing','paused'] %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_id = (e.attributes.app_id if e.attributes is defined and e.attributes.app_id is defined else '') %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set score = 0 %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
            {% if app_id or app_name %}{% set score = score + 1 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > ns.best_score and active and plex_ok %}
              {% set ns.best_score = score %}
            {% endif %}
          {% endfor %}
          {{ ns.best_score }}
    - name: MA Meta Resolver
      state: >-
        {% set raw_users = states('input_text.plex_allowed_users') | lower %}
        {% set raw_users_clean = '' if raw_users in ['unknown','unavailable','none'] else raw_users %}
        {% set allowed_users = (raw_users_clean.split(',') if raw_users_clean else []) | map('trim') | reject('equalto','') | list %}
        {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
        {% set raw_players = states('input_text.plex_allowed_players') | lower %}
        {% set raw_players_clean = '' if raw_players in ['unknown','unavailable','none'] else raw_players %}
        {% set allowed_players = (raw_players_clean.split(',') if raw_players_clean else []) | map('trim') | reject('equalto','') | list %}
        {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
        {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
        {% set pref = states('sensor.ma_active_meta_entity') %}
        {% set target = states('input_select.ma_active_target') %}
        {% set by_host = states('sensor.ma_active_target_by_host') %}
        {% set stale_s = states('input_number.ma_meta_stale_s') | float(45) %}
        {% set ns = namespace(list=[], count=0, best='', best_score=0) %}
        {% for e in states.media_player %}
          {% set st = (e.state | lower) if e is not none else '' %}
          {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
          {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
          {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
          {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
          {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
          {% set play_state = (e.attributes.play_state if e.attributes is defined and e.attributes.play_state is defined else '') | lower %}
          {% set is_playing = (e.attributes.is_playing if e.attributes is defined and e.attributes.is_playing is defined else none) %}
          {% set is_paused = (e.attributes.is_paused if e.attributes is defined and e.attributes.is_paused is defined else none) %}
          {% set ent_l = (e.entity_id | lower) %}
          {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
          {% set app_l = (app_name | lower) %}
          {% set source_l = (source | lower) %}
          {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
          {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
          {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
          {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
          {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
          {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
          {% set pos_updated = (e.attributes.media_position_updated_at if e.attributes is defined and e.attributes.media_position_updated_at is defined else none) %}
          {% set pos_ts = as_timestamp(pos_updated) if pos_updated is not none else 0 %}
          {% set pos_age = (as_timestamp(now()) - pos_ts) if pos_ts > 0 else 9999 %}
          {% set recent = pos_age < stale_s %}
          {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
          {% set title_l = title | lower %}
          {% set content_l = content_id | lower %}
          {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                             (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
          {% set title_ok = title not in ['','None', none] and not url_like %}
          {% set active = st in ['playing','paused'] or play_state in ['playing','paused'] or (is_playing is true) or (is_paused is true) %}
          {% set score = 0 %}
          {% if active %}{% set score = score + 4 %}{% endif %}
          {% if is_playing is true %}{% set score = score + 3 %}{% endif %}
          {% if is_paused is true %}{% set score = score + 1 %}{% endif %}
          {% if title_ok %}{% set score = score + 3 %}{% endif %}
          {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
          {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
          {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
          {% if recent %}{% set score = score + 2 %}{% endif %}
          {% if app_name or source %}{% set score = score + 1 %}{% endif %}
          {% if e.entity_id == pref %}{% set score = score + 2 %}{% endif %}
          {% if e.entity_id == target %}{% set score = score + 1 %}{% endif %}
          {% if e.entity_id == by_host %}{% set score = score + 2 %}{% endif %}
          {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
          {% if score > 0 and plex_ok %}
            {% set ns.list = ns.list + [{'entity': e.entity_id, 'score': score, 'active': active, 'recent': recent, 'has_meta': (title_ok or artist not in ['','None', none] or album not in ['','None', none]), 'state': st}] %}
            {% set ns.count = ns.count + 1 %}
          {% endif %}
          {% if score > ns.best_score and plex_ok %}
            {% set ns.best_score = score %}
            {% set ns.best = e.entity_id %}
          {% endif %}
        {% endfor %}
        {{ ns.count }}
      attributes:
        best_entity: >-
          {% set best = '' %}
          {% set score = 0 %}
          {% set raw = state_attr('sensor.ma_meta_resolver','candidates_json') | default('[]', true) %}
          {% set parsed = raw | from_json %}
          {% for c in parsed %}
            {% if c.score is defined and c.score > score %}
              {% set score = c.score %}
              {% set best = c.entity if c.entity is defined else '' %}
            {% endif %}
          {% endfor %}
          {{ best }}
        best_score: >-
          {% set score = 0 %}
          {% set raw = state_attr('sensor.ma_meta_resolver','candidates_json') | default('[]', true) %}
          {% set parsed = raw | from_json %}
          {% for c in parsed %}
            {% if c.score is defined and c.score > score %}
              {% set score = c.score %}
            {% endif %}
          {% endfor %}
          {{ score }}
        candidates_json: >-
          {% set raw_users = states('input_text.plex_allowed_users') | lower %}
          {% set raw_users_clean = '' if raw_users in ['unknown','unavailable','none'] else raw_users %}
          {% set allowed_users = (raw_users_clean.split(',') if raw_users_clean else []) | map('trim') | reject('equalto','') | list %}
          {% set allow_all_users = allowed_users | length == 0 or 'all' in allowed_users %}
          {% set raw_players = states('input_text.plex_allowed_players') | lower %}
          {% set raw_players_clean = '' if raw_players in ['unknown','unavailable','none'] else raw_players %}
          {% set allowed_players = (raw_players_clean.split(',') if raw_players_clean else []) | map('trim') | reject('equalto','') | list %}
          {% set allow_all_players = allowed_players | length == 0 or 'all' in allowed_players %}
          {% set plex_session_allowed = is_state('binary_sensor.plex_session_allowed','on') %}
          {% set pref = states('sensor.ma_active_meta_entity') %}
          {% set target = states('input_select.ma_active_target') %}
          {% set by_host = states('sensor.ma_active_target_by_host') %}
          {% set stale_s = states('input_number.ma_meta_stale_s') | float(45) %}
          {% set ns = namespace(list=[]) %}
          {% for e in states.media_player %}
            {% set st = (e.state | lower) if e is not none else '' %}
            {% set title = (e.attributes.media_title if e.attributes is defined and e.attributes.media_title is defined else '') %}
            {% set artist = (e.attributes.media_artist if e.attributes is defined and e.attributes.media_artist is defined else '') %}
            {% set album = (e.attributes.media_album_name if e.attributes is defined and e.attributes.media_album_name is defined else (e.attributes.media_album if e.attributes is defined and e.attributes.media_album is defined else '')) %}
            {% set app_name = (e.attributes.app_name if e.attributes is defined and e.attributes.app_name is defined else '') %}
            {% set source = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
            {% set play_state = (e.attributes.play_state if e.attributes is defined and e.attributes.play_state is defined else '') | lower %}
            {% set is_playing = (e.attributes.is_playing if e.attributes is defined and e.attributes.is_playing is defined else none) %}
            {% set is_paused = (e.attributes.is_paused if e.attributes is defined and e.attributes.is_paused is defined else none) %}
            {% set ent_l = (e.entity_id | lower) %}
            {% set name_l = ((e.attributes.friendly_name if e.attributes is defined and e.attributes.friendly_name is defined else e.entity_id) | lower) %}
            {% set app_l = (app_name | lower) %}
            {% set source_l = (source | lower) %}
            {% set is_plex = ('plex' in ent_l) or ('plex' in app_l) or ('plex' in source_l) %}
            {% set user_ok = allow_all_users or (allowed_users | select('in', name_l) | list | length > 0) or (allowed_users | select('in', app_l) | list | length > 0) or (allowed_users | select('in', source_l) | list | length > 0) or (allowed_users | select('in', ent_l) | list | length > 0) %}
            {% set player_ok = allow_all_players or (allowed_players | select('in', name_l) | list | length > 0) or (allowed_players | select('in', app_l) | list | length > 0) or (allowed_players | select('in', source_l) | list | length > 0) or (allowed_players | select('in', ent_l) | list | length > 0) %}
            {% set plex_ok = (not is_plex) or ((allow_all_users and allow_all_players) and plex_session_allowed) or (user_ok and player_ok) %}
            {% set pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
            {% set dur = (e.attributes.media_duration if e.attributes is defined and e.attributes.media_duration is defined else 0) | float(0) %}
            {% set pos_updated = (e.attributes.media_position_updated_at if e.attributes is defined and e.attributes.media_position_updated_at is defined else none) %}
            {% set pos_ts = as_timestamp(pos_updated) if pos_updated is not none else 0 %}
            {% set pos_age = (as_timestamp(now()) - pos_ts) if pos_ts > 0 else 9999 %}
            {% set recent = pos_age < stale_s %}
            {% set content_id = (e.attributes.media_content_id if e.attributes is defined and e.attributes.media_content_id is defined else '') %}
            {% set title_l = title | lower %}
            {% set content_l = content_id | lower %}
            {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                               (('://' in content_l) or content_l.startswith('www.') or content_l.endswith('.mp3') or content_l.endswith('.flac') or content_l.endswith('.wav') or content_l.endswith('.m4a') or content_l.endswith('.aac') or content_l.endswith('.ogg'))) %}
            {% set title_ok = title not in ['','None', none] and not url_like %}
            {% set active = st in ['playing','paused'] or play_state in ['playing','paused'] or (is_playing is true) or (is_paused is true) %}
            {% set score = 0 %}
            {% if active %}{% set score = score + 4 %}{% endif %}
            {% if is_playing is true %}{% set score = score + 3 %}{% endif %}
            {% if is_paused is true %}{% set score = score + 1 %}{% endif %}
            {% if title_ok %}{% set score = score + 3 %}{% endif %}
            {% if artist not in ['','None', none] %}{% set score = score + 2 %}{% endif %}
            {% if album not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
            {% if pos > 0 or dur > 0 %}{% set score = score + 2 %}{% endif %}
            {% if recent %}{% set score = score + 2 %}{% endif %}
            {% if app_name or source %}{% set score = score + 1 %}{% endif %}
            {% if e.entity_id == pref %}{% set score = score + 2 %}{% endif %}
            {% if e.entity_id == target %}{% set score = score + 1 %}{% endif %}
            {% if e.entity_id == by_host %}{% set score = score + 2 %}{% endif %}
            {% if url_like and not title_ok %}{% set score = score - 2 %}{% endif %}
            {% if score > 0 and plex_ok %}
              {% set ns.list = ns.list + [{'entity': e.entity_id, 'score': score, 'active': active, 'recent': recent, 'has_meta': (title_ok or artist not in ['','None', none] or album not in ['','None', none]), 'state': st}] %}
            {% endif %}
          {% endfor %}
          {{ (ns.list | tojson) if ns.list else '[]' }}
    - name: MA Meta Detected Entity
      unique_id: ma_meta_detected_entity
      state: >-
        {{ state_attr('sensor.ma_meta_candidates','best_entity') or '' }}
    - name: MA Meta Confidence
      state: >-
        {{ state_attr('sensor.ma_meta_candidates','best_score') | int(0) }}
    - name: MA Detected Receiver Entity
      state: >-
        {% set hw_playing = states('sensor.spectra_ls_hw_playing_entity') %}
        {% if hw_playing not in ['','none','unknown','unavailable'] and states[hw_playing] is not none %}
          {{ hw_playing }}
        {% else %}
        {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
        {% set rooms = [] %}
        {% if rooms_raw is string %}
          {% set raw_l = rooms_raw | lower %}
          {% set raw_trim = rooms_raw | trim %}
          {% if raw_l in ['unknown','unavailable','none',''] %}
            {% set rooms = [] %}
          {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
            {% set rooms = rooms_raw | from_json %}
          {% else %}
            {% set rooms = [] %}
          {% endif %}
        {% else %}
          {% set rooms = rooms_raw or [] %}
        {% endif %}
        {% set ns_playing = namespace(ent='') %}
        {% for r in rooms %}
          {% set ent = (r.entity if r is not none and r.entity is defined else '') %}
          {% if ns_playing.ent == '' and ent not in ['','unknown','unavailable','none'] and states[ent] is not none %}
            {% if (states(ent) | lower) == 'playing' %}
              {% set ns_playing.ent = ent %}
            {% endif %}
          {% endif %}
        {% endfor %}
        {% if ns_playing.ent != '' %}
          {{ ns_playing.ent }}
        {% else %}
        {% set meta = states('sensor.ma_meta_detected_entity') %}
        {% set meta_pos = (state_attr(meta,'media_position') if meta not in ['','unknown','unavailable',none] else 0) | float(0) %}
        {% set meta_src = (state_attr(meta,'source') if meta not in ['','unknown','unavailable',none] else '') or '' %}
        {% set target_opts = (state_attr('input_select.ma_active_target','options') or []) %}
        {% set ns = namespace(best='', best_score=0) %}
        {% for e in states.media_player %}
          {% set st = (e.state | lower) if e is not none else '' %}
          {% set dev_class = (e.attributes.device_class if e.attributes is defined and e.attributes.device_class is defined else '') %}
          {% set volume = (e.attributes.volume_level if e.attributes is defined and e.attributes.volume_level is defined else none) %}
          {% set source_list = (e.attributes.source_list if e.attributes is defined and e.attributes.source_list is defined else []) %}
          {% set sound_mode_list = (e.attributes.sound_mode_list if e.attributes is defined and e.attributes.sound_mode_list is defined else []) %}
          {% set ip = (e.attributes.ip_address if e.attributes is defined and e.attributes.ip_address is defined else '') %}
          {% set rec_pos = (e.attributes.media_position if e.attributes is defined and e.attributes.media_position is defined else 0) | float(0) %}
          {% set rec_src = (e.attributes.source if e.attributes is defined and e.attributes.source is defined else '') %}
          {% set score = 0 %}
          {% if dev_class == 'speaker' %}{% set score = score + 3 %}{% endif %}
          {% if volume is not none %}{% set score = score + 2 %}{% endif %}
          {% if source_list | length > 0 %}{% set score = score + 2 %}{% endif %}
          {% if sound_mode_list | length > 0 %}{% set score = score + 1 %}{% endif %}
          {% if ip not in ['','None', none] %}{% set score = score + 1 %}{% endif %}
          {% if e.entity_id in target_opts %}{% set score = score + 3 %}{% endif %}
          {% if st == 'playing' %}{% set score = score + 2 %}{% elif st == 'paused' %}{% set score = score + 1 %}{% endif %}
          {% if meta_pos > 0 and rec_pos > 0 %}
            {% set diff = (rec_pos - meta_pos) | abs %}
            {% if diff <= 3 %}{% set score = score + 3 %}
            {% elif diff <= 8 %}{% set score = score + 2 %}
            {% elif diff <= 15 %}{% set score = score + 1 %}
            {% endif %}
          {% endif %}
          {% if meta_src and rec_src and meta_src == rec_src %}{% set score = score + 1 %}{% endif %}
          {% if score > ns.best_score %}
            {% set ns.best_score = score %}
            {% set ns.best = e.entity_id %}
          {% endif %}
        {% endfor %}
        {{ ns.best }}
        {% endif %}
        {% endif %}
    - name: MA Active Meta Entity
      unique_id: ma_active_meta_entity
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% set rooms = [] %}
          {% if rooms_raw is string %}
            {% set raw_l = rooms_raw | lower %}
            {% set raw_trim = rooms_raw | trim %}
            {% if raw_l in ['unknown','unavailable','none',''] %}
              {% set rooms = [] %}
            {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
              {% set rooms = rooms_raw | from_json %}
            {% else %}
              {% set rooms = [] %}
            {% endif %}
          {% else %}
            {% set rooms = rooms_raw or [] %}
          {% endif %}
          {% set entries = rooms | selectattr('entity','equalto', t) | list %}
          {% set entry = entries[0] if (entries | length) > 0 else none %}
          {% set override_on = is_state('input_boolean.ma_meta_override_active','on') %}
          {% set override_entity = states('input_text.ma_meta_override_entity') %}
          {% set detected = states('sensor.ma_meta_detected_entity') %}
          {% set detected_conf = states('sensor.ma_meta_confidence') | int(0) %}
          {% set conf_min = states('input_number.ma_meta_confidence_min') | int(4) %}
          {% set detected_ok = detected not in ['','none','unknown','unavailable'] and detected_conf >= conf_min %}
          {% set mapped = (entry.meta if entry is not none and entry.meta is defined and entry.meta not in ['','none','unknown','unavailable'] else '') %}
          {% set kitchen_meta = 'media_player.kitchen_wiim' %}
          {% set kitchen_state = states(kitchen_meta) %}
          {% set kitchen_active = kitchen_state not in ['','none','unknown','unavailable'] %}
          {% set kitchen_title = (state_attr(kitchen_meta,'media_title') or '') %}
          {% set kitchen_artist = (state_attr(kitchen_meta,'media_artist') or '') %}
          {% set kitchen_has_meta = kitchen_title not in ['', 'None', none] or kitchen_artist not in ['', 'None', none] %}
          {% set kitchen_pos_updated = state_attr(kitchen_meta,'media_position_updated_at') %}
          {% set kitchen_pos_ts = as_timestamp(kitchen_pos_updated) if kitchen_pos_updated is not none else 0 %}
          {% set kitchen_pos_age = (as_timestamp(now()) - kitchen_pos_ts) if kitchen_pos_ts > 0 else 9999 %}
          {% set kitchen_stream_active = kitchen_pos_age < 30 %}
          {% if override_on and override_entity not in ['','none','unknown','unavailable'] %}
            {% set meta_candidate = override_entity %}
          {% elif t == 'media_player.kitchen_speakers' and (kitchen_stream_active or kitchen_active) and kitchen_has_meta and not detected_ok %}
            {% set meta_candidate = kitchen_meta %}
          {% elif detected_ok %}
            {% set meta_candidate = detected %}
          {% elif mapped != '' %}
            {% set meta_candidate = mapped %}
          {% else %}
            {% set meta_candidate = t %}
          {% endif %}
          {% set meta_state = states(meta_candidate) if meta_candidate not in ['','none','unknown','unavailable'] else '' %}
          {% set meta_valid = meta_candidate not in ['','none','unknown','unavailable'] and meta_state not in ['unknown','unavailable',''] %}
          {{ meta_candidate if meta_valid else t }}
        {% endif %}
    - name: MA Active Player ID
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_short = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(pid='') %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.pid == '' and (ent == lookup or ent == t or pid == lookup or pid == lookup_short or pid == ('media_player.' ~ lookup_short)) %}
              {% set ns.pid = pid %}
            {% endif %}
          {% endfor %}
          {{ ns.pid }}
        {% endif %}
    - name: MA Active Player ID Resolved
      state: >-
        {% set pid = states('sensor.ma_active_player_id') %}
        {% if pid not in ['','none','unknown','unavailable'] %}
          {{ pid }}
        {% else %}
          {% set t = states('input_select.ma_active_target') %}
          {% set m = states('sensor.ma_active_meta_entity') %}
          {% set lookup = t if t not in ['','none','unknown','unavailable'] else m %}
          {% if lookup.startswith('media_player.') %}
            {{ lookup.split('.')[-1] }}
          {% else %}
            {{ lookup }}
          {% endif %}
        {% endif %}
    - name: Now Playing Entity
      state: >-
        {% set resolver = state_attr('sensor.ma_meta_resolver','best_entity') %}
        {% set res_valid = resolver not in ['','unknown','unavailable','none'] and states[resolver] is not none %}
        {% set t = states('input_select.ma_active_target') %}
        {% set t_valid = t not in ['','unknown','unavailable','none'] and states[t] is not none %}
        {% set t_state = (states(t) | lower) if t_valid else '' %}
        {% set t_title = (state_attr(t,'media_title') if t_valid else '') or '' %}
        {% set t_artist = (state_attr(t,'media_artist') if t_valid else '') or '' %}
        {% set t_has_meta = t_title not in ['', 'None', none] or t_artist not in ['', 'None', none] %}
        {% set ma_state = (states('sensor.ma_active_state') | lower) %}
        {% set ma_title = states('sensor.ma_active_title') %}
        {% set by_host = states('sensor.ma_active_target_by_host') %}
        {% set preferred = states('sensor.ma_active_meta_entity') %}
        {% set pref_valid = preferred not in ['','unknown','unavailable','none'] and states[preferred] is not none %}
        {% set pref_state = (states(preferred) | lower) if pref_valid else '' %}
        {% set pref_title = (state_attr(preferred,'media_title') if pref_valid else '') or '' %}
        {% set pref_artist = (state_attr(preferred,'media_artist') if pref_valid else '') or '' %}
        {% set pref_pos_updated = (state_attr(preferred,'media_position_updated_at') if pref_valid else none) %}
        {% set pref_pos_ts = as_timestamp(pref_pos_updated) if pref_pos_updated is not none else 0 %}
        {% set pref_pos_age = (as_timestamp(now()) - pref_pos_ts) if pref_pos_ts > 0 else 9999 %}
        {% set pref_recent = pref_pos_age < 30 %}
        {% set pref_has_meta = pref_title not in ['', 'None', none] or pref_artist not in ['', 'None', none] %}
        {% set pref_active = pref_state in ['playing','paused'] %}
        {% if res_valid %}
          {{ resolver }}
        {% elif pref_valid and (pref_active or pref_recent or pref_has_meta) %}
          {{ preferred }}
        {% elif t_valid and ma_state == 'playing' and (t_has_meta or ma_title not in ['','unknown','unavailable','none']) %}
          {{ t }}
        {% elif by_host not in ['','unknown','unavailable','none'] and states[by_host] is not none %}
          {{ by_host }}
        {% elif preferred not in ['','unknown','unavailable','none'] %}
          {{ preferred }}
        {% else %}
          {{ states('input_select.ma_active_target') }}
        {% endif %}
    - name: Now Playing Title
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {% if t in ['','unknown','unavailable',none] %}
          {{ '' }}
        {% else %}
          {% set lookup_id = t %}
          {% set short_id = t.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% if ns.p is none and (p.player_id == lookup_id or p.player_id == short_id or p.player_id == ('media_player.' ~ short_id) or p.entity_id == lookup_id) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_title = (ns.p.current_media.title if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set ma_uri = (ns.p.current_media.uri if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_title = (stream_meta.title if stream_meta is not none and stream_meta.title is defined else '') | default('', true) %}
          {% set title = (ma_title if ma_title not in ['None', none] else '') | default('', true) %}
          {% set uri = (ma_uri if ma_uri not in ['None', none] else '') | default('', true) %}
          {% set title_l = title | lower %}
          {% set uri_l = uri | lower %}
          {% set queue_title = title_l in ['music assistant queue','media assistant queue'] %}
          {% if queue_title %}{% set title = '' %}{% endif %}
          {% set url_like = (('://' in title_l) or title_l.startswith('www.') or title_l.endswith('.mp3') or title_l.endswith('.flac') or title_l.endswith('.wav') or title_l.endswith('.m4a') or title_l.endswith('.aac') or title_l.endswith('.ogg') or
                              (('://' in uri_l) or uri_l.startswith('www.') or uri_l.endswith('.mp3') or uri_l.endswith('.flac') or uri_l.endswith('.wav') or uri_l.endswith('.m4a') or uri_l.endswith('.aac') or uri_l.endswith('.ogg'))) %}
          {% if title and not url_like %}
            {{ title }}
          {% else %}
            {% set stream_l = stream_title | lower %}
            {% set stream_queue = stream_l in ['music assistant queue','media assistant queue'] %}
            {% set stream_url = (('://' in stream_l) or stream_l.startswith('www.') or stream_l.endswith('.mp3') or stream_l.endswith('.flac') or stream_l.endswith('.wav') or stream_l.endswith('.m4a') or stream_l.endswith('.aac') or stream_l.endswith('.ogg')) %}
            {% if stream_title and not stream_url and not stream_queue %}
              {{ stream_title }}
            {% else %}
            {% set ha_title = state_attr(t,'media_title') or '' %}
            {% set ma_active_title = states('sensor.ma_active_title') | default('', true) %}
            {% set ma_active_tl = ma_active_title | lower %}
            {% set ma_active_queue = ma_active_tl in ['music assistant queue','media assistant queue'] %}
            {% set ha_id = state_attr(t,'media_content_id') or '' %}
            {% set ha_tl = ha_title | lower %}
            {% set ha_il = ha_id | lower %}
            {% set ha_queue = ha_tl in ['music assistant queue','media assistant queue'] %}
            {% set ha_url = (('://' in ha_tl) or ha_tl.startswith('www.') or ha_tl.endswith('.mp3') or ha_tl.endswith('.flac') or ha_tl.endswith('.wav') or ha_tl.endswith('.m4a') or ha_tl.endswith('.aac') or ha_tl.endswith('.ogg') or
                             (('://' in ha_il) or ha_il.startswith('www.') or ha_il.endswith('.mp3') or ha_il.endswith('.flac') or ha_il.endswith('.wav') or ha_il.endswith('.m4a') or ha_il.endswith('.aac') or ha_il.endswith('.ogg'))) %}
            {% set fallback_title = (ha_title if not ha_url and not ha_queue else '') | default('', true) %}
            {% if fallback_title != '' %}
              {{ fallback_title }}
            {% elif ma_active_title != '' and not ma_active_queue %}
              {{ ma_active_title }}
            {% else %}
              {{ (state_attr(t,'app_name') or state_attr(t,'source') or state_attr(t,'friendly_name') or '') | default('', true) }}
            {% endif %}
            {% endif %}
          {% endif %}
        {% endif %}
    - name: Now Playing Artist
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {% if t in ['','unknown','unavailable',none] %}
          {{ '' }}
        {% else %}
          {% set lookup_id = t %}
          {% set short_id = t.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% if ns.p is none and (p.player_id == lookup_id or p.player_id == short_id or p.player_id == ('media_player.' ~ short_id) or p.entity_id == lookup_id) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_artist = (ns.p.current_media.artist if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_artist = (stream_meta.artist if stream_meta is not none and stream_meta.artist is defined else '') | default('', true) %}
          {% if ma_artist and ma_artist not in ['None', none] %}
            {{ ma_artist }}
          {% elif stream_artist and stream_artist not in ['None', none] %}
            {{ stream_artist }}
          {% else %}
            {{ (state_attr(t,'media_artist') or '') | default('', true) }}
          {% endif %}
        {% endif %}
    - name: Now Playing Album
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {% if t in ['','unknown','unavailable',none] %}
          {{ '' }}
        {% else %}
          {% set lookup_id = t %}
          {% set short_id = t.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% if ns.p is none and (p.player_id == lookup_id or p.player_id == short_id or p.player_id == ('media_player.' ~ short_id) or p.entity_id == lookup_id) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_album = (ns.p.current_media.album if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_album = (stream_meta.album if stream_meta is not none and stream_meta.album is defined else '') | default('', true) %}
          {% if ma_album and ma_album not in ['None', none] %}
            {{ ma_album }}
          {% elif stream_album and stream_album not in ['None', none] %}
            {{ stream_album }}
          {% else %}
            {{ (state_attr(t,'media_album_name') or state_attr(t,'media_album') or '') | default('', true) }}
          {% endif %}
        {% endif %}
    - name: Now Playing Source
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {% if t in ['','unknown','unavailable',none] %}
          {{ '' }}
        {% else %}
          {% set lookup_id = t %}
          {% set short_id = t.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% if ns.p is none and (p.player_id == lookup_id or p.player_id == short_id or p.player_id == ('media_player.' ~ short_id) or p.entity_id == lookup_id) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_src = (ns.p.active_source if ns.p is not none else '') | default('', true) %}
          {% set ma_src_l = ma_src | lower %}
          {% set ma_src_queue = ma_src_l in ['music assistant queue','media assistant queue'] %}
          {% if ma_src and ma_src not in ['None', none] and not ma_src_queue %}
            {{ ma_src }}
          {% else %}
            {% set ha_src = (state_attr(t,'source') or '') | default('', true) %}
            {% set ha_src_l = ha_src | lower %}
            {% set ha_src_queue = ha_src_l in ['music assistant queue','media assistant queue'] %}
            {% if ha_src and not ha_src_queue %}
              {% if ha_src.startswith('media_player.') and states[ha_src] is not none %}
                {{ state_attr(ha_src,'friendly_name') or ha_src.split('.')[-1] }}
              {% else %}
                {{ ha_src }}
              {% endif %}
            {% else %}
              {{ (state_attr(t,'app_name') or '') | default('', true) }}
            {% endif %}
          {% endif %}
        {% endif %}
    - name: Now Playing State
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {% if t in ['','unknown','unavailable',none] %}
          {{ 'idle' }}
        {% else %}
          {% set pos_updated = state_attr(t,'media_position_updated_at') %}
          {% set pos_ts = as_timestamp(pos_updated) if pos_updated is not none else 0 %}
          {% set pos_age = (as_timestamp(now()) - pos_ts) if pos_ts > 0 else 9999 %}
          {% set pos_recent = pos_age < 30 %}
          {% set lookup_id = t %}
          {% set short_id = t.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% if ns.p is none and (p.player_id == lookup_id or p.player_id == short_id or p.player_id == ('media_player.' ~ short_id) or p.entity_id == lookup_id) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_state = (ns.p.playback_state if ns.p is not none else '') | default('', true) %}
          {% set ha_state = states(t) | lower %}
          {% set active_state = states('sensor.ma_active_state') | lower %}
          {% if ha_state in ['unknown','unavailable','none',''] %}
            {% if active_state not in ['unknown','unavailable','none',''] %}
              {{ active_state }}
            {% elif ma_state and (ma_state | lower) not in ['unknown','unavailable','none',''] %}
              {{ ma_state | lower }}
            {% else %}
              {{ 'idle' }}
            {% endif %}
          {% elif ha_state == 'paused' and pos_recent %}
            {{ 'playing' }}
          {% elif ma_state and (ma_state | lower) not in ['none','unknown','unavailable',''] %}
            {{ ma_state | lower }}
          {% else %}
            {% if ha_state in ['unknown','unavailable','none',''] %}
              {{ 'idle' }}
            {% else %}
              {{ ha_state }}
            {% endif %}
          {% endif %}
        {% endif %}
    - name: Now Playing Position
      unit_of_measurement: s
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {{ (state_attr(t,'media_position') if t not in ['','unknown','unavailable',none] else 0) | float(0) }}
    - name: Now Playing Duration
      unit_of_measurement: s
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {{ (state_attr(t,'media_duration') if t not in ['','unknown','unavailable',none] else 0) | float(0) }}
    - name: Now Playing Volume
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {{ (state_attr(t,'volume_level') if t not in ['','unknown','unavailable',none] else 0) | float(0) }}
    - name: Now Playing Friendly
      state: >-
        {% set t = states('sensor.now_playing_entity') %}
        {{ (state_attr(t,'friendly_name') if t not in ['','unknown','unavailable',none] else '') | default('', true) }}
    - name: MA Control Hosts
      state: >-
        {% set target = states('input_select.ma_active_target') %}
        {% set valid_target = target not in ['none','unknown','unavailable',''] %}
        {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
        {% set rooms = [] %}
        {% if rooms_raw is string %}
          {% set raw_l = rooms_raw | lower %}
          {% set raw_trim = rooms_raw | trim %}
          {% if raw_l in ['unknown','unavailable','none',''] %}
            {% set rooms = [] %}
          {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
            {% set rooms = rooms_raw | from_json %}
          {% else %}
            {% set rooms = [] %}
          {% endif %}
        {% else %}
          {% set rooms = rooms_raw or [] %}
        {% endif %}
        {% set members = state_attr(target,'group_members') or state_attr(target,'members') or [] %}
        {% set target_host = '' %}
        {% if valid_target %}
          {% set target_entries = (rooms | selectattr('entity','equalto', target) | list) %}
          {% set target_entry = (target_entries[0] if (target_entries | length) > 0 else none) %}
          {% if target_entry is not none and target_entry.tcp_host is defined and target_entry.tcp_host not in ['','unknown','unavailable'] %}
            {% set target_host = target_entry.tcp_host %}
          {% endif %}
        {% endif %}
        {% if target_host != '' %}
          {{ target_host }}
        {% else %}
          {% set hosts = [] %}
          {% for m in members %}
            {% for r in rooms %}
              {% if r.entity is defined and r.entity == m and r.tcp_host is defined and r.tcp_host not in ['','unknown','unavailable'] %}
                {% set hosts = hosts + [r.tcp_host] %}
              {% endif %}
            {% endfor %}
          {% endfor %}
          {% if hosts | length == 0 %}
            {% set primary_entity = states('input_text.spectra_ls_target_primary_entity') %}
            {% set room_entity = states('input_text.spectra_ls_target_room_entity') %}
            {% set primary_host = states('input_text.spectra_ls_target_primary_tcp_host') %}
            {% set room_host = states('input_text.spectra_ls_target_room_tcp_host') %}
            {% if valid_target and target == primary_entity and primary_host not in ['','unknown','unavailable','none'] %}
              {% set hosts = [primary_host] %}
            {% elif valid_target and target == room_entity and room_host not in ['','unknown','unavailable','none'] %}
              {% set hosts = [room_host] %}
            {% endif %}
          {% endif %}
          {% if hosts | length == 0 %}
            {% set candidates = [states('sensor.ma_detected_receiver_entity'), states('sensor.ma_active_meta_entity'), target] %}
            {% set ns = namespace(picked='') %}
            {% for c in candidates %}
              {% if ns.picked == '' and c not in ['','none','unknown','unavailable'] %}
                {% set c_state = states(c) %}
                {% if c_state not in ['unknown','unavailable',''] %}
                  {% set ip = state_attr(c,'ip_address') or '' %}
                  {% set model = state_attr(c,'device_model') or '' %}
                  {% set role = state_attr(c,'group_role') or '' %}
                  {% set gstate = state_attr(c,'group_state') or '' %}
                  {% set purpose = state_attr(c,'integration_purpose') or '' %}
                  {% set ma_ok = state_attr(c,'music_assistant_compatible') %}
                  {% set is_linkplay = (ip not in ['','None', none]) and ((ma_ok is true) or (model not in ['','None', none]) or (role not in ['','None', none]) or (gstate not in ['','None', none]) or (purpose not in ['','None', none])) %}
                  {% if is_linkplay %}
                    {% set ns.picked = ip %}
                  {% endif %}
                {% endif %}
              {% endif %}
            {% endfor %}
            {% if ns.picked != '' %}
              {% set hosts = [ns.picked] %}
            {% endif %}
          {% endif %}
          {{ hosts | unique | join(',') if (hosts | length) > 0 else '' }}
        {% endif %}
    - name: MA Control Targets
      state: >-
        {% set rooms = state_attr('sensor.spectra_ls_rooms_raw','rooms') or [] %}
        {{ rooms | length }}
      attributes:
        entities: >-
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% set rooms = [] %}
          {% if rooms_raw is string %}
            {% set raw_l = rooms_raw | lower %}
            {% set raw_trim = rooms_raw | trim %}
            {% if raw_l in ['unknown','unavailable','none',''] %}
              {% set rooms = [] %}
            {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
              {% set rooms = rooms_raw | from_json %}
            {% else %}
              {% set rooms = [] %}
            {% endif %}
          {% else %}
            {% set rooms = rooms_raw or [] %}
          {% endif %}
          {% set ns = namespace(entities=[]) %}
          {% for r in rooms %}
            {% if r is not none and r.entity is defined and r.entity not in ['','none','unknown','unavailable'] %}
              {% set ns.entities = ns.entities + [r.entity] %}
            {% endif %}
          {% endfor %}
          {{ ns.entities | tojson }}
        labels: >-
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% set rooms = [] %}
          {% if rooms_raw is string %}
            {% set raw_l = rooms_raw | lower %}
            {% set raw_trim = rooms_raw | trim %}
            {% if raw_l in ['unknown','unavailable','none',''] %}
              {% set rooms = [] %}
            {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
              {% set rooms = rooms_raw | from_json %}
            {% else %}
              {% set rooms = [] %}
            {% endif %}
          {% else %}
            {% set rooms = rooms_raw or [] %}
          {% endif %}
          {% set ns = namespace(labels=[]) %}
          {% for r in rooms %}
            {% set label = '' %}
            {% if r is not none and r.label is defined and r.label not in ['','none','unknown','unavailable'] %}
              {% set label = r.label %}
            {% endif %}
            {% if label == '' and r is not none and r.entity is defined and r.entity not in ['','none','unknown','unavailable'] %}
              {% set friendly = state_attr(r.entity, 'friendly_name') %}
              {% if friendly not in ['','None', none] %}
                {% set label = friendly %}
              {% else %}
                {% set label = r.entity %}
              {% endif %}
            {% endif %}
            {% if label == '' %}{% set label = 'Target' %}{% endif %}
            {% set host_raw = (r.tcp_host if r is not none and r.tcp_host is defined else '') %}
            {% set host = (host_raw | string | trim) %}
            {% set host_no_port = host.split(':')[0] if ':' in host else host %}
            {% set ip_suffix = host_no_port %}
            {% if '.' in host_no_port %}
              {% set parts = host_no_port.split('.') %}
              {% if parts | length >= 2 %}
                {% set ip_suffix = parts[-2] ~ '.' ~ parts[-1] %}
              {% endif %}
            {% endif %}
            {% if ip_suffix not in ['','none','unknown','unavailable'] %}
              {% set ns.labels = ns.labels + [label ~ ' ' ~ ip_suffix] %}
            {% else %}
              {% set ns.labels = ns.labels + [label] %}
            {% endif %}
          {% endfor %}
          {{ ns.labels | tojson }}
    - name: MA Control Host
      state: >-
        {% set hosts = states('sensor.ma_control_hosts') %}
        {% if ',' in hosts %}
          {{ hosts.split(',')[0] }}
        {% else %}
          {{ hosts }}
        {% endif %}
    - name: MA Active Target By Host
      state: >-
        {% set host = states('sensor.ma_control_host') %}
        {% if host in ['','none','unknown','unavailable'] %}
          {{ '' }}
        {% else %}
          {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
          {% set rooms = [] %}
          {% if rooms_raw is string %}
            {% set raw_l = rooms_raw | lower %}
            {% set raw_trim = rooms_raw | trim %}
            {% if raw_l in ['unknown','unavailable','none',''] %}
              {% set rooms = [] %}
            {% elif raw_trim.startswith('[') or raw_trim.startswith('{') %}
              {% set rooms = rooms_raw | from_json %}
            {% else %}
              {% set rooms = [] %}
            {% endif %}
          {% else %}
            {% set rooms = rooms_raw or [] %}
          {% endif %}
          {% set ns = namespace(ent='') %}
          {% for r in rooms %}
            {% if r.tcp_host is defined and r.tcp_host == host and r.entity is defined and r.entity not in ['','none','unknown','unavailable'] %}
              {% set ns.ent = r.entity %}
            {% endif %}
          {% endfor %}
          {{ ns.ent }}
        {% endif %}
    - name: MA Control Port
      state: >-
        8899
    - name: MA Active Friendly
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% set by_host = states('sensor.ma_active_target_by_host') %}
        {% if by_host not in ['','none','unknown','unavailable'] and states[by_host] is not none %}
          {{ (state_attr(by_host, 'friendly_name') or '') | default('', true) }}
        {% elif t not in ['none','unknown','unavailable',''] and states[t] is not none %}
          {{ (state_attr(t, 'friendly_name') or '') | default('', true) }}
        {% else %}
          {{ '' }}
        {% endif %}
    - name: MA Active State
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ 'idle' }}
        {% else %}
          {% set ap_state = (state_attr('sensor.ma_active_player','playback_state') or state_attr('sensor.ma_active_player','result').playback_state if state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').playback_state is defined else '') | default('', true) %}
          {% if ap_state not in ['','none','unknown','unavailable'] %}
            {{ ap_state | lower }}
          {% else %}
            {% set meta = states('sensor.ma_active_meta_entity') %}
            {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
            {% set meta_state = states(meta) | lower %}
            {% set meta_title = (state_attr(meta,'media_title') or '') %}
            {% set meta_artist = (state_attr(meta,'media_artist') or '') %}
            {% set meta_has = meta_title not in ['', 'None', none] or meta_artist not in ['', 'None', none] %}
            {% set meta_src = (state_attr(meta,'source') or '') | lower %}
            {% set meta_app = (state_attr(meta,'app_name') or '') | lower %}
            {% set meta_pos_updated = state_attr(meta,'media_position_updated_at') %}
            {% set meta_pos_ts = as_timestamp(meta_pos_updated) if meta_pos_updated is not none else 0 %}
            {% set meta_pos_age = (as_timestamp(now()) - meta_pos_ts) if meta_pos_ts > 0 else 9999 %}
            {% set meta_recent = meta_pos_age < 30 %}
            {% set meta_recent_long = meta_pos_age < 300 %}
            {% set meta_airplay = meta_src == 'airplay' or meta_app == 'airplay' %}
            {% if meta_has and (meta_recent or (meta_airplay and meta_recent_long)) %}
              {{ 'playing' }}
            {% else %}
            {% set target_state = states(t) | default('', true) %}
            {% if target_state not in ['','none','unknown','unavailable'] %}
              {{ target_state | lower }}
            {% else %}
              {{ states(meta) | default('idle', true) }}
            {% endif %}
            {% endif %}
          {% endif %}
        {% endif %}
    - name: MA Active Title
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set _mp = states.media_player | list %}
          {% set spectra_entity = states('input_text.spectra_ls_target_primary_entity') %}
          {% set ap_id = states('sensor.ma_active_player_id') %}
          {% set t_short = t.split('.')[-1] %}
          {% set ap_match = ap_id == t or ap_id == t_short or ap_id == ('media_player.' ~ t_short) %}
          {% set ap_current = (state_attr('sensor.ma_active_player','current_media') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').current_media if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').current_media is defined else {}) %}
          {% set ap_stream = (state_attr('sensor.ma_active_player','streamdetails') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').streamdetails if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').streamdetails is defined else {}) %}
          {% set ap_stream_meta = ap_stream.stream_metadata if ap_stream is defined and ap_stream.stream_metadata is defined else none %}
          {% set ap_title = ap_current.title if ap_current is defined and ap_current.title is defined else '' %}
          {% set ap_name = ap_current.name if ap_current is defined and ap_current.name is defined else '' %}
          {% set ap_track = ap_current.metadata.title if ap_current is defined and ap_current.metadata is defined and ap_current.metadata.title is defined else '' %}
          {% set ap_stream_title = ap_stream_meta.title if ap_stream_meta is not none and ap_stream_meta.title is defined else '' %}
          {% set ap_stream_name = ap_stream_meta.stream_title if ap_stream_meta is not none and ap_stream_meta.stream_title is defined else '' %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_id = lookup %}
          {% set short_id = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.p is none and (pid == lookup_id or pid == short_id or pid == ('media_player.' ~ short_id) or ent == lookup or ent == t) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_title = (ns.p.current_media.title if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set ma_name = (ns.p.current_media.name if ns.p is not none and ns.p.current_media is defined and ns.p.current_media.name is defined else '') | default('', true) %}
          {% set ma_track = (ns.p.current_media.metadata.title if ns.p is not none and ns.p.current_media is defined and ns.p.current_media.metadata is defined and ns.p.current_media.metadata.title is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_title = (stream_meta.title if stream_meta is not none and stream_meta.title is defined else '') | default('', true) %}
          {% set stream_name = (stream_meta.stream_title if stream_meta is not none and stream_meta.stream_title is defined else '') | default('', true) %}
          {% set ha_target_title = (state_attr(t, 'media_title') or '') | default('', true) %}
          {% set ha_meta_title = (state_attr(meta, 'media_title') or '') | default('', true) %}
          {% set ha_primary_title = (state_attr(spectra_entity, 'media_title') if spectra_entity != '' and t == spectra_entity else '') | default('', true) %}
          {% set ns_ha = namespace(val='') %}
          {% for c in [ha_target_title, ha_meta_title, ha_primary_title] %}
            {% set c_l = c | lower %}
            {% set url_like = (('://' in c_l) or c_l.startswith('www.') or c_l.endswith('.mp3') or c_l.endswith('.flac') or c_l.endswith('.wav') or c_l.endswith('.m4a') or c_l.endswith('.aac') or c_l.endswith('.ogg')) %}
            {% if ns_ha.val == '' and c and not url_like %}
              {% set ns_ha.val = c %}
            {% endif %}
          {% endfor %}
          {% set ha_title = ns_ha.val %}
          {% set candidates = [ha_title, ap_title, ap_name, ap_track, ap_stream_title, ap_stream_name, ma_title, ma_name, ma_track, stream_title, stream_name] %}
          {% set ns2 = namespace(val='') %}
          {% for c in candidates %}
            {% set c_l = c | lower %}
            {% set url_like = (('://' in c_l) or c_l.startswith('www.') or c_l.endswith('.mp3') or c_l.endswith('.flac') or c_l.endswith('.wav') or c_l.endswith('.m4a') or c_l.endswith('.aac') or c_l.endswith('.ogg')) %}
            {% if ns2.val == '' and c and not url_like %}
              {% set ns2.val = c %}
            {% endif %}
          {% endfor %}
          {{ ns2.val | default('', true) }}
        {% endif %}
    - name: MA Active Artist
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set _mp = states.media_player | list %}
          {% set spectra_entity = states('input_text.spectra_ls_target_primary_entity') %}
          {% set ap_id = states('sensor.ma_active_player_id') %}
          {% set t_short = t.split('.')[-1] %}
          {% set ap_match = ap_id == t or ap_id == t_short or ap_id == ('media_player.' ~ t_short) %}
          {% set ap_current = (state_attr('sensor.ma_active_player','current_media') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').current_media if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').current_media is defined else {}) %}
          {% set ap_stream = (state_attr('sensor.ma_active_player','streamdetails') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').streamdetails if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').streamdetails is defined else {}) %}
          {% set ap_stream_meta = ap_stream.stream_metadata if ap_stream is defined and ap_stream.stream_metadata is defined else none %}
          {% set ap_artist = ap_current.artist if ap_current is defined and ap_current.artist is defined else '' %}
          {% set ap_artist = (ap_artist if ap_artist else (ap_current.metadata.artist if ap_current is defined and ap_current.metadata is defined and ap_current.metadata.artist is defined else '')) %}
          {% set ap_stream_artist = ap_stream_meta.artist if ap_stream_meta is not none and ap_stream_meta.artist is defined else '' %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_id = lookup %}
          {% set short_id = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.p is none and (pid == lookup_id or pid == short_id or pid == ('media_player.' ~ short_id) or ent == lookup or ent == t) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_artist = (ns.p.current_media.artist if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_artist = (stream_meta.artist if stream_meta is not none and stream_meta.artist is defined else '') | default('', true) %}
          {% set ha_primary_artist = (state_attr(spectra_entity, 'media_artist') if spectra_entity != '' and t == spectra_entity else '') | default('', true) %}
          {% set ha_artist = (state_attr(t, 'media_artist') or state_attr(meta, 'media_artist') or '') | default('', true) %}
          {{ (ha_artist or ha_primary_artist or ap_artist or ap_stream_artist or ma_artist or stream_artist or '') | default('', true) }}
        {% endif %}
    - name: MA Active Album
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set _mp = states.media_player | list %}
          {% set spectra_entity = states('input_text.spectra_ls_target_primary_entity') %}
          {% set ap_id = states('sensor.ma_active_player_id') %}
          {% set t_short = t.split('.')[-1] %}
          {% set ap_match = ap_id == t or ap_id == t_short or ap_id == ('media_player.' ~ t_short) %}
          {% set ap_current = (state_attr('sensor.ma_active_player','current_media') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').current_media if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').current_media is defined else {}) %}
          {% set ap_stream = (state_attr('sensor.ma_active_player','streamdetails') if ap_match else {}) or (state_attr('sensor.ma_active_player','result').streamdetails if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').streamdetails is defined else {}) %}
          {% set ap_stream_meta = ap_stream.stream_metadata if ap_stream is defined and ap_stream.stream_metadata is defined else none %}
          {% set ap_album = ap_current.album if ap_current is defined and ap_current.album is defined else '' %}
          {% set ap_album = (ap_album if ap_album else (ap_current.metadata.album if ap_current is defined and ap_current.metadata is defined and ap_current.metadata.album is defined else '')) %}
          {% set ap_stream_album = ap_stream_meta.album if ap_stream_meta is not none and ap_stream_meta.album is defined else '' %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_id = lookup %}
          {% set short_id = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.p is none and (pid == lookup_id or pid == short_id or pid == ('media_player.' ~ short_id) or ent == lookup or ent == t) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_album = (ns.p.current_media.album if ns.p is not none and ns.p.current_media is defined else '') | default('', true) %}
          {% set stream_meta = (ns.p.streamdetails.stream_metadata if ns.p is not none and ns.p.streamdetails is defined and ns.p.streamdetails.stream_metadata is defined else none) %}
          {% set stream_album = (stream_meta.album if stream_meta is not none and stream_meta.album is defined else '') | default('', true) %}
          {% set ha_primary_album = (state_attr(spectra_entity, 'media_album_name') or state_attr(spectra_entity, 'media_album') if spectra_entity != '' and t == spectra_entity else '') | default('', true) %}
          {% set ha_album = (state_attr(t, 'media_album_name') or state_attr(t, 'media_album') or state_attr(meta, 'media_album_name') or state_attr(meta, 'media_album') or '') | default('', true) %}
          {{ (ha_album or ha_primary_album or ap_album or ap_stream_album or ma_album or stream_album or '') | default('', true) }}
        {% endif %}
    - name: MA Active App
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set _mp = states.media_player | list %}
          {% set spectra_entity = states('input_text.spectra_ls_target_primary_entity') %}
          {% set ap_id = states('sensor.ma_active_player_id') %}
          {% set t_short = t.split('.')[-1] %}
          {% set ap_match = ap_id == t or ap_id == t_short or ap_id == ('media_player.' ~ t_short) %}
          {% set ap_app = ((state_attr('sensor.ma_active_player','app_name') if ap_match else '') or (state_attr('sensor.ma_active_player','result').app_name if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').app_name is defined else '') or '') | default('', true) %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_id = lookup %}
          {% set short_id = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.p is none and (pid == lookup_id or pid == short_id or pid == ('media_player.' ~ short_id) or ent == lookup or ent == t) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_app = (ns.p.app_name if ns.p is not none and ns.p.app_name is defined else '') | default('', true) %}
          {% set ha_primary_app = (state_attr(spectra_entity, 'app_name') if spectra_entity != '' and t == spectra_entity else '') | default('', true) %}
          {% set ha_app = (state_attr(t, 'app_name') or state_attr(meta, 'app_name') or '') | default('', true) %}
          {% set app = (ha_app or ha_primary_app or ap_app or ma_app or '') | default('', true) %}
          {% set app_l = app | lower %}
          {{ '' if app_l in ['media assistant queue','music assistant queue'] else app }}
        {% endif %}
    - name: MA Active Source
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ '' }}
        {% else %}
          {% set _mp = states.media_player | list %}
          {% set spectra_entity = states('input_text.spectra_ls_target_primary_entity') %}
          {% set ap_id = states('sensor.ma_active_player_id') %}
          {% set t_short = t.split('.')[-1] %}
          {% set ap_match = ap_id == t or ap_id == t_short or ap_id == ('media_player.' ~ t_short) %}
          {% set ap_src = ((state_attr('sensor.ma_active_player','active_source') if ap_match else '') or (state_attr('sensor.ma_active_player','result').active_source if ap_match and state_attr('sensor.ma_active_player','result') is defined and state_attr('sensor.ma_active_player','result').active_source is defined else '') or '') | default('', true) %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {% set lookup_id = lookup %}
          {% set short_id = lookup.split('.')[-1] %}
          {% set players = state_attr('sensor.ma_players','result') or [] %}
          {% set ns = namespace(p=None) %}
          {% for p in players %}
            {% set pid = (p.player_id if p.player_id is defined else '') %}
            {% set ent = (p.entity_id if p.entity_id is defined else '') %}
            {% if ns.p is none and (pid == lookup_id or pid == short_id or pid == ('media_player.' ~ short_id) or ent == lookup or ent == t) %}
              {% set ns.p = p %}
            {% endif %}
          {% endfor %}
          {% set ma_src = (ns.p.active_source if ns.p is not none else '') | default('', true) %}
          {% set ha_primary_src = (state_attr(spectra_entity, 'source') if spectra_entity != '' and t == spectra_entity else '') | default('', true) %}
          {% set ha_src = (state_attr(t, 'source') or state_attr(meta, 'source') or '') | default('', true) %}
          {% set src = (ha_src or ha_primary_src or ap_src or ma_src or '') | default('', true) %}
          {% set src_l = src | lower %}
          {{ '' if src_l in ['media assistant queue','music assistant queue'] else src }}
        {% endif %}
    - name: MA Active Duration
      unit_of_measurement: s
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ 0 }}
        {% else %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {{ (state_attr(meta, 'media_duration') or state_attr(t, 'media_duration') or 0) | float(0) }}
        {% endif %}
    - name: MA Active Position
      unit_of_measurement: s
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ 0 }}
        {% else %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {{ (state_attr(meta, 'media_position') or state_attr(t, 'media_position') or 0) | float(0) }}
        {% endif %}
    - name: MA Meta Age (s)
      unit_of_measurement: s
      state: >-
        {% set meta = states('sensor.ma_active_meta_entity') %}
        {% if meta in ['','none','unknown','unavailable'] or states[meta] is none %}
          {{ 9999 }}
        {% else %}
          {% set pos_updated = state_attr(meta,'media_position_updated_at') %}
          {% set pos_ts = as_timestamp(pos_updated) if pos_updated is not none else 0 %}
          {% set base_ts = pos_ts if pos_ts > 0 else as_timestamp(states[meta].last_changed) %}
          {% if base_ts is none %}
            {{ 9999 }}
          {% else %}
            {{ (as_timestamp(now()) - base_ts) | float(0) }}
          {% endif %}
        {% endif %}
    - name: MA Active Volume
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% if t in ['none','unknown','unavailable',''] %}
          {{ 0 }}
        {% else %}
          {% set meta = states('sensor.ma_active_meta_entity') %}
          {% set meta = (meta if meta not in ['','none','unknown','unavailable'] else t) %}
          {{ (state_attr(meta, 'volume_level') or state_attr(t, 'volume_level') or 0) | float(0) }}
        {% endif %}
    - name: MA Balance Left Label
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% set members = state_attr(t,'group_members') or state_attr(t,'members') or [] %}
        {% if members | length == 0 %}
          {{ '' | default('', true) }}
        {% elif members | length == 2 %}
          {{ (state_attr(members[0], 'friendly_name') or members[0]) | default('', true) }}
        {% else %}
          LEFT
        {% endif %}
    - name: MA Balance Right Label
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% set members = state_attr(t,'group_members') or state_attr(t,'members') or [] %}
        {% if members | length == 0 %}
          {{ '' | default('', true) }}
        {% elif members | length > 0 %}
          {{ (state_attr(members[-1], 'friendly_name') or members[-1]) | default('', true) }}
        {% else %}
          {{ '' | default('', true) }}
        {% endif %}
    - name: MA Balance Group Size
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% set members = state_attr(t,'group_members') or state_attr(t,'members') or [] %}
        {{ members | length }}
- binary_sensor:
    - name: MA Meta Stale
      state: >-
        {% set age = states('sensor.ma_meta_age_s') | float(9999) %}
        {% set stale_s = states('input_number.ma_meta_stale_s') | float(45) %}
        {{ age > stale_s }}
    - name: MA Meta Low Confidence
      state: >-
        {% set conf = states('sensor.ma_meta_confidence') | int(0) %}
        {% set min_conf = states('input_number.ma_meta_confidence_min') | int(4) %}
        {{ conf < min_conf }}
    - name: MA Control Ambiguous
      state: >-
        {% set target = states('input_select.ma_active_target') %}
        {% set target_ok = target not in ['none','unknown','unavailable',''] %}
        {% set host = states('sensor.ma_control_host') %}
        {% set host_ok = host not in ['none','unknown','unavailable',''] %}
        {% set now_playing = states('sensor.now_playing_entity') | lower %}
        {% set raw_amb = states('input_text.ma_ambiguous_entities') | lower %}
        {% set amb_list = raw_amb.split(',') | map('trim') | reject('equalto','') | list %}
        {% set amb_entity = now_playing not in ['none','unknown','unavailable',''] and now_playing in amb_list %}
        {% set src = (states('sensor.ma_active_source') or '') | lower %}
        {% set app = (states('sensor.ma_active_app') or '') | lower %}
        {% set airplay = 'airplay' in src or 'airplay' in app %}
        {% set appletv = false %}
        {% set hw = states('sensor.spectra_ls_hw_playing_entity') %}
        {% set hw_ok = hw not in ['none','unknown','unavailable',''] and states[hw] is not none %}
        {% set rooms_raw = state_attr('sensor.spectra_ls_rooms_raw','rooms') %}
        {% set rooms = (rooms_raw | from_json) if rooms_raw is string else (rooms_raw or []) %}
        {% set ns = namespace(room_playing=false) %}
        {% for r in rooms %}
          {% if r.entity is defined and r.entity not in ['','none','unknown','unavailable'] and states[r.entity] is not none %}
            {% if (states(r.entity) | lower) == 'playing' %}
              {% set ns.room_playing = true %}
            {% endif %}
          {% endif %}
        {% endfor %}
        {% set meta_low = is_state('binary_sensor.ma_meta_low_confidence','on') %}
        {% set np = states('sensor.now_playing_entity') %}
        {% set np_state = (states(np) | lower) if np not in ['','none','unknown','unavailable'] else '' %}
        {% set np_active = np_state in ['playing','paused'] %}
        {% set np_is_playing = (state_attr(np,'is_playing') if np not in ['','none','unknown','unavailable'] else none) %}
        {% set np_is_paused = (state_attr(np,'is_paused') if np not in ['','none','unknown','unavailable'] else none) %}
        {% set np_play_state = ((state_attr(np,'play_state') if np not in ['','none','unknown','unavailable'] else '') | lower) %}
        {% set np_has_meta = ((state_attr(np,'media_title') or '') not in ['','None', none]) or ((state_attr(np,'media_artist') or '') not in ['','None', none]) %}
        {% set np_active_strong = np_active or (np_is_playing is true) or (np_is_paused is true) or (np_play_state in ['play','playing','pause','paused']) %}
        {% set np_matches_target = np == target or np == states('sensor.ma_active_meta_entity') or np == states('sensor.ma_active_target_by_host') %}
        {% set strong_now_playing = np_matches_target and (np_active_strong or np_has_meta) %}
        {% set signal_ok = hw_ok or ns.room_playing or (host_ok and (not meta_low or strong_now_playing)) %}
        {{ (not target_ok) or (not host_ok) or (not signal_ok) or airplay or amb_entity }}
    - name: MA Active Is Group
      state: >-
        {% set t = states('input_select.ma_active_target') %}
        {% set members = state_attr(t,'group_members') or state_attr(t,'members') or [] %}
        {{ members | length > 0 }}

- select:
    - name: MA Active Target Friendly
      unique_id: ma_active_target_friendly
      options: >-
        {{ ['None'] }}
      state: >-
        {{ 'None' }}
      select_option:
        service: input_select.select_option
        data:
          entity_id: input_select.ma_active_target
          option: none
