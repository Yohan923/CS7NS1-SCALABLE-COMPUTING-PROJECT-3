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