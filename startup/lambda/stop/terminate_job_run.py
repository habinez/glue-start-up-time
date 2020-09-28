import json
import logging

from boto3 import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    glue_client = client("glue")
    logger.info(json.dumps(event, default=str, indent=4))
    if 'job_name' in event.keys():
        try:
            response = glue_client.batch_stop_job_run(
                    JobName=event['job_name'],
                    JobRunIds=event['run_ids']
                )
            return json.dumps(response, default=str, indent=4)

        except Exception as exception:
            return json.dumps(exception, default=str)


# with open("sample_event.json") as e_file:
#     event = json.load(e_file)
#     print(handler(event, None))