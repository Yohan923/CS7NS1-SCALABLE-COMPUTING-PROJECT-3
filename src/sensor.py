import argparse
import random
import time
import json
import flask
import threading
from opensimplex import OpenSimplex


def construct_packet(keys, values):
    packet = {}
    for i in range(len(keys)):
        packet[keys[i]] = values[i]
    return json.dumps(packet)


def simulate_speed():
    global INITIAL_SPEED
    global INITIAL_ACCELERATION
    global SPEED
    global ACCELERATION
    noise = OpenSimplex()
    # Increasing this value would mean moving faster accross perlin noise space, meaning the difference between each value would be greater.
    NOISE_COUNTER_INCREMENT = 0.1

    INITIAL_SPEED = random.randrange(100)
    SPEED = INITIAL_SPEED
    INITIAL_ACCELERATION = random.randint(-3, 6)
    ACCELERATION = INITIAL_ACCELERATION

    noise_counter = 0

    while(1):
        # Taking noise from x axis of perlin noise space..
        accelleration_change = noise.noise2d(noise_counter, 0)

        ACCELERATION += accelleration_change
        SPEED += ACCELERATION

        # Some checks to make sure car isn't reversing, or is stationary for too long, etc..
        if SPEED < 0:
            SPEED = 0
        elif SPEED > 180:
            SPEED = 180
        if ACCELERATION < -5:
            ACCELERATION = -5
        elif ACCELERATION > 5:
            ACCELERATION = 5

        noise_counter += NOISE_COUNTER_INCREMENT
        # Only do this loop once a second..
        time.sleep(1)


# Create the application instance
app = flask.Flask(__name__, template_folder="templates")
SENSOR_TYPE = ""


@app.route('/')
def getSpeed():
    keys = []
    values = []
    if SENSOR_TYPE == "speed":
        global INITIAL_SPEED
        global INITIAL_ACCELERATION
        global SPEED
        global ACCELERATION
        keys = ["initialSpeed", "initialAcceleration",
                "speed", "acceleration", "speedPretty", "accelerationPretty"]
        values = [INITIAL_SPEED, INITIAL_ACCELERATION, SPEED, ACCELERATION, str(
            SPEED) + " km/h", str(ACCELERATION) + " km/h"]

    # I guess we make this packet available to gram from some port?
    myPacket = construct_packet(keys, values)
    return myPacket


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Simulates some sensors')
    parser.add_argument('--sensor-type', metavar='sensor-type', type=str,
                        help='The type of sensor to simulate')
    parser.add_argument('--port', metavar='port', type=int,
                        help='The port for the sensor output to be broadcasted to')
    args = parser.parse_args()

    if args.sensor_type is None:
        print("Please specify the type of sensor to simulate")
        exit(1)

    SENSOR_TYPE = args.sensor_type

    if args.sensor_type == "speed":
        x = threading.Thread(target=simulate_speed)
        x.daemon = True
        x.start()

    myPort = 5000
    if args.port:
        myPort = args.port
    app.run(debug=True, port=myPort)
