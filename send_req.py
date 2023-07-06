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
        return json_response
    except requests.exceptions.HTTPError as errh:
        return f"Http Error: {errh}"
    except requests.exceptions.ConnectionError as errc:
        return f"Error Connecting: {errc}"
    except requests.exceptions.Timeout as errt:
        return f"Timeout Error: {errt}"
    except requests.exceptions.RequestException as err:
        return f"Something went wrong: {err}"


def send_post_requests_at_rate(endpoint, params_list, qps):
    interval = 1.0 / qps if qps != 0 else 0
    responses = []
    for params in tqdm(params_list):  # Add tqdm for progress bar
        response = send_post_request(endpoint, params)
        responses.append(response)
        time.sleep(interval)
    return responses


def send_requests_from_ui(input_urls):
    endpoint = 'https://etewv9yzp0.execute-api.us-west-2.amazonaws.com/Prod/gdl-api-gateway-to-sqs'
    params_list = [{'command': url, "s3_uri": "s3://dataset-ingested/gallery-dl/"} for url in input_urls.split('\n')]
    responses = send_post_requests_at_rate(endpoint, params_list, 2)
    return "\n".join([f"Scraping request received; response: {res}" for res in responses])


if __name__ == "__main__":
    # Gradio UI
    iface = gr.Interface(fn=send_requests_from_ui, inputs="text", outputs="text")
    iface.launch()
