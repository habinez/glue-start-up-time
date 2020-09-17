#!/usr/bin/env python3

from aws_cdk import core

from startup.startup_stack import StartupStack

#env = core.Environment(account="024008546344", region="us-east-2")

app = core.App()
StartupStack(app, "startup")

app.synth()
