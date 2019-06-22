import requests
import slack
import json
import os
import urllib.parse

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
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


def handler(event, context):
    try:
        slash_message = {
            k: v[0] for k, v in urllib.parse.parse_qs(event["body"]).items()
        }
        channel = slash_message["channel_id"]
        indicator = slash_message.get("text")
        if not indicator:
            return "Please enter an input"

        client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])
        pdns_results = passivetotal_get(indicator)

        if not pdns_results.get("results", None):
            return "No Results for indicator {}".format(indicator)

        first_item = True
        for result in pdns_results.get("results"):
            message = ""
            for k, v in result.items():
                message += "```{}: {}```\n\n".format(k, v)
            if first_item:
                response = client.chat_postMessage(channel=channel, text=message)
                thread_ts = response["ts"]
                first_item = False

            response = client.chat_postMessage(
                channel=channel, text=message, thread_ts=thread_ts
            )

        status = {"statusCode": 200, "body": "Done"}

        return status
    except Exception as e:
        client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])
        response = client.chat_postMessage(channel=SLACK_CHANNEL, text=str(e))
        return "Error occurred, message sent to administrator"

