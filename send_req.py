import requests
import time
import json
from tqdm import tqdm
from pathlib import Path
from unibox import UniLoader, UniLogger
import gradio as gr

logger = UniLogger("_data", file_suffix="sdxl_scrum")
data_loader = UniLoader(logger)

def load_txt(txt_path):
    return data_loader.load_txt(Path(txt_path))

def send_post_request(endpoint, params):
    try:
        response = requests.post(endpoint, data=json.dumps(params), headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Will raise exception if status is 4xx, 5xx
        json_response = response.json()
        print(json_response)  # print the response
        return json_response
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong", err)


def send_post_requests_at_rate(endpoint, params_list, qps):
    interval = 1.0 / qps if qps != 0 else 0
    for params in tqdm(params_list):  # Add tqdm for progress bar
        send_post_request(endpoint, params)
        time.sleep(interval)

def send_requests_from_ui(input_urls):
    endpoint = 'https://etewv9yzp0.execute-api.us-west-2.amazonaws.com/Prod/gdl-api-gateway-to-sqs'
    params_list = [{'command': url} for url in input_urls.split('\n')]
    send_post_requests_at_rate(endpoint, params_list, 2)


def _send_single_req():
    endpoint = 'https://etewv9yzp0.execute-api.us-west-2.amazonaws.com/Prod/gdl-api-gateway-to-sqs'
    params_list = [
        {'command': "\"https://www.artstation.com/sleeping_bird\"",
         "s3_uri": "s3://dataset-ingested/gallery-dl/"
         }
    ]
    send_post_requests_at_rate(endpoint, params_list, 2)


if __name__ == '__main__':
    # Gradio UI
    iface = gr.Interface(fn=send_requests_from_ui, inputs='text', outputs='text')
    iface.launch()

