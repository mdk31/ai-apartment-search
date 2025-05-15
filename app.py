#!/usr/bin/env python3

import aws_cdk as cdk
from ai_apartment_search.waf_stack import WafStack


app = cdk.App()
WafStack(app, 'WafStack')

# FrontendStack(app, "FrontendStack")

app.synth()
