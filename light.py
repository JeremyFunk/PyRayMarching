from abc import ABCMeta, abstractmethod
import math
import helpers
import settings
from solver import IntersectionInfo
from dataclasses import dataclass
from evaluator import convert_to_evaluator

@dataclass
class LightInfo:
    light_dir: [float]
    light_intensity: [float]

class Light(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self, light_col, light_intensity):
        self.light_col_ev = convert_to_evaluator(light_col)
        self.light_intensity_ev = convert_to_evaluator(light_intensity)
    
    @abstractmethod
    def light(self, i: IntersectionInfo) -> LightInfo:
        pass

    @abstractmethod
    def evaluate(self, t):
        self.light_col = self.light_col_ev.evaluate(t)
        self.light_intensity = self.light_intensity_ev.evaluate(t)
        pass


class PointLight(Light):
    def __init__(self, light_pos, light_col, light_intensity):
        super().__init__(light_col, light_intensity)
        self.light_pos_ev = convert_to_evaluator(light_pos)

    def light(self, solve: IntersectionInfo) -> LightInfo:
        light_dir = [solve.position[0] - self.light_pos[0], solve.position[1] - self.light_pos[1], solve.position[2] - self.light_pos[2]]
        r2 = helpers.vec_len_squared(light_dir)
        distance = math.sqrt(r2)
        distance_inv = 1 / distance
        light_dir = [light_dir[0] * distance_inv, light_dir[1] * distance_inv, light_dir[2] * distance_inv]
        intensity = self.light_intensity / (4 * math.pi * r2)
        light_intensity = [self.light_col[0] * intensity, self.light_col[1] * intensity, self.light_col[2] * intensity]

        return LightInfo(light_dir, light_intensity)

    def evaluate(self, t):
        super().evaluate(t)
        self.light_pos = self.light_pos_ev.evaluate(t)

