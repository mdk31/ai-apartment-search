import json
import os
import boto3

waf = boto3.client('wafv2')
WEB_ACL_NAME = os.getenv('WEB_ACL_NAME')
WEB_ACL_ID = os.getenv('WEB_ACL_ID')
WEB_ACL_SCOPE = os.getenv('WEB_ACL_SCOPE')

def lambda_handler(event, context):

    if "Records" in event and event["Records"][0].get("EventSource") == "aws:sns":
        mode = "activate"
    else:
        mode = event.get("mode", "toggle")

    response = waf.get_webacl(
        Name=WEB_ACL_NAME,
        Scope=WEB_ACL_SCOPE,
        Id=WEB_ACL_ID
    )

    web_acl = response['WebACL']
    rules = web_acl['Rules']
    lock_token = web_acl['LockToken']

    updated = False

    for rule in rules:
        if rule["Name"] == 'KillSwitch':
            current_action = list(rule["Action"].keys())[0]
            if mode == "activate" and current_action == "Block":
                rule["Action"] = {"Count": {}}
                updated = True
            elif mode == "deactivate" and current_action == "Count":
                rule["Action"] = {"Block": {}}
                updated = True
            else:
                print(f"Unexpected action: {rule['Action']}")
            break

    if not updated:
        raise Exception("KillSwitch not found")

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
    return {
        "statusCode": 200,
        "body": f"KillSwitch toggled successfully. Now: {rules[0]['Action']}"
        }
    
    