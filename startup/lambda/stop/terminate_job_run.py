import json
import logging

from boto3 import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    glue_client = client("glue")
    logger.info(json.dumps(event, default=str, indent=4))
    glue_job_name = str()
    ids = list()
    for e in event:
        glue_job_name = e.get("glue_job_name")
        ids.append(e.get("job_run_id"))

    if glue_job_name:
        try:
            response = glue_client.batch_stop_job_run(
                    JobName=glue_job_name,
                    JobRunIds= ids
                )
            return json.dumps(response, default=str, indent=4)

        except Exception as exception:
            return exception.args
