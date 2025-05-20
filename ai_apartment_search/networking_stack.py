import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_rds as rds,
    aws_iam as iam,
    aws_secretsmanager as secretsmanager
)
from constructs import Construct

class NetworkingStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
    
        vpc = ec2.Vpc(
            self, "AppVPC",
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='PrivateSubnet',
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
                )
            ]
        )

        db_security_group = ec2.SecurityGroup(
            self, "DBSecurityGroup",
            vpc=vpc,
            description="The security group for the PostgreSQL database"
        )

        lambda_security_group = ec2.SecurityGroup(
            self, "LambdaSecurityGroup",
            vpc=vpc,
            description="The security group for lambda functions to connect to the database"
        )

        db_security_group.add_ingress_rule(
            peer=lambda_security_group,
            connection=ec2.Port.POSTGRES,
            description='Allow the lambda to access the PostgresSQL DB'
        )

        cdk.CfnOutput(
            self, 'LambdaSecurityGroupID',
            value=lambda_security_group.security_group_id,
            description="The security group ID for lambda functions that need DB access")

        cdk.CfnOutput(
            self, 'DBSecurityGroupID',
            value=db_security_group.security_group_id,
            description="DB security group")

        cdk.CfnOutput(
            self, 'VPCID',
            value=vpc.vpc_id,
            description='The VPC ID where the DB is deployed'
        )

        

