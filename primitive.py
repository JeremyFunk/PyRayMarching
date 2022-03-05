from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import numpy as np

class Primitive(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def map_primitive(self, pos):
        pass
    
class SpherePrimitive(Primitive):
    def __init__(self, pos, rad):
        self.pos = pos
        self.rad = rad
        pass

    def map_primitive(self, pos):
        dist_vec = [pos[0] - self.pos[0], pos[1] - self.pos[1], pos[2] - self.pos[2]]
        dist = helpers.vec_len(dist_vec) - self.rad
        return dist
    
class BoxPrimitive(Primitive):
    def __init__(self, pos, bounds):
        self.pos = pos
        self.bounds = bounds
        pass

    def map_primitive(self, pos):
        dist_vec = [abs(pos[0] - self.pos[0]) - self.bounds[0], abs(pos[1] - self.pos[1]) - self.bounds[1], abs(pos[2] - self.pos[2]) - self.bounds[2]]

        return min(max(dist_vec[0],max(dist_vec[1], dist_vec[2])), 0.0) + helpers.vec_len(helpers.vec_max(dist_vec, 0))

    
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


