from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import numpy as np
import modifiers
from evaluator import convert_to_evaluator
from dataclasses import dataclass

@dataclass
class MapReturn:
    albedo: [float]
    distance: float

class Primitive(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, pos, rot = [0, 0, 0], scale = [1, 1, 1], pos_modifiers: [modifiers.PosModifier] = [], dist_modifiers: [modifiers.DistanceModifier] = []):
        self.pos_modifiers = pos_modifiers
        self.dist_modifiers = dist_modifiers
        self.rot_ev = convert_to_evaluator(rot)
        self.pos_ev = convert_to_evaluator(pos)
        self.scale_ev = convert_to_evaluator(scale)
        
    def map_primitive(self, pos) -> MapReturn:
        pos = helpers.matrix_vec_mul(self.translation_mat_inv, pos)

        for m in self.pos_modifiers:
            pos = m.modify(pos)

        ret = self._map_primitive(pos)
        for d in self.dist_modifiers:
            ret.distance = d.modify(distance)
        return ret
    
    @abstractmethod
    def _map_primitive(self, pos) -> MapReturn:
        pass
    
    @abstractmethod
    def evaluate(self, t):
        self.rot = self.rot_ev.evaluate(t)
        self.pos = self.pos_ev.evaluate(t)
        self.scale = self.scale_ev.evaluate(t)
        self.translation_mat = helpers.matrix_translation(self.rot, self.pos, self.scale)
        self.translation_mat_inv = helpers.matrix_inv(self.translation_mat)
        for m in self.pos_modifiers:
            m.evaluate(t)
        for m in self.dist_modifiers:
            m.evaluate(t)

class SpherePrimitive(Primitive):
    def __init__(self, pos, rad, rot = [0, 0, 0], scale=[1, 1, 1], pos_modifiers = [], dist_modifiers = []):
        super().__init__(pos, rot, scale, pos_modifiers, dist_modifiers)
        self.rad_ev = convert_to_evaluator(rad)
        pass

    def _map_primitive(self, pos):
        dist = helpers.vec_len(pos) - self.rad
        return MapReturn([1,1,1], dist)
    
    def evaluate(self, t):
        super().evaluate(t)
        self.rad = self.rad_ev.evaluate(t)

    
class BoxPrimitive(Primitive):
    def __init__(self, pos, bounds, rot = [0, 0, 0], pos_modifiers = [], dist_modifiers = []):
        super().__init__(pos, rot, [1, 1, 1], pos_modifiers, dist_modifiers)
        self.bounds_ev = convert_to_evaluator(bounds)

    def _map_primitive(self, pos):
        dist_vec = [abs(pos[0]) - self.bounds[0], abs(pos[1]) - self.bounds[1], abs(pos[2]) - self.bounds[2]]
        dist =  min(max(dist_vec[0],max(dist_vec[1], dist_vec[2])), 0.0) + helpers.vec_len(helpers.vec_max(dist_vec, 0))
        return MapReturn([1,1,1], dist)

    def evaluate(self, t):
        super().evaluate(t)
        self.bounds = self.bounds_ev.evaluate(t)
    
class Torus(Primitive):
    def __init__(self, pos, radius, ring_diameter, rot = [0, 0, 0], pos_modifiers = [], dist_modifiers = []):
        super().__init__(pos, rot, [1, 1, 1], pos_modifiers, dist_modifiers)
        self.radius_ev = convert_to_evaluator(radius)
        self.ring_diameter_ev = convert_to_evaluator(ring_diameter)

    def _map_primitive(self, pos):
        l = math.sqrt(pos[0] * pos[0] + pos[2] * pos[2]) - self.radius
        dist =  math.sqrt(l * l + pos[1] * pos[1]) - self.ring_diameter
        return MapReturn([1,1,1], dist)

    def evaluate(self, t):
        super().evaluate(t)
        self.radius = self.radius_ev.evaluate(t)
        self.ring_diameter = self.ring_diameter_ev.evaluate(t)

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
            dist = min(d1.distance, d2.distance)
            return MapReturn([1,1,1], dist)

        if(self.mode == MergeMode.Subtraction):
            dist =  max(-d1.distance, d2.distance)
            return MapReturn([1,1,1], dist)

        dist =  max(d1.distance, d2.distance)
        return MapReturn([1,1,1], dist)

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
            dist = helpers.interpolate(d2, d1, h) - self.smoothness * h * (1.0 - h)
            return MapReturn([1,1,1], dist)

        if(self.mode == MergeMode.Subtraction):
            h = helpers.clamp(.5 - .5 * (d2 + d1) / self.smoothness, 0, 1)
            dist = helpers.interpolate(d2, -d1, h) + self.smoothness * h * (1.0 - h)
            return MapReturn([1,1,1], dist)
        
        h = helpers.clamp(.5 - .5 * (d2 - d1) / self.smoothness, 0, 1)
        dist = helpers.interpolate(d2, d1, h) + self.smoothness * h * (1.0 - h)
        return MapReturn([1,1,1], dist)

    def evaluate(self, t):
        self.primitive1.evaluate(t)
        self.primitive2.evaluate(t)

