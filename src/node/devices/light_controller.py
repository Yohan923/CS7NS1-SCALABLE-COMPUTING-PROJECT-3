from node.devices.photo_sensor import PhotoIntensity
import time
from threading import Thread

class LIGHT_INTENSITY():
    OFF = 0
    DIM = 1
    NORMAL = 0

class LightController(Thread):

    def __init__(self, headlight_state):
        Thread.__init__(self)
        self._headlight_state = headlight_state

    
    def set_state(self, headlight_state):
        self._headlight_state = headlight_state

    
    def get_state(self):
        return self._headlight_state
    
    
    def set_speed_by_photo_intensity(self, photo_intensity):
        if photo_intensity >= PhotoIntensity.BRIGHT:
            self.set_state(LIGHT_INTENSITY.OFF)
        elif photo_intensity <= PhotoIntensity.DIM:
            self.set_state(LIGHT_INTENSITY.DIM)
        else:
            self.set_state(LIGHT_INTENSITY.NORMAL)
    
    def run(self):
        while True:
            # not really do anything since its a contoller
            time.sleep(5000)
