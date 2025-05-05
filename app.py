#!/usr/bin/env python3

import aws_cdk as cdk
from ai_apartment_search.frontend_stack import FrontendStack


app = cdk.App()

# FrontendStack(app, "FrontendStack")

app.synth()
