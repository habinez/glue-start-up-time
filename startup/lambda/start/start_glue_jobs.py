import json
import logging
import os
from random import randint

from boto3 import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    glue_client = client("glue")
    job_runs = event["job_runs"]
    job_name = os.environ["JOB_NAME"]
    started_runs = list()
    job_runs = int(job_runs)

    if job_runs > 50:
        job_runs = 50
    for _ in range(job_runs):
        try:
            response = glue_client.start_job_run(
                JobName=job_name,
                MaxCapacity=randint(2, job_runs)
            )
            logger.info(json.dumps(response, default=str))
            started_runs.append(response['JobRunId'])

        except Exception as exception:
            logger.error(exception)
            raise exception

    return json.dumps(dict(job_name=job_name,run_ids=started_runs))

#
# if __name__ == "__main__":
#     handler(event={dict(job_runs="13")}, context={}):
