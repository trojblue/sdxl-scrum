import requests
import time
import json

def send_post_request(endpoint, params):
    try:
        response = requests.post(endpoint, data=json.dumps(params), headers={'Content-Type': 'application/json'})
        response.raise_for_status()  # Will raise exception if status is 4xx, 5xx
        return response.json()
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
    for params in params_list:
        send_post_request(endpoint, params)
        time.sleep(interval)


if __name__ == '__main__':
    endpoint = 'http://localhost:5000/echo'
    params_list = [{'name': 'Alice'}, {'name': 'Bob'}, {'name': 'Charlie'}]
    send_post_requests_at_rate(endpoint, params_list, 2)