class Mandelbulb(Primitive):
    def __init__(self, pos, rot = [0, 0, 0], pos_modifiers = [], dist_modifiers = []):
        super().__init__(pos, rot, [1, 1, 1], pos_modifiers, dist_modifiers)

    def _map_primitive(self, pos):
        w = [pos[0], pos[1], pos[2]]
        m = helpers.vec_len_squared(w)

        trap = [abs(w[0]), abs(w[1]), abs(w[2]), m]
        dz = 1.0
        
        for i in range(5):
            # dz = 8.0 * math.pow(m, 3.5) * dz + 1.0

            # r = helpers.vec_len(w)
            # b = 8.0 * math.acos(w[1] / r)
            # a = 8.0 * math.atan2(w[0], w[2])
            # w = [
            #     pos[0] + pow(r, 8.0) * math.sin(b) * math.sin(a),
            #     pos[1] + pow(r, 8.0) * math.cos(b),
            #     pos[2] + pow(r, 8.0) * math.sin(b) * math.cos(a),
            # ]

            m2 = m*m;
            m4 = m2*m2;
            dz = 8.0*math.sqrt(m4*m2*m)*dz + 1.0;

            x = w[0]; x2 = x*x; x4 = x2*x2;
            y = w[1]; y2 = y*y; y4 = y2*y2;
            z = w[2]; z2 = z*z; z4 = z2*z2;

            k3 = x2 + z2;
            k2 = k3*k3*k3*k3*k3*k3*k3;
            k2 = k2**-.5
            k1 = x4 + y4 + z4 - 6.0*y2*z2 - 6.0*x2*y2 + 2.0*z2*x2;
            k4 = x2 - y2 + z2;

            w[0] = pos[0] +  64.0*x*y*z*(x2-z2)*k4*(x4-6.0*x2*z2+z4)*k1*k2;
            w[1] = pos[1] + -16.0*y2*k3*k4*k4 + k1*k1;
            w[2] = pos[2] +  -8.0*y*k4*(x4*x4 - 28.0*x4*x2*z2 + 70.0*x4*z4 - 28.0*x2*z2*z4 + z4*z4)*k1*k2;

            trap = [min(abs(w[0]), trap[0]), min(abs(w[1]), trap[1]), min(abs(w[2]), trap[2]), min(trap[3], m)]
            m = helpers.vec_len_squared(w)
            if m > 512.0:
                break


            
        return MapReturn([m, trap[1], trap[2]], .25 * math.log(m) * math.sqrt(m) / dz)


        # return 

    def evaluate(self, t):
        super().evaluate(t)

class Mandelbulb2(Primitive):
    def __init__(self, pos, power, rot = [0, 0, 0], pos_modifiers = [], dist_modifiers = []):
        super().__init__(pos, rot, [1, 1, 1], pos_modifiers, dist_modifiers)
        self.power_ev = convert_to_evaluator(power)

    def _map_primitive(self, pos):
        z = [pos[0], pos[1], pos[2]]
        dr = 1.0;
        r = 0.0;
        iterations = 0;

        for i in range(15):
            iterations = i;
            r = helpers.vec_len(z)

            if (r>2):
                break;
            
            theta = math.acos(z[2]/r);
            phi = math.atan2(z[1],z[0]);
            dr =  math.pow( r, self.power-1.0)*self.power*dr + 1.0;

            zr = math.pow( r,self.power);
            theta = theta*self.power;
            phi = phi*self.power;
            
            z = [math.sin(theta)*math.cos(phi) * zr, math.sin(phi)*math.sin(theta) * zr, math.cos(theta) * zr];
            z = [z[0] + pos[0], z[1] + pos[1], z[2] + pos[2]];
        dst = 0.5*math.log(r)*r/dr;
        return MapReturn([iterations, iterations, iterations], dst);


        # return 

    def evaluate(self, t):
        super().evaluate(t)
        self.power = self.power_ev.evaluate(t)

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


