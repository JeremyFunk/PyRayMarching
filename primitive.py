from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import numpy as np
from evaluator import convert_to_evaluator

class Primitive(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, pos, rot = [0, 0, 0]):
        self.rot_ev = convert_to_evaluator(rot)
        self.pos_ev = convert_to_evaluator(pos)
        
    def map_primitive(self, pos):
        pos = helpers.matrix_vec_mul(self.translation_mat_inv, pos)
        return self._map_primitive(pos)
    
    @abstractmethod
    def _map_primitive(self, pos):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        self.rot = self.rot_ev.evaluate(t)
        self.pos = self.pos_ev.evaluate(t)
        self.translation_mat = helpers.matrix_translation(self.rot, self.pos)
        self.translation_mat_inv = helpers.matrix_inv(self.translation_mat)

class SpherePrimitive(Primitive):
    def __init__(self, pos, rad, rot = [0, 0, 0]):
        super().__init__(pos, rot)
        self.rad_ev = convert_to_evaluator(rad)
        pass

    def _map_primitive(self, pos):
        dist = helpers.vec_len(pos) - self.rad
        return dist
    
    def evaluate(self, t):
        super().evaluate(t)
        self.rad = self.rad_ev.evaluate(t)

    
class BoxPrimitive(Primitive):
    def __init__(self, pos, bounds, rot = [0, 0, 0]):
        super().__init__(pos, rot)
        self.bounds_ev = convert_to_evaluator(bounds)

    def _map_primitive(self, pos):
        dist_vec = [abs(pos[0]) - self.bounds[0], abs(pos[1]) - self.bounds[1], abs(pos[2]) - self.bounds[2]]
        return min(max(dist_vec[0],max(dist_vec[1], dist_vec[2])), 0.0) + helpers.vec_len(helpers.vec_max(dist_vec, 0))

    def evaluate(self, t):
        super().evaluate(t)
        self.bounds = self.bounds_ev.evaluate(t)
    
from enum import Enum
class MergeMode(Enum):
    Union = 1,
    Subtraction = 2,
    Intersection = 3

class MergePrimitive():
    def __init__(self, primitive1: Primitive, primitive2: Primitive, mode: MergeMode):
        self.primitive1 = primitive1
        self.primitive2 = primitive2
        self.mode = mode

    def map_primitive(self, pos):
        d1 = self.primitive1.map_primitive(pos)
        d2 = self.primitive2.map_primitive(pos)
        if(self.mode == MergeMode.Union):
            return min(d1, d2)
        if(self.mode == MergeMode.Subtraction):
            return max(-d1, d2)
        return max(d1, d2)

    def evaluate(self, t):
        self.primitive1.evaluate(t)
        self.primitive2.evaluate(t)

class SmoothMergePrimitive():
    def __init__(self, primitive1: Primitive, primitive2: Primitive, mode: MergeMode, smoothness):
        self.primitive1 = primitive1
        self.primitive2 = primitive2
        self.mode = mode
        self.smoothness = smoothness

    def map_primitive(self, pos): 
        d1 = self.primitive1.map_primitive(pos)
        d2 = self.primitive2.map_primitive(pos)
        if(self.mode == MergeMode.Union):
            h = helpers.clamp(.5 + .5 * (d2 - d1) / self.smoothness, 0, 1)
            return helpers.interpolate(d2, d1, h) - self.smoothness * h * (1.0 - h)
        if(self.mode == MergeMode.Subtraction):
            h = helpers.clamp(.5 - .5 * (d2 + d1) / self.smoothness, 0, 1)
            return helpers.interpolate(d2, -d1, h) + self.smoothness * h * (1.0 - h)
        
        h = helpers.clamp(.5 - .5 * (d2 - d1) / self.smoothness, 0, 1)
        return helpers.interpolate(d2, d1, h) + self.smoothness * h * (1.0 - h)

    def evaluate(self, t):
        self.primitive1.evaluate(t)
        self.primitive2.evaluate(t)

# class FlowerLike(Primitive):
#     def __init__(self, pos):
#         self.pos = pos
#         pass

#     def map_primitive(self, pos):
#         dist_vec = [pos[0] - self.pos[0], pos[1] - self.pos[1], pos[2] - self.pos[2]]

#         width = .22
#         scale = 4
#         t = .2
#         dotp = helpers.vec_dot(dist_vec, dist_vec)
#         dist_vec[0] += math.sin(t * 40)*.007
#         dist_vec = np.multiply(np.divide(dist_vec, dotp), scale)
#         dist_vec = np.sin(np.add(dist_vec, [math.sin(1 + t)*2,-t,-t*2]))
#         d = helpers.vec2_len([dist_vec[1], dist_vec[2]]) - width
#         d = min(d, helpers.vec2_len([dist_vec[0], dist_vec[2]]) - width)
#         d = min(d, helpers.vec2_len([dist_vec[0], dist_vec[1]]) - width)
#         d = min(d, helpers.vec_len(np.multiply(dist_vec, np.multiply(dist_vec, dist_vec))) - width * 3)

#         return d*dotp/scale

# class SiperskiPyramid(Primitive):
#     def __init__(self, pos):
#         self.pos = pos
#         pass

#     def map_primitive(self, pos):
#         # dist_vec = [pos[0] - self.pos[0], pos[1] - self.pos[1], pos[2] - self.pos[2]]

#         ori = [0, 0, 5]
#         a1 = np.add([1,1,1], ori)
#         a2 = np.add([-1,-1,1], ori)
#         a3 = np.add([1,-1,-1], ori)
#         a4 = np.add([-1,1,-1], ori)

#         c = [0, 0, 0]
#         n = 0
#         dist = 0
#         d = 0
#         scale = .2
#         for n in range(16):
#             c = a1
#             dist = helpers.vec_len(np.subtract(pos, a1))
#             d = helpers.vec_len(np.subtract(pos, a2))
#             if d < dist:
#                 c = a2
#                 dist = d
#             d = helpers.vec_len(np.subtract(pos, a3))
#             if d < dist:
#                 c = a3
#                 dist = d
#             d = helpers.vec_len(np.subtract(pos, a4))
#             if d < dist:
#                 c = a4
#                 dist = d
#             pos = np.subtract(np.multiply(scale, pos), np.multiply(c, (scale - 1)))
#         return np.multiply(helpers.vec_len(pos), pow(scale, -15))


