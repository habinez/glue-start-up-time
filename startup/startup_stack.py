import os

from aws_cdk import aws_glue
from aws_cdk import aws_iam as iam
from aws_cdk import core, aws_s3, aws_s3_assets


class StartupStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        bucket = aws_s3.Bucket(self, "demo-bucket-glue-sha", bucket_name="demo-bucket-glue-sha")

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

        glue_job = aws_glue.CfnJob(
            self, "test_job",
            role=glue_job_role.role_arn,
            command=aws_glue.CfnJob.JobCommandProperty(
                name='glueetl',
                script_location=glue_script.s3_object_url
            ),
            default_arguments={
                "--continuous-log-logGroup": "aws_cloudwatch_log_group.example.name",
                "--enable-continuous-cloudwatch-log": False,
                "--continuous-log-logStreamPrefix" : "demo",
                "--enable-continuous-log-filter": False,
                "--enable-metrics": "",
                "--TempDir": f"{bucket.bucket_name}/glue/tmp"
            },
            glue_version="2.0",
            log_uri=f"{bucket.bucket_name}/glue/logs",
            execution_property=aws_glue.CfnJob.ExecutionPropertyProperty(
                max_concurrent_runs=100
            ),
            max_capacity=100,
            tags={
                "Owner": "self",
                "Purpose": "demo",
                "Charge": "credits"
            }

        )
