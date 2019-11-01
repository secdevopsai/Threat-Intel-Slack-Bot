import os
import json
from .aws import LAMBDA

PASSIVETOTAL_LAMBDA_FUNCTION = os.environ["PASSIVETOTAL_LAMBDA_FUNCTION"]


def handler(*, channel, indicator):
    response = LAMBDA.invoke(
        FunctionName=PASSIVETOTAL_LAMBDA_FUNCTION,
        InvocationType='Event',
        Payload=json.dumps({"indicator": indicator, "channel": channel})
    )
    status = {"statusCode": 200, "body": "Processing Request."}

    return status
