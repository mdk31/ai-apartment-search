from constructs import Construct

from aws_cdk import (
    core,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_apigateway as apigw,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_certificatemanager as acm,
    aws_lambda as _lambda,
    aws_secretsmanager as secretsmanager,
    Stack
)

class AiApartmentSearchStack(Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        domain_name = "aiapartmentsnyc.com"
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)


app = core.App()
AiApartmentSearchStack(app, "RentalAppStack")
app.synth()


