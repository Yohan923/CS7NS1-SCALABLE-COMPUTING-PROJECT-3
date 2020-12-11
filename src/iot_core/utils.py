import boto3

iot = boto3.client('iot')

def create_a_thing(name, type=None, attributes=None):

    response = iot.create_thing(
        thingName='string',
        thingTypeName='string',
        attributePayload={
            'attributes': {
                'string': 'string'
            },
            'merge': True|False
        },
        billingGroupName='string'
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