def subscribe(): # to be implemented
    # Subscribe
    print("Subscribing to topic '{}'...".format(args.topic))
    subscribe_future, packet_id = mqtt_connection.subscribe(
        topic=args.topic,
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_message_received)

    subscribe_result = subscribe_future.result()
    print("Subscribed with {}".format(str(subscribe_result['qos'])))


def publish(): # to be implemented
    pass