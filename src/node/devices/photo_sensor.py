from threading import Thread
import time


# TODO: try to proper readings
class PhotoIntensity():
    BRIGHT = 100
    DIM = 60
    DARK = 20


class PhotoSensor(Thread):
    
    def __init__(self, photo_intensity):
        Thread.__init__(self)
        self._photo_intensity = photo_intensity


    def set_photo_intensity(self, photo_intensity):
        self._photo_intensity = photo_intensity


    def get_photo_intensity(self):
        return self._photo_intensity


    def run(self):
        while True:
            # can be where to generate data
            print(self.get_photo_intensity())
            time.sleep(1)