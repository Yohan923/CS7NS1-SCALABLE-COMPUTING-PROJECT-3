import boto3

iot = boto3.client('iot')

def create_a_thing(thing_name, thing_type=None, attributes=None):
    param_dict = {}
    for name, val in [('thingTypeName', thing_type), ('attributePayload', attributes)]:
        if val:
            param_dict.update({name: val})

    response = iot.create_thing(
        thingName=thing_name,
        **param_dict
    )

    return response.get('thingArn')


def describe_thing(name):

    response = iot.describe_thing(
        thingName=name
    )

    return response.get('thingArn')


def get_endpoint():
    response = iot.describe_endpoint(
        endpointType='iot:Data-ATS'
    )

    return response.get('endpointAddress')