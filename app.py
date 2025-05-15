#!/usr/bin/env python3

import aws_cdk as cdk
from ai_apartment_search.waf_stack import WafStack
from ai_apartment_search.networking_stack import NetworkingStack


app = cdk.App()
WafStack(app, 'WafStack')
NetworkingStack(app, 'NetworkingStack')


# FrontendStack(app, "FrontendStack")

app.synth()
