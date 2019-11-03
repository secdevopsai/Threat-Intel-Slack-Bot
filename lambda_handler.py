

def handle_slash_message(event, context):
    from urllib.parse import parse_qs
    from tisb.slashmessage import handler as slash_handler

    slash_message = {
        k: v[0] for k, v in parse_qs(event["body"]).items()
    }
    channel = slash_message["channel_id"]
    indicator = slash_message.get("text", "")
    return slash_handler(indicator=indicator, channel=channel)


def handle_passivetotal(event, context):
    from tisb.passivetotal import handler as passivetotal_handler
    return passivetotal_handler(**event)


def handle_virustotal(event, context):
    from tisb.virustotal import handler as virustotal_handler
    return virustotal_handler(**event)
