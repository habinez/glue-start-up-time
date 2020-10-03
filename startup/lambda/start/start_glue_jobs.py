import json
import logging
import os
from random import randint

from boto3 import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    logger.info(json.dumps(event, default=str, indent=4))
    glue_client = client("glue")
    max_capacity = int(event["capacity"])
    glue_job_name = event["glue_job_name"]

    try:
        response = glue_client.start_job_run(
            JobName=glue_job_name,
            AllocatedCapacity = max_capacity    
        )
        output = dict(glue_job_name=glue_job_name,
                      job_run_id=response['JobRunId']
                      )
        return json.dumps(output, default=str)

    except Exception as exception:
        logger.error(exception)
        raise exception

