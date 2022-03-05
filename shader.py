from abc import ABCMeta, abstractmethod
import math
import helpers
import settings
from solver import IntersectionInfo

class Shader(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def shade(self, i: IntersectionInfo):
        pass
    
class NormalShader(Shader):
    def __init__(self):
        pass
    def shade(self, solve: IntersectionInfo):
        if not solve.hit:
            return [0, 0, 0]
        return [solve.normal[0] * .5 + .5, solve.normal[1] * .5 + .5, solve.normal[2] * .5 + .5]
        

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
        


class SimpleLightShader(Shader):
    def __init__(self, light_pos, light_col):
        self.light_pos = light_pos
        self.light_col = light_col

    def shade(self, solve: IntersectionInfo):
        if not solve.hit:
            return [0, 0, 0]

        light_dir = helpers.vec_normalize([solve.position[0] - self.light_pos[0], solve.position[1] - self.light_pos[1], solve.position[2] - self.light_pos[2]])
        diffuse_intensity = max(0, helpers.vec_dot(solve.normal, light_dir))
        return [self.light_col[0] * diffuse_intensity, self.light_col[1] * diffuse_intensity, self.light_col[2] * diffuse_intensity]
        