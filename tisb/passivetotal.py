import requests
import slack
import json
import os
import urllib.parse
from validators.domain import domain as domain_validator
from validators.url import url as url_validator
from validators.ip_address import ipv4 as ipv4_validator
from defang import defang

SLACK_API_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

username = os.environ["PASSIVETOTAL_USERNAME"]
key = os.environ["PASSIVETOTAL_APIKEY"]
auth = (username, key)
base_url = "https://api.passivetotal.org"


def handler(*, indicator, channel):
    pdns_results = passivetotal_get(indicator)
    text, attachments = format_message_for_slack(pdns_results, indicator)
    client = slack.WebClient(token=SLACK_API_TOKEN)
    client.chat_postMessage(channel=channel, text=text,
                            attachments=attachments)


def passivetotal_get(indicator):
    path = "/v2/dns/passive"
    url = base_url + path
    data = {"query": indicator}

    pdns_results = requests.get(url, auth=auth, json=data).json()
    return pdns_results


def format_message_for_slack(response, indicator):
    results = response.get("results", [])
    if not results:
        return f"No results for indicator {indicator}", None

    attachments = []
    for result in results:
        indicator = result['value']
        resolve = result['resolve']
        if (url_validator(indicator) or domain_validator(indicator)) and not ipv4_validator(indicator):
            indicator = defang(indicator, all_dots=True)
        if (url_validator(resolve) or domain_validator(resolve)) and not ipv4_validator(resolve):
            resolve = defang(resolve, all_dots=True)

        attachments.append({
            "color": "#36a64f",
            "author_name": f"PassiveTotal Results for {result['value']}",
            "author_link": f"https://community.riskiq.com/search/{result['value']}",
            "author_icon": "https://cdn.riskiq.com/wp-content/themes/riskiq/media/gradient-logo.png",
            "title": f"Query Results for {result['resolve']}",
            "title_link": f"https://community.riskiq.com/search/{result['resolve']}",
            "fields": [
                {
                    "title": "Resolve",
                    "value": f"{resolve}",
                    "short": False
                },
                {
                    "title": "Resolve Type",
                    "value": f"{result['resolveType']}",
                    "short": False
                },
                {
                    "title": "Record Type",
                    "value": f"{result['recordType']}",
                    "short": False
                },
                {
                    "title": "First Seen",
                    "value": f"{result['firstSeen']}",
                    "short": False
                },
                {
                    "title": "Last Seen",
                    "value": f"{result['lastSeen']}",
                    "short": False
                }
            ],
            "footer": "PassiveTotal",
            "footer_icon": "https://cdn.riskiq.com/wp-content/themes/riskiq/media/gradient-logo.png"
        })
    return f"Results found for `{result['value']}`", attachments
