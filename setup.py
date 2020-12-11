from os import path, mkdir, system

# the commands are setup specific to linux
COMMANDS = [
    'pip install awsiotsdk',
    'pip install boto3'
]


def get_input(instruction, validate=None, default=None):

    while True:
        result = input(instruction)

        if not result and default is not None:
            return default
        elif not result:
            print('default value is not supported for this option please manually type in one')
            continue

        if not validate:
            return result

        if not validate(result):
            print('the input is not valid')
            continue
        
        return result


def check_verbosity(verbosity):
    return verbosity in ['NoLogs', 'Fatal', 'Error', 'Warn', 'Info', 'Debug', 'Trace']


def setup_aws():
    
    if not path.exists('~/.aws/'):
        mkdir('~/.aws/')

    with open('~/.aws/credentials', 'w') as cred:
        with open('~/.aws/config', 'w') as conf:
            aws_key = get_input('enter aws access key id: ')
            aws_secret = get_input('enter aws secret access key: ')
            
            cred.writelines([
                f'[default]',
                f'aws_access_key_id = {aws_key}',
                f'aws_secret_access_key = {aws_secret}'
            ])

            conf.writelines([
                f'[default]',
                f'region = eu-west-1'
            ])
            
            cred.close()
            conf.close()

    # configure your thing
    from src.iot_core.utils import create_a_thing, get_endpoint, describe_thing
    with open('./src/consts/iot_core.py', 'w') as f:
        thing_name = get_input('enter a name for your thing, e.g. username-device: ')
        thing_type = get_input('enter a type for your thing or leave it blank: ', default='')
        root_cert_path = '../certs/root-CA.crt'
        client_id = get_input('enter client_id, press enter for default[pie]: ', default='pie')
        signing_region = 'eu-west-1'
        proxy_host = get_input('enter host address of proxy, press enter for default[www-proxy.scss.tcd.ie]: ', default='www-proxy.scss.tcd.ie')
        proxy_port = get_input('enter port of proxy, press enter for default[8080]: ', default='8080')
        verbosity = get_input('enter log verbosity, choices = {NoLogs,Fatal,Error,Warn,Info,Debug,Trace}, default[NoLogs]: ', check_verbosity, 'NoLogs')
        
        thing_arn = create_a_thing(thing_name, thing_type)
        while not thing_arn:
            thing_arn = describe_thing(thing_name)

        f.writelines([
            f'ENDPOINT=\'{get_endpoint()}\'\n',
            f'THING_ARN=\'{thing_arn}\'\n'
            f'ROOT_CERT_PATH=\'{root_cert_path}\'\n',
            f'CLIENT_ID=\'{client_id}\'\n',
            f'SIGNING_REGION=\'{signing_region}\'\n',
            f'PROXY_HOST=\'{proxy_host}\'\n',
            f'PROXY_PORT={proxy_port}\n',
            f'VERBOSITY=\'{verbosity}\'\n'
        ])

        f.close()

        

if __name__ == "__main__":

    if not path.exists('venv'):
        system('python3 -m venv ./venv')

    if not path.exists('./certs/root-CA.crt'):
        mkdir('./certs')
        system('curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > ./certs/root-CA.crt')
    
    # activate venv 
    system('. ./venv/bin/activate')
    # install dependencies
    system(' && '.join(COMMANDS))

    setup_aws()
