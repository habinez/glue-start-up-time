import os

from aws_cdk import (
    core,
    aws_s3,
    aws_s3_assets,
    aws_glue,
    aws_events,
    aws_iam as iam,
    aws_lambda as lambda_,
    aws_events_targets,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks
)


class StartupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        # remove the name to avoid collision
        #
        # #bucket_name = "demo-bucket-glue-sha"

        bucket = aws_s3.Bucket(self, "demo-bucket-glue-sha")
        bucket_name = bucket.bucket_name
        dir_name = os.path.dirname(__file__)
        # dir_name = os.path.abspath(os.path.join(dir_name, os.pardir))

        glue_script = aws_s3_assets.Asset(self,
                                          "glue-script",
                                          path=os.path.join(dir_name, "jobs", "glue_job_example.py")
                                          )
        policy_statement = iam.PolicyStatement(
            actions=['logs:*',
                     "events:*",
                     'cloudwatch:*',
                     's3:*',
                     'ec2:*',
                     'iam:*',
                     'glue:*'
                     ]
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

        aws_glue.CfnCrawler(
            self, "weather-nyc-crawler",
            role=glue_job_role.role_arn,
            database_name=db.database_input.name,
            table_prefix="",
            targets={"s3Targets": [
                {
                    "path": "s3://conco-aws-athena/snowflake-workshop-lab/weather-nyc"
                }
            ]
            }
        )

        glue_job = aws_glue.CfnJob(
            self, "demo-pyspark-job",
            name="demo-pyspark-job",
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
                max_concurrent_runs=50
            ),
            max_capacity=2,
            tags={
                "Owner": "self",
                "Purpose": "demo",
                "Charge": "credits"
            }

        )

        lambda_execution_role = iam.Role(
            self,
            'LambdaExecutionRole',
            role_name="LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com')
        )
        lambda_execution_policy_statement = iam.PolicyStatement(
            actions=['lambda:InvokeFunction',
                     "logs:CreateLogGroup",
                     "logs:CreateLogStream",
                     "logs:PutLogEvents",
                     "states:StartExecution",
                     "events:*",
                     "glue:*"
                     ]
        )
        lambda_execution_policy_statement.add_all_resources()

        lambda_execution_role.add_to_policy(lambda_execution_policy_statement)

        stop_job_function = lambda_.Function(
            self, "terminate-glue-job-run",
            function_name="demo-stop-glue-job-runs",
            code=lambda_.Code.from_asset(os.path.join(dir_name, "lambda", "stop")),
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="terminate_job_run.handler",
            role=lambda_execution_role
        )

        start_glue_job_function = lambda_.Function(
            self, "start-glue-job",
            function_name="demo-start-glue-job",
            code=lambda_.Code.from_asset(os.path.join(dir_name, "lambda", "start")),
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="start_glue_jobs.handler",
            role=lambda_execution_role,
            environment=dict(JOB_NAME=glue_job.name)
        )

        start_job_task = tasks.LambdaInvoke(
            self,
            "Start Glue Jobs",
            lambda_function=start_glue_job_function,
            result_path="$",
            output_path="$.Payload",
            #result_selector= {"Payload.$": "States.StringToJson($.Payload)"}
            payload=sfn.TaskInput.from_data_at("$")
        )

        start_jobs_state = sfn.Map(self, "Run Jobs",
                                   input_path="$",
                                   items_path="$.capacities",
                                   max_concurrency=5,
                                   parameters={
                                       "capacity.$": "$$.Map.Item.Value",
                                       "glue_job_name.$": "$.job_name"
                                   }
                                   )
        start_jobs_state.iterator(start_job_task)

        wait_time = sfn.WaitTime.duration(core.Duration.seconds(30))
        wait_state = sfn.Wait(self, "Wait 30 Sec", time=wait_time)

        stop_job_state = tasks.LambdaInvoke(
            self,
            "Stop Glue Jobs",
            lambda_function=stop_job_function,
            payload=sfn.TaskInput.from_data_at("$")
        )

        start_jobs_state.next(wait_state)
        wait_state.next(stop_job_state)
        sfn_policy_statement = iam.PolicyStatement(
            actions=["logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                     'cloudwatch:*',
                     'lambda:InvokeFunction'
                     ]
        )

        sfn_policy_statement.add_all_resources()

        sfn_role = iam.Role(
            self,
            'StepFunctionRole',
            assumed_by=iam.ServicePrincipal('states.amazonaws.com')
        )
        sfn_role.add_to_policy(sfn_policy_statement)

        state_machine = sfn.StateMachine(self, "StateMachine",
                                         definition=start_jobs_state,
                                         state_machine_name="orchestrator",
                                         role=sfn_role)

        core.CfnOutput(self,
                       "state machine arn",
                       value=state_machine.state_machine_arn
                       )

        aws_events.Rule(
            self,
            "glue-job-start-event",
            enabled=False,
            event_pattern=aws_events.EventPattern(
                source=["aws.glue"],
                detail_type=["Glue Job Run Status"],
                detail={
                    "state": [
                        "RUNNING"
                    ],
                    "jobName": [
                        glue_job.name
                    ]
                }
            ),
            targets=[aws_events_targets.LambdaFunction(stop_job_function)]
        )

        lambda_.Function(
            self, "demo-start-state-machine",
            function_name="demo-start-state-machine",
            code=lambda_.Code.from_asset(os.path.join(dir_name, "lambda", "start")),
            runtime=lambda_.Runtime.PYTHON_3_7,
            handler="start_state_machine.handler",
            role=lambda_execution_role,
            environment=dict(JOB_NAME=glue_job.name,
                             STATE_MACHINE_ARN=state_machine.state_machine_arn
                             )
        )
