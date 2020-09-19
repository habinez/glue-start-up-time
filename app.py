#!/usr/bin/env python3

from aws_cdk import core

from startup.startup_stack import StartupStack

app = core.App()
StartupStack(app, "startup")

core.Tag.add(app, "Owner", "self")
core.Tag.add(app, "Purpose", "demo")
core.Tag.add(app, "Charge", "credits")

app.synth()
