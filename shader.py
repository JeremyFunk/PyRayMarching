from abc import ABCMeta, abstractmethod
import math
import helpers
import settings
from solver import IntersectionInfo
import numpy as np
import light

class Shader(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def shade(self, i: IntersectionInfo):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        pass
    
class NormalShader(Shader):
    def __init__(self):
        pass
    def shade(self, solve: IntersectionInfo):
        if not solve.hit:
            return [0, 0, 0]
        return [solve.normal[0] * .5 + .5, solve.normal[1] * .5 + .5, solve.normal[2] * .5 + .5]
    
    
    def evaluate(self, t):
        pass

class DepthShader(Shader):
    def __init__(self, min_depth, max_depth):
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.inv_relative_max_depth = 1 / (max_depth - min_depth)

    def shade(self, solve: IntersectionInfo):
        if(solve.dist <= self.min_depth):
            return [1,1,1]
        if(solve.dist >= self.max_depth):
            return [0,0,0]

        depth_value = 1 - ((solve.dist - self.min_depth) * self.inv_relative_max_depth)
        return [depth_value, depth_value, depth_value]
        

    def evaluate(self, t):
        pass

class SimpleLightShader(Shader):
    def __init__(self, lights: [light.Light]):
        self.lights = lights

    def shade(self, solve: IntersectionInfo):
        if not solve.hit:
            return [0, 0, 0]

        total_illumination = [0, 0, 0]
        for l in self.lights:
            light_info = l.light(solve)
            current_illumination = np.multiply(max(0, helpers.vec_dot(solve.normal, [-light_info.light_dir[0], -light_info.light_dir[1], -light_info.light_dir[2]])), light_info.light_intensity)
            total_illumination = np.add(total_illumination, current_illumination)
        return total_illumination
        
    def evaluate(self, t):
        for l in self.lights:
            l.evaluate(t)