import os

from aws_cdk import aws_glue
from aws_cdk import aws_iam as iam
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from aws_cdk import core, aws_s3, aws_s3_assets


class StartupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # remove the name to avoid collision
        #
        # #bucket_name = "demo-bucket-glue-sha"

        bucket = aws_s3.Bucket(self, "demo-bucket-glue-sha")
        bucket_name = bucket.bucket_name
        dirname = os.path.dirname(__file__)

        glue_script = aws_s3_assets.Asset(self,
                                          "glue-script",
                                          path=os.path.join(dirname, "glue_job_example.py")
                                          )
        policy_statement = iam.PolicyStatement(
            actions=['logs:*', 's3:*', 'ec2:*', 'iam:*', 'cloudwatch:*', 'glue:*']
        )

        policy_statement.add_all_resources()

        glue_job_role = iam.Role(
            self,
            'Glue-Job-Role',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com')
        )
        glue_job_role.add_to_policy(policy_statement)

        db = aws_glue.CfnDatabase(self, "db",
                                  catalog_id=core.Aws.ACCOUNT_ID,
                                  database_input=aws_glue.CfnDatabase.DatabaseInputProperty(
                                      name="public"
                                  )

                                  )

        registrator_crawler = aws_glue.CfnCrawler(
            self, "weather-nyc-crawler",
            role=glue_job_role.role_arn,
            database_name=db.database_input.name,
            table_prefix="",
            targets={"s3Targets": [
                {
                    "path": "s3://snowflake-workshop-lab/weather-nyc"
                }
            ]
            }
        )

        glue_job = aws_glue.CfnJob(
            self, "demo-pyspark-job",
            role=glue_job_role.role_arn,
            command=aws_glue.CfnJob.JobCommandProperty(
                name='glueetl',
                script_location=glue_script.s3_object_url
            ),
            default_arguments={
                # "--continuous-log-logGroup": "aws_glue.demo.job.glue",
                "--enable-continuous-cloudwatch-log": True,
                # "--continuous-log-logStreamPrefix": "pyspark",
                "--enable-continuous-log-filter": False,
                "--enable-metrics": "",
                "--TempDir": f"s3://{bucket_name}/glue/tmp",
                "--BUCKET": bucket_name
            },
            glue_version="2.0",
            log_uri=f"s3://{bucket_name}/glue/logs",
            execution_property=aws_glue.CfnJob.ExecutionPropertyProperty(
                max_concurrent_runs=100
            ),
            max_capacity=2,
            tags={
                "Owner": "self",
                "Purpose": "demo",
                "Charge": "credits"
            }

        )

        start_job_task = tasks.GlueStartJobRun(
            self,
            "Start Job",
            glue_job_name=glue_job.name,
            arguments=sfn.TaskInput.from_object({
                "AllocatedCapacity": "$.num_workers"
            })
        )
        start_job_task._parameters.update({
                "AllocatedCapacity": "$.num_workers"
            })

        wait = sfn.WaitTime.duration(core.Duration.minutes(1))

        wait = sfn.Wait(self, "wait 1 min", time=wait)
        terminate = sfn.Pass(self, "Terminate Job Run")
        wait.next(terminate)
        start_job_task.next(wait)
        startState = sfn.Map(self, "Run Jobs",
                             input_path="$",
                             items_path="$.executions",
                             max_concurrency=0
                             )
        startState.iterator(start_job_task)

        sfn.StateMachine(self, "StateMachine", definition=startState)
