#!/usr/bin/env python3

import aws_cdk as cdk
from ai_apartment_search.waf_stack import WafStack
from ai_apartment_search.networking_stack import NetworkingStack
from ai_apartment_search.database_stack import DatabaseStack


app = cdk.App()
WafStack(app, 'WafStack')
NetworkingStack(app, 'NetworkingStack')
DatabaseStack(app, 'DatabaseStack')

# FrontendStack(app, "FrontendStack")

app.synth()
