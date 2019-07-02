import requests
import slack
import os
import re
import ipaddress

SLACK_TOKEN = os.environ["SLACK_API_TOKEN"]
SLACK_CHANNEL = os.environ["SLACK_CHANNEL"]

vt_api_key = os.environ["VT_API_KEY"]
base_url = "https://www.virustotal.com"


def vt_domain_get(domain):
    domain = domain.lower()
    path = "/vtapi/v2/domain/report?apikey={}&domain={}".format(vt_api_key, domain)
    url = base_url + path
    vt_results = requests.get(url).json()
    return vt_results

def vt_hash_get(hash):
    path = "/vtapi/v2/file/report?apikey={}&resource={}".format(vt_api_key, hash)
    url = base_url + path
    vt_results = requests.get(url).json()
    return vt_results

def vt_ip_get(ip):
    path = "/vtapi/v2/ip-address/report?apikey={}&ip={}".format(vt_api_key, ip)
    url = base_url + path
    vt_results = requests.get(url).json()
    return vt_results


def handler(event, context):
    try:
        channel = event['body']['channel_id']
        indicator = event['body']['text']
        if not indicator:
            return "Please enter an input"

        client = slack.WebClient(token=os.environ["SLACK_API_TOKEN"])

        ## check if value is an IP
        ip_check = re.compile("^^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
        ip_test = bool(ip_check.match(indicator))

        ## check if value is a domain
        domain_check = re.compile("^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$")
        domain_test = bool(domain_check.match(indicator))

        ## make VT call based on the indicator type
        if ip_test:
            vt_results = vt_ip_get(indicator)
        elif domain_test:
            vt_results = vt_domain_get(indicator)
        else:
            vt_results = vt_hash_get(indicator)

        ## validated results
        if not vt_results:
            return "No Results for indicator {}".format(indicator)

        ## create slack messages and send
        first_item = True
        for result in vt_results:
            message = ""
            message += "```{} -> {}: {}```\n\n".format(indicator, result, vt_results[result])

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
        response = client.chat_postMessage(channel=os.environ["SLACK_CHANNEL"], text=str(e))
        return "Error occurred, message sent to administrator"
