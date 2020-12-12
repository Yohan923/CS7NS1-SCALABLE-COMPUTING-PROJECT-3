from threading import Thread
import time


# rainfall measured by the critical angle between the glass and infrared, the critical angle for total internal refraction is around 42°
# when glass is dry, 60° when wet, assume 70° for very wet
class RainfallLevel():
    HIGH = 70
    MILD = 60
    DRY = 42


class RainfallSensor(Thread):
    
    def __init__(self, rainfall):
        Thread.__init__(self)
        self._rainfall = rainfall


    def set_rainfall(self, rainfall):
        self._rainfall = rainfall


    def get_rainfall(self):
        return self._rainfall


    def run(self):
        while True:
            # can be where to generate data
            print(self.get_rainfall())
            time.sleep(1)