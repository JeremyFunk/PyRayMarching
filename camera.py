from abc import ABCMeta, abstractmethod
import math
import helpers
import settings

class Camera(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        self.width = float(settings.width)
        self.height = float(settings.height)
        self.ar = self.width / self.height
    
    @abstractmethod
    def generate_ray(self, x, y):
        pass

    @abstractmethod
    def evaluate(self, t):
        pass
    
class PinholeCamera(Camera):
    
    def __init__(self):
        super().__init__()
        self.scale = math.radians(float(settings.fov) * .5)
        
    def generate_ray(self, x, y):
        rx = (2 * (x + .5) / self.width - 1) * self.ar * self.scale
        ry = (1 - 2 * (y + .5) / self.height) * self.scale
        
        return helpers.vec_normalize([-ry, -rx, -1])
        
    def evaluate(self, t):
        pass