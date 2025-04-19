import json
import os
import boto3

waf = boto3.client('wafv2')
WEB_ACL_NAME = os.getenv('WEB_ACL_NAME')
WEB_ACL_ID = os.getenv('WEB_ACL_ID')
WEB_ACL_SCOPE = os.getenv('WEB_ACL_SCOPE')

def lambda_handler(event, context):

    response = waf.get_webacl(
        Name=WEB_ACL_NAME,
        Scope=WEB_ACL_SCOPE,
        Id=WEB_ACL_ID
    )

    web_acl = response['WebACL']
    rules = web_acl['Rules']
    lock_token = web_acl['LockToken']

    for rule in rules:
        if rule['Name'] == 'KillSwitch':
            rule['Action'] = {'Block': {}}
            break

    waf.update_web_acl(
        Name=WEB_ACL_NAME,
        Scope=WEB_ACL_SCOPE,
        Id=WEB_ACL_ID,
        Rules=rules,
        LockToken=lock_token,
        DefaultAction=web_acl['DefaultAction'],
        VisibilityConfig=web_acl['VisibilityConfig'],
        Description=web_acl.get('Description', '')
    )
    
    