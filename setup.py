import setuptools

with open("README.md") as fp:
    long_description = fp.read()

setuptools.setup(
    name="startup",
    version="0.0.1",

    description="An empty CDK Python app",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="author",

    package_dir={"": "startup"},
    packages=setuptools.find_packages(where="startup"),

    install_requires=[
        "aws-cdk.core>=1.64.0",
        "aws_cdk.aws_events",
        "aws_cdk.aws_glue",
        "aws_cdk.aws_s3",
        "aws_cdk.aws_s3_assets",
        "aws_cdk.aws_lambda",
        "aws_cdk.aws_iam",
        "aws_cdk.aws_stepfunctions",
        "aws_cdk.aws_stepfunctions_tasks",
        "aws_cdk.aws_events",
        "aws_cdk.aws_events_targets",
        "boto3",
        "awscli"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: Apache Software License",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
