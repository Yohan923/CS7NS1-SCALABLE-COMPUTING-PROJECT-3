from os import path, mkdir, system

# the commands are setup specific to linux
COMMANDS = [
    '. ./venv/bin/activate',
    'pip install awsiotsdk',
    'pip install boto3',
    'pip install numpy',
    'pip install opensimplex',
    'pip install numpy',
    'git pull',
    'python setup_aws_ta.py',
    'python setup_thing_ta.py',
    'python src/run_program.py 1 --neighbors 1 2 3 4 5 --location 10 --speed 0 --acceleration 1 --remote_host 10.35.70.27 --photo_sensor 80 --rainfall_sensor 35'
]

if __name__ == "__main__":

    if not path.exists('venv'):
        system('python3 -m venv ./venv')

    if not path.exists('./certs/root-CA.crt'):
        mkdir('./certs')
        system('curl https://www.amazontrust.com/repository/AmazonRootCA1.pem > ./certs/root-CA.crt')
    
    # install dependencies and run other setup scripts inside venv
    system(' && '.join(COMMANDS))