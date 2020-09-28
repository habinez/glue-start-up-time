import json
import os
from boto3 import client
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    glue_client = client("glue")
    job_runs = event["job_runs"]
    job_name = os.environ["JOB_NAME"]
    started_runs = list()
    for _ in range(int(job_runs)):
        try:
            response = glue_client.start_job_run(JobName=job_name)
            logger.info(json.dumps(response, default=str))
            started_runs.append(response['JobRunId'])

        except Exception as exception:
            logger.error(exception)

    return json.dumps(started_runs)


# if  __name__ == "__main__" :
#     handler(event={}, context{}):