from send_req import *
def _send_single_req():
    endpoint = "https://etewv9yzp0.execute-api.us-west-2.amazonaws.com/Prod/gdl-api-gateway-to-sqs"
    params_list = [
        {
            "command": '"https://www.artstation.com/sleeping_bird"',
            "s3_uri": "s3://dataset-ingested/gallery-dl/",
        }
    ]
    send_post_requests_at_rate(endpoint, params_list, 2)