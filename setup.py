from os import path, mkdir, system

# the commands are setup specific to linux
COMMANDS = [
    '. ./venv/bin/activate',
    'pip install awsiotsdk',
    'pip install boto3',
    'pip install numpy',
    'pip install opensimplex',
    'pip install numpy',
    'python setup_aws.py',
    'python setup_thing.py'
]

if __name__ == "__main__":

    if not path.exists('venv'):
        system('python3 -m venv ./venv')

    if not path.exists('./certs/root-CA.crt'):
        mkdir('./certs')
        system('curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > ./certs/root-CA.crt')
    
    # install dependencies and run other setup scripts inside venv
    system(' && '.join(COMMANDS))
