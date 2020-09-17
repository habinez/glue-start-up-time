import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

glueContext = GlueContext(SparkContext.getOrCreate())

acount_a_table = glueContext.create_dynamic_frame.from_catalog(
             database="oss-accounta",
             table_name="table-in-account-a",
             catalog_id=None
             )

acount_a_table.printSchema()