import aws_cdk as cdk
import os
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins
)
from constructs import Construct

# TODO: write index document
class FrontendStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        frontend_bucket = s3.Bucket(
            self, 'FrontendBucket',
            website_error_document='index.html',
            website_index_document='index.html',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            auto_delete_objects=True
        )

        distribution =cloudfront.Distribution(
            self, 'FrontendDistribution',
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin(frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS
            )
        )

        s3_deployment.BucketDeployment(
            self, 'FrontendDeployment',
            destination_bucket=frontend_bucket,
            sources=[s3_deployment.Source.asset("frontend/build")],
            retain_on_delete=False
        )

        cdk.CfnOutput(
            self, "CloudFrontURL",
            value=distribution.domain_name,
            description="URL of the deployed frontend"
        )
