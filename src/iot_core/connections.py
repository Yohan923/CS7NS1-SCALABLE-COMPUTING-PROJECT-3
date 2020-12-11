# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from consts import iot_core as conf
from iot_core.auth import get_cred_provider_with_assumed_role
import iot_core.callbacks as cb
import uuid
import sys
import threading
import time
from uuid import uuid4


class MQTTConnection:

    def __init__(self):
        io.init_logging(getattr(io.LogLevel, conf.VERBOSITY), 'stderr')
        self.init_mqtt_connection_over_websocket()


    def init_mqtt_connection_over_websocket(self):
        client_id = conf.CLIENT_ID + str(uuid.uuid4())
        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        # use websocket
        proxy_options = http.HttpProxyOptions(host_name=conf.PROXY_HOST, port=conf.PROXY_PORT)

        credentials_provider = auth.AwsCredentialsProvider.new_default_chain(client_bootstrap)
        mqtt_connection = mqtt_connection_builder.websockets_with_default_aws_signing(
            endpoint=conf.ENDPOINT,
            client_bootstrap=client_bootstrap,
            region=conf.SIGNING_REGION,
            credentials_provider=credentials_provider,
            websocket_proxy_options=proxy_options,
            ca_filepath=conf.ROOT_CERT_PATH,
            on_connection_interrupted=cb.on_connection_interrupted,
            on_connection_resumed=cb.on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=6)

        self._connection = mqtt_connection


    def connect(self):
        print("Connecting to {} with client ID '{}'...".format(
        conf.ENDPOINT, conf.client_id))
        connect_future = self._connection.connect()
        
        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")


    def disconnect(self):
        # Disconnect
        print("Disconnecting...")
        disconnect_future = self._connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")


    def subscribe(self, topic, qos=mqtt.QoS.AT_LEAST_ONCE, callback=None):
        print("Subscribing to topic '{}'...".format(topic))
        subscribe_future, packet_id = self._connection.subscribe(
            topic=topic,
            qos=qos,
            callback=callback)

        subscribe_result = subscribe_future.result()
        print("Subscribed with {}".format(str(subscribe_result['qos'])))
        return packet_id

    
    def publish(self, topic, message, qos=mqtt.QoS.AT_LEAST_ONCE):
        if not topic:
            print('topic is not specified for publish')
            return

        print(f'Publishing message to topic = {topic}: {message}')
        self._connection.publish(
            topic=topic,
            payload=message,
            qos=qos)