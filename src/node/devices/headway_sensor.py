from threading import Thread
import config
import time


class HeadwaySensor(Thread):
    # distance_to_contact suppose to represent the distance between your car head and the object in front of it if any
    def __init__(self, distance_to_contact=None):
        Thread.__init__(self)
        self._distance_to_contact = distance_to_contact


    def set_distance_to_contact(self, distance_to_contact):
        self._distance_to_contact = distance_to_contact


    def get_distance_to_contact(self):
        return self._distance_to_contact


    def run(self):
        while True:
            # can be where to generate data
            print(self.get_distance_to_contact())
            time.sleep(1)