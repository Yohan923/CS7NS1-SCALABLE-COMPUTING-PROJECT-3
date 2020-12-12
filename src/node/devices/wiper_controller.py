from rainfall_sensor import RainfallLevel
from threading import Thread
import time

class WIPER_SPEED():
    FAST = 2
    SLOW = 1
    STOP = 0

class WiperController(Thread):

    def __init__(self, wiper_speed):
        Thread.__init__(self)
        self._wiper_speed = wiper_speed

    
    def set_speed(self, wiper_speed):
        self._wiper_speed = wiper_speed

    
    def get_speed(self):
        return self._wiper_speed
    

    # rainfall measured by the critical angle between the glass and infrared, the critical angle for total internal refraction is around 42°
    # when glass is dry, 60° when wet, assume 70° for very wet
    def set_speed_by_rainfall(self, rainfall):
        if rainfall <= RainfallLevel.DRY:
            self.set_speed(WIPER_SPEED.STOP)
        elif rainfall <= RainfallLevel.MILD:
            self.set_speed(WIPER_SPEED.SLOW)
        else:
            self.set_speed(WIPER_SPEED.FAST)

    def run(self):
        while True:
            # not really do anything since its a contoller
            time.sleep(5000)
