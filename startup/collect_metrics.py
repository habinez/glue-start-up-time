from json import dumps, dump, load, loads
import pandas as pd
import pdb
import logging 
import boto3
import botostubs

logger=logging.getLogger()

glue_client = boto3.client("glue")

paginator = glue_client.get_paginator('get_job_runs')
page_iterator = paginator.paginate(JobName='demo-pyspark-job')

runs = list()
for page in page_iterator:
    for run in page['JobRuns']:
        #if run['JobRunState'] == 'STOPPED' :# and run['NumberOfWorkers'] != 2:
        run.pop('Attempt')
        run.pop('LogGroupName')
        run.pop('PredecessorRuns')
        runs.append(run)
        # if run['NumberOfWorkers'] != 2:
        #     print(run['AllocatedCapacity'], run['MaxCapacity'], run['NumberOfWorkers'])

df = pd.DataFrame(data = runs)
print(df.columns)
df.to_csv("glue_job_runs.csv", index=False)


