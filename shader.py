from abc import ABCMeta, abstractmethod
import math
import helpers
import settings
from solver import IntersectionInfo
from evaluator import convert_to_evaluator
import numpy as np
import light

class BackgroundShader(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def shade(self, x, y):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        pass

class BackgroundSingleColor(BackgroundShader):
    def __init__(self, color = [0,0,0]):
        self.color_ev = convert_to_evaluator(color)

    def shade(self, x, y):
        return self.color
    
    def evaluate(self, t):
        self.color = self.color_ev.evaluate(t)


class BackgroundLinearXGradient(BackgroundShader):
    def __init__(self, color1, color2, min_x, max_x):
        self.color1_ev = convert_to_evaluator(color1)
        self.color2_ev = convert_to_evaluator(color2)

    def shade(self, x, y):
        return helpers.vec_interpolate(self.color1, self.color2, float(x) / settings.width)
    
    def evaluate(self, t):
        self.color1 = self.color1_ev.evaluate(t)
        self.color2 = self.color2_ev.evaluate(t)



class BackgroundLinearYGradient(BackgroundShader):
    def __init__(self, color1, color2, min_y, max_y):
        self.color1_ev = convert_to_evaluator(color1)
        self.color2_ev = convert_to_evaluator(color2)

    def shade(self, x, y):
        return helpers.vec_interpolate(self.color1, self.color2, float(y) / settings.height)
    
    def evaluate(self, t):
        self.color1 = self.color1_ev.evaluate(t)
        self.color2 = self.color2_ev.evaluate(t)

class Shader(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        self.background_shader = BackgroundSingleColor()
        pass
    
    def set_background_shader(self, shader: BackgroundShader = None):
        if(shader == None):
            self.background_shader = BackgroundSingleColor()
        else:
            self.background_shader = shader

    @abstractmethod
    def shade(self, i: IntersectionInfo, x, y):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        self.background_shader.evaluate(t)
        pass
    

class ColorShader(Shader):
    def __init__(self, color = [1,1,1]):
        super().__init__()
        self.color = color
        pass
    def shade(self, solve: IntersectionInfo, x, y):
        if not solve.hit:
            return self.background_shader.shade(x, y)
        return self.color
    
    
    def evaluate(self, t):
        super().evaluate(t)

class AlbedoShader(Shader):
    def __init__(self):
        super().__init__()
        pass
    def shade(self, solve: IntersectionInfo, x, y):
        if not solve.hit:
            return self.background_shader.shade(x, y)
        return solve.albedo
    
    
    def evaluate(self, t):
        super().evaluate(t)
class NormalShader(Shader):
    def __init__(self):
        pass
    def shade(self, solve: IntersectionInfo, x, y):
        if not solve.hit:
            return self.background_shader.shade(x, y)
        return [solve.normal[0] * .5 + .5, solve.normal[1] * .5 + .5, solve.normal[2] * .5 + .5]
    
    
    def evaluate(self, t):
        super().evaluate(t)

class DepthShader(Shader):
    def __init__(self, min_depth, max_depth):
        super().__init__()
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.inv_relative_max_depth = 1 / (max_depth - min_depth)

    def shade(self, solve: IntersectionInfo, x, y):
        if(solve.dist <= self.min_depth):
            return [1,1,1]
        if(solve.dist >= self.max_depth):
            return [0,0,0]

        depth_value = 1 - ((solve.dist - self.min_depth) * self.inv_relative_max_depth)
        return [depth_value, depth_value, depth_value]
        

    def evaluate(self, t):
        super().evaluate(t)

class SimpleLightShader(Shader):
    def __init__(self, lights: [light.Light]):
        super().__init__()
        self.lights = lights

    def shade(self, solve: IntersectionInfo, x, y):
        if not solve.hit:
            return self.background_shader.shade(x, y)

        total_illumination = [0, 0, 0]
        for l in self.lights:
            light_info = l.light(solve)
            current_illumination = np.multiply(max(0, helpers.vec_dot(solve.normal, [-light_info.light_dir[0], -light_info.light_dir[1], -light_info.light_dir[2]])), light_info.light_intensity)
            total_illumination = np.add(total_illumination, current_illumination)
        return total_illumination
        
    def evaluate(self, t):
        super().evaluate(t)
        for l in self.lights:
            l.evaluate(t)

class FractalShader(Shader):
    def __init__(self, col1 = [1, 1, 1], col2 = [0, 0, 0], darkness = 30, light_dir = [-45, -45, -45]):
        super().__init__()
        self.col1_ev = convert_to_evaluator(col1)
        self.col2_ev = convert_to_evaluator(col2)
        self.light_dir_ev = convert_to_evaluator(light_dir)
        self.darkness_ev = convert_to_evaluator(darkness)
        pass
    def shade(self, solve: IntersectionInfo, x, y):
        if not solve.hit:
            return self.background_shader.shade(x, y)

        a = helpers.clamp(helpers.vec_dot([solve.normal[0] * .5 + .5, solve.normal[1] * .5 + .5, solve.normal[2] * .5 + .5], self.light_dir), 0, 1)
        b = helpers.clamp(solve.albedo[0] / 16.0, 0, 1)
        color_mix = helpers.vec_clamp([a * self.col1[0] + b * self.col2[0], a * self.col1[1] + b * self.col2[1], a * self.col1[2] + b * self.col2[2]], 0, 1)

        rim = solve.bounces / self.darkness
        return [color_mix[0] * rim, color_mix[1] * rim, color_mix[2] * rim]
        # return [bounce_component * self.frac_col[0], bounce_component * self.frac_col[1], bounce_component * self.frac_col[2]]
    
    
    def evaluate(self, t):
        super().evaluate(t)
        self.col1 = self.col1_ev.evaluate(t)
        self.col2 = self.col2_ev.evaluate(t)
        self.light_dir = helpers.vec_normalize(self.light_dir_ev.evaluate(t))
        self.darkness = self.darkness_ev.evaluate(t)