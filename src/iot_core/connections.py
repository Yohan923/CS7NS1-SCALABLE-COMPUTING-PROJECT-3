# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import consts.iot_core as conf
import iot_core.callbacks as cb
import uuid
import sys
import threading
import time
from uuid import uuid4


class MQTTConnection:

    def __init__(self):
        io.init_logging(getattr(io.LogLevel, conf.VERBOSITY), 'stderr')


    @staticmethod
    def get_mqtt_connection_over_websocket():
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

        return mqtt_connection

    
    @staticmethod
    def get_mqtt_connection(cert_path, pri_key_path):

        client_id = conf.CLIENT_ID + str(uuid.uuid4())
        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
        
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=conf.ENDPOINT,
            cert_filepath=cert_path,
            pri_key_filepath=pri_key_path,
            client_bootstrap=client_bootstrap,
            ca_filepath=conf.ROOT_CERT_PATH,
            on_connection_interrupted=cb.on_connection_interrupted,
            on_connection_resumed=cb.on_connection_resumed,
            client_id=client_id,
            clean_session=False,
            keep_alive_secs=6)

        return mqtt_connection
