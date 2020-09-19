import json
import logging

from boto3 import client

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    glue_client = client("glue")
    logger.info(json.dumps(event, default=str, indent=4))
    logger.info(json.dumps(context, default=str, indent=4))
    if "detail" in event.keys():
        run_detail = event["detail"]
        logger.info(json.dumps(run_detail, default=str))
        if 'jobName' in run_detail.keys():
            if run_detail['state'] == 'RUNNING':
                response = glue_client.batch_stop_job_run(
                    JobName=run_detail['jobName'],
                    JobRunIds=[
                        run_detail['jobRunId']
                    ]
                )
                return json.dumps(response, default=str, indent=4)
            else:
                logger.critical(f"run_detail['jobName'], run_detail['jobRunId'] is not running")
                return json.dumps(run_detail, default=str, indent=4)

    logger.error("Wrong Event")
    logger.error(json.dumps(event, default=str, indent=4))
    return json.dumps(event, default=str, indent=4)


with open("sample_event.json") as e_file:
    event = json.load(e_file)
    print(handler(event, None))