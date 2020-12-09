# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from config import iot_core as conf
from iot_core.auth import get_cred_provider_with_assumed_role
import iot_core.callbacks as cb
import uuid
import sys
import threading
import time
from uuid import uuid4


io.init_logging(getattr(io.LogLevel, conf.VERBOSITY), 'stderr')

received_all_event = threading.Event()

def connect_to_thing_via_mqtt_with_websock():
    try:
        client_id = conf.CLIENT_ID + str(uuid.uuid4())
        # Spin up resources
        event_loop_group = io.EventLoopGroup(1)
        host_resolver = io.DefaultHostResolver(event_loop_group)
        client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

        # use websocket
        proxy_options = http.HttpProxyOptions(host_name=conf.PROXY_HOST, port=conf.PROXY_PORT)

        credentials_provider = get_cred_provider_with_assumed_role(role_arn=conf.ASSUME_ROLE_ARN)
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

        print("Connecting to {} with client ID '{}'...".format(
            conf.ENDPOINT, conf.client_id))

        connect_future = mqtt_connection.connect()

        # Future.result() waits until a result is available
        connect_future.result()
        print("Connected!")

    except KeyboardInterrupt:
        # Disconnect
        print("Disconnecting...")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()
        print("Disconnected!")
