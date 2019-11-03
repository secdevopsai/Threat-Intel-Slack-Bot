from tisb import passivetotal

VALID_RESULT = {
    "totalRecords": 200,
    "firstSeen": "2009-09-01 21:40:49",
    "lastSeen": "2017-04-11 22:42:20",
    "results": [
        {
            "firstSeen": "2011-03-08 07:38:51",
            "resolveType": "ip",
            "value": "passivetotal.org",
            "recordHash": "55e1cabe4667d8bdb6349f9bef7c9bb46e16d05662e535626d5662f2b02572b2",
            "lastSeen": "2011-03-08 07:38:51",
            "resolve": "52.8.192.151",
            "source": [
                "kaspersky"
            ],
            "recordType": "A",
            "collected": "2017-04-11 22:42:19"
        },
    ],
    "queryType": "domain",
    "pager": None,
    "queryValue": "passivetotal.org"
}


EMPTY_RESULT = {
    "firstSeen": None,
    "lastSeen": None,
    "pager": None,
    "queryType": "domain",
    "queryValue": "example.org",
    "results": [],
    "totalRecords": 0
}


def test_message_formatting_valid_results():
    results = VALID_RESULT
    text, attachments = passivetotal.format_message_for_slack(
        results, "example.org")
    assert "Results found" in text
    assert attachments


def test_message_formatting_no_results():
    results = EMPTY_RESULT
    text, attachments = passivetotal.format_message_for_slack(
        results, "example.org")
    assert "No results" in text
    assert not attachments
