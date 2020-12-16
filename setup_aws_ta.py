from os import path, mkdir, system
from src.utils import get_input


def setup_aws():
    home_path = path.expanduser('~')
    aws_dir_path = ''.join([home_path, '/.aws'])
    aws_cred_path = ''.join([home_path, '/.aws/credentials'])
    aws_conf_path = ''.join([home_path, '/.aws/config'])
    if not path.exists(aws_dir_path):
        mkdir(aws_dir_path)

    with open(aws_cred_path, 'w') as cred:
        with open(aws_conf_path, 'w') as conf:
            aws_key = get_input('enter aws access key id: ', lambda x: len(x)==20)
            aws_secret = get_input('enter aws secret access key: ', lambda x: len(x)==40)
            
            cred.writelines([
                f'[default]\n',
                f'aws_access_key_id = {aws_key}\n',
                f'aws_secret_access_key = {aws_secret}\n'
            ])

            conf.writelines([
                f'[default]\n',
                f'region = eu-west-1\n'
            ])
            
            cred.close()
            conf.close()


if __name__ == "__main__":
    setup_aws()
