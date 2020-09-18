import sys

from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext

import sys
from awsglue.utils import getResolvedOptions

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'BUCKET'])

bucket = args["BUCKET"]
run_id = args["JOB_RUN_ID"]

glueContext = GlueContext(SparkContext.getOrCreate())

sample1 = glueContext.create_dynamic_frame.from_catalog(
    name_space="public",
    table_name="weather_nyc",
    additional_options={"mergeSchema": "true"}
    )


print(sample1.count())


output_path = "s3://{bucket}/glue/jobs/{run_id}/output/sample".format(bucket=bucket, run_id=run_id)

(sample1.toDF()
 .repartition(1)
 .write
 .format("parquet")
 .option("SaveMode.Overwrite", "overwrite")
 .save(output_path)
 )
