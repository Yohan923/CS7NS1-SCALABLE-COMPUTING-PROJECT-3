from os import path


def get_input(instruction, validate=None, default=None):

    while True:
        result = input(instruction)

        if not result and default:
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


def match_endpoint(endpoint):
    return '.iot.eu-west-1.amazonaws.com' in endpoint


def check_path(file_path):
    return path.exists(file_path)


def check_verbosity(verbosity):
    return verbosity in ['NoLogs', 'Fatal', 'Error', 'Warn', 'Info', 'Debug', 'Trace']
        

if __name__ == "__main__":

    with open('./src/config/iot_core.py', 'w') as f:

        endpoint = get_input('enter endpoint of your thing: ', match_endpoint)
        assume_role_arn = get_input('enter the arn of your assumed role connecting to iot core: ')
        root_cert_path = get_input('enter path to root CA, press enter for default[../certs/root-CA.crt]: ', check_path, '../certs/root-CA.crt')
        client_id = get_input('enter client_id, press enter for default[pie]: ', default='pie')
        signing_region = 'eu-west-1'
        proxy_host = get_input('enter host address of proxy, press enter for default[www-proxy.scss.tcd.ie]: ', default='www-proxy.scss.tcd.ie')
        proxy_port = get_input('enter port of proxy, press enter for default[8080]: ', default='8080')
        verbosity = get_input('enter log verbosity, choices = {NoLogs,Fatal,Error,Warn,Info,Debug,Trace}, default[NoLogs]: ', check_verbosity, 'NoLogs')
        
        f.writelines([
            f'ENDPOINT=\'{endpoint}\'\n',
            f'ASSUME_ROLE_ARN=\'{assume_role_arn}\'\n',
            f'ROOT_CERT_PATH=\'{root_cert_path}\'\n',
            f'CLIENT_ID=\'{client_id}\'\n',
            f'SIGNING_REGION=\'{signing_region}\'\n',
            f'PROXY_HOST=\'{proxy_host}\'\n',
            f'PROXY_PORT={proxy_port}\n',
            f'VERBOSITY=\'{verbosity}\'\n'
        ])

        f.close()
