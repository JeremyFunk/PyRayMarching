from abc import ABCMeta, abstractmethod
import math
import helpers
import settings
from evaluator import convert_to_evaluator


class Camera(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self, pos, rot):
        self.width = float(settings.width)
        self.height = float(settings.height)
        self.ar = self.width / self.height
        self.rot_ev = convert_to_evaluator(rot)
        self.pos_ev = convert_to_evaluator(pos)
    
    def generate_ray(self, x, y):
        direction = self._generate_ray(x, y)
        return [helpers.matrix_dir_mul(self.rot_mat_inv, direction), self.pos]

    @abstractmethod
    def _generate_ray(self, x, y):
        pass

    @abstractmethod
    def evaluate(self, t):
        self.rot = self.rot_ev.evaluate(t)
        self.pos = self.pos_ev.evaluate(t)
        self.rot_mat = helpers.matrix_rotation(self.rot)
        self.rot_mat_inv = helpers.matrix_inv(self.rot_mat)
    
class PinholeCamera(Camera):
    
    def __init__(self, pos=[0, 0, 0], rot=[0, 0, 0]):
        super().__init__(pos, rot)
        self.scale = math.radians(float(settings.fov) * .5)
        
    def _generate_ray(self, x, y):
        rx = (2 * (x + .5) / self.width - 1) * self.ar * self.scale
        ry = (1 - 2 * (y + .5) / self.height) * self.scale
        
        return helpers.vec_normalize([-ry, -rx, -1])
        
    def evaluate(self, t):
        super().evaluate(t)