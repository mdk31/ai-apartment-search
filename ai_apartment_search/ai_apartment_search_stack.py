from aws_cdk import (
    Stack,
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
    aws_ssm as ssm,
    aws_logs as logs
    # core
)

from constructs import Construct

class AiApartmentSearchStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        domain_name = "yourcustomdomain.com"
        hosted_zone = route53.HostedZone.from_lookup(self, "HostedZone", domain_name=domain_name)

        # certificate = acm.Certificate(
        #     self, "SiteCertificate",
        #     domain_name=domain_name,
        #     validation=acm.CertificateValidation.from_dns(hosted_zone)
        # )

        # db_secret = secretsmanager.Secret.from_secret_name_v2(self, "DBSecret", "PostgresDB")
        # db_host = ssm.StringParameter.from_string_parameter_name(self, "DBHost", "/rental-app/db-host").string_value

        # log_group = logs.LogGroup(self, "APIGatewayLogGroup")

        # frontend_bucket = s3.Bucket(
        #     self, "FrontendBucket",
        #     website_index_document="index.html",
        #     public_read_access=True,
        #     removal_policy=core.RemovalPolicy.DESTROY
        # )

        # frontend_distribution = cloudfront.Distribution(
        #     self, "FrontendDistribution",
        #     default_behavior=cloudfront.BehaviorOptions(
        #         origin=origins.S3Origin(frontend_bucket),
        #         viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
        #     ),
        #     domain_names=[domain_name],
        #     certificate=certificate
        # )

        # route53.ARecord(
        #     self, "FrontendAlias",
        #     zone=hosted_zone,
        #     target=route53.RecordTarget.from_alias(targets.CloudFrontTarget(frontend_distribution))
        # )

        # openai_secret = secretsmanager.Secret.from_secret_name_v2(self, "OpenAISecret", "OpenAISecret")

        # openai_lambda = _lambda.Function(
        #     self, "OpenAIFunc",
        #     runtime=_lambda.Runtime.PYTHON_3_9,
        #     handler="openai_handler.lambda_handler",
        #     code=_lambda.Code.from_asset("lambda"),
        #     environment={
        #         "OPENAI_SECRET_ARN": openai_secret.secret_arn
        #     }
        # )
        # openai_secret.grant_read(openai_lambda)

        # api_gateway = apigw.LambdaRestApi(
        #     self, "APIGateway",
        #     handler=openai_lambda,
        #     proxy=True,
        #     deploy_options=apigw.StageOptions(
        #         logging_level=apigw.MethodLoggingLevel.ERROR,
        #         access_log_destination=apigw.LogGroupLogDestination(log_group),
        #         access_log_format=apigw.AccessLogFormat.json_with_standard_fields()
        #     )
        # )

        # ssm.StringParameter(
        #     self, "OpenAIAPIURLParameter",
        #     parameter_name="/rental-app/openai-api-url",
        #     string_value=api_gateway.url
        # )

        # cluster = ecs.Cluster(self, "FargateCluster")

        # fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
        #     self, "FlaskAPI",
        #     cluster=cluster,
        #     task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
        #         image=ecs.ContainerImage.from_registry(f"{core.Stack.of(self).account}.dkr.ecr.us-east-1.amazonaws.com/rental-flask-api:latest"),
        #         environment={
        #             "DB_SECRET_ARN": db_secret.secret_arn,
        #             "DB_HOST_PARAM": "/rental-app/db-host",
        #             "OPENAI_API_PARAM": "/rental-app/openai-api-url"
        #         }
        #     ),
        #     certificate=certificate,
        #     domain_name=f"api.{domain_name}",
        #     domain_zone=hosted_zone,
        #     desired_count=1
        # )

        # route53.ARecord(
        #     self, "ApiAlias",
        #     zone=hosted_zone,
        #     target=route53.RecordTarget.from_alias(targets.LoadBalancerTarget(fargate_service.load_balancer))
        # )

        # core.CfnOutput(self, "FrontendURL", value=f"https://{domain_name}")
        # core.CfnOutput(self, "FlaskAPIEndpoint", value=f"https://api.{domain_name}")
        # core.CfnOutput(self, "OpenAIAPIURL", value=api_gateway.url)
        # core.CfnOutput(self, "DBHost", value=db_host)
