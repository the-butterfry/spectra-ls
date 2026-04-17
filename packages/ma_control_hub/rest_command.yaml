ma_api_command:
  url: "{{ states('sensor.ma_api_url') }}"
  method: POST
  headers:
    Content-Type: "application/json"
    # NOTE: ma_ll_token should include the 'Bearer ' prefix.
    # Example in secrets.yaml: ma_ll_token: "Bearer <TOKEN>"
    Authorization: !secret ma_ll_token
  payload: "{{ payload }}"
  content_type: "application/json"
