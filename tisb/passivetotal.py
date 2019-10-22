import requests
import slack
import json
import os
import urllib.parse

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

username = os.environ["PASSIVETOTAL_USERNAME"]
key = os.environ["PASSIVETOTAL_APIKEY"]
auth = (username, key)
base_url = "https://api.passivetotal.org"


def passivetotal_get(indicator):
    path = "/v2/dns/passive"
    url = base_url + path
    data = {"query": indicator}

    pdns_results = requests.get(url, auth=auth, json=data).json()
    return pdns_results


def handler(indicator, channel):
    client = slack.WebClient(token=SLACK_API_TOKEN)
    pdns_results = passivetotal_get(indicator)

    if not pdns_results.get("results", None):
        client.chat_postMessage(
            channel=channel, text=f"No Results for indicator {indicator}")

    first_item = True
    for result in pdns_results.get("results"):
        message = ""
        for k, v in result.items():
            message += f"```{k}: {v}```\n\n"
        if first_item:
            response = client.chat_postMessage(channel=channel, text=message)
            thread_ts = response["ts"]
            first_item = False

        response = client.chat_postMessage(
            channel=channel, text=message, thread_ts=thread_ts
        )

    return
