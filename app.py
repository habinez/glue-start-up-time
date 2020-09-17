#!/usr/bin/env python3

from aws_cdk import core

from startup.startup_stack import StartupStack


app = core.App()
StartupStack(app, "startup")

app.synth()
