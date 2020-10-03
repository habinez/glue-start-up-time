import json
import logging
import os
from random import randint

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    client = boto3.client("stepfunctions")
    runs = randint(7, 14) #int(event["job_runs"])
    job_name = os.environ["JOB_NAME"]
    state_machine_arn = os.environ["STATE_MACHINE_ARN"]
    capacities = [randint(2, 50) for _ in range(runs)]
    try:
        response = client.start_execution(
            stateMachineArn=state_machine_arn,
            name=f"run-{runs}-glue-jobs-{randint(1, 1000_0)}",
            input=json.dumps(dict(job_name=job_name, capacities=capacities))
        )
        return json.dumps(response, default=str)

    except Exception as exception:
        logger.error(exception)
        raise exception
        return exception


