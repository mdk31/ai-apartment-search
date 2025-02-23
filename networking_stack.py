from aws_cdk import core
import aws_cdk.aws_ec2 as ec2

class NetworkingStack(core.Stack):
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create a VPC
        self.vpc = ec2.Vpc(self, "AppVpc", max_azs=2)

        # Security Group
        self.security_group = ec2.SecurityGroup(
            self, "AppSG", vpc=self.vpc,
            description=""
        )

        self.security_group.add_ingress_rule(
            ec2.Peer.any_ipv4(),  # Later restrict this to EC2/Lambda IPs
            ec2.Port.tcp(5432),
            "Allow PostgreSQL access from within the VPC"
        )
