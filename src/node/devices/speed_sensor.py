from threading import Thread
import time


class SpeedSensor(Thread):

    def __init__(self, speed_vector):
        Thread.__init__(self)
        self._speed_vector = speed_vector # in the form (x, y), direction and speed in respective axis


    def set_speed(self, speed_vector):
        self._speed_vector = speed_vector

    
    def get_speed(self):
        return self._speed_vector

    def run(self):
        while True:
            # can be where to generate data
            print(self.get_speed())
            time.sleep(1)