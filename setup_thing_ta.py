from src.utils import get_input, check_verbosity
from src.iot_core.utils import create_a_thing, get_endpoint, describe_thing

if __name__ == "__main__":
        # configure your thing
    with open('./src/consts/iot_core.py', 'w') as f:
        thing_name = 'TA'
        thing_type = ''
        root_cert_path = './certs/root-CA.crt'
        client_id = 'TA-pi'
        signing_region = 'eu-west-1'
        proxy_host = 'www-proxy.scss.tcd.ie'
        proxy_port = '8080'
        verbosity = 'NoLogs'
        
        thing_arn = create_a_thing(thing_name, thing_type)
        print(f'created thing with name {thing_name} arn = {thing_arn}')

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