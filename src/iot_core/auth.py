from awscrt import auth
import boto3
import uuid

def get_cred_provider_with_assumed_role(role_arn, role_session_name=None):
    if not role_arn:
        print('the assumed role arn must be specified')
        exit(-1)

    sts = boto3.client('sts')

    res = sts.assume_role(RoleArn=role_arn, RoleSessionName=role_session_name or str(uuid.uuid4()))

    access_key = res['Credentials']['AccessKeyId']
    access_secret = res['Credentials']['SecretAccessKey']
    access_token = res['Credentials']['SessionToken']
    
    return auth.AwsCredentialsProvider.new_static(access_key_id=access_key, secret_access_key=access_secret, session_token=access_token)