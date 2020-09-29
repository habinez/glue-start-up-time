#!/usr/bin/env python3

import os
from aws_cdk import core


from startup.startup_stack import StartupStack

app = core.App()
StartupStack(app, "startup",
             env=core.Environment(account=os.environ["CDK_DEFAULT_ACCOUNT"],
                                  region=os.environ["CDK_DEFAULT_REGION"]
                                  )
             )

core.Tag.add(app, "Owner", "self")
core.Tag.add(app, "Purpose", "demo")
core.Tag.add(app, "Charge", "credits")

app.synth()
