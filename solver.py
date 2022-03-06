from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import primitive
import modifiers
import numpy as np
from dataclasses import dataclass

@dataclass
class IntersectionInfo:
    hit: bool
    dist: float
    albedo: [float]
    bounces: int
    normal: [float]
    position: [float]

class Solver(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def solve(self, pos, ray) -> IntersectionInfo:
        pass

    @abstractmethod
    def evaluate(self, t):
        pass

class GeneralSolver(Solver):
    def __init__(self, primitives: [primitive.Primitive], pos_modifiers: [modifiers.PosModifier]):
        self.primitives = primitives
        self.pos_modifiers = pos_modifiers
        
    def solve(self, pos, ray):
        res = self._solve_world(pos, ray)
        if not res[0]:
            return IntersectionInfo(False, res[1], res[2], res[3], None, res[4])
        normal = self._calculate_normal(res[4])
        return IntersectionInfo(True, res[1], res[2], res[3], normal, res[3])

    def _calculate_normal(self, pos):
        gradient_x = self._map_world([pos[0] + small_step, pos[1], pos[2]]).distance - self._map_world([pos[0] - small_step, pos[1], pos[2]]).distance
        gradient_y = self._map_world([pos[0], pos[1] + small_step, pos[2]]).distance - self._map_world([pos[0], pos[1] - small_step, pos[2]]).distance
        gradient_z = self._map_world([pos[0], pos[1], pos[2] + small_step]).distance - self._map_world([pos[0], pos[1], pos[2] - small_step]).distance
        return helpers.vec_normalize([gradient_x, gradient_y, gradient_z])

    def _solve_world(self, pos, ray):
        total_dist = 0
        for i in range(step_number):
            dist = self._map_world(pos)
            if(dist.distance < min_dist):
                return [True, total_dist, dist.albedo, i, pos]
            if(dist.distance > max_dist):
                return [False, total_dist, [0,0,0], i, pos]

            estimator = dist.distance
            total_dist += estimator
            pos = [pos[0] + ray[0] * estimator, pos[1] + ray[1] * estimator, pos[2] + ray[2] * estimator]
        return [False, total_dist, [0,0,0], step_number, pos]

    def _map_world(self, pos):
        
        for m in self.pos_modifiers:
            pos = m.modify(pos)

        lowest_dist = primitive.MapReturn([0,0,0], max_dist * 2)
        for prim in self.primitives:
            dist = prim.map_primitive(pos)
            if(dist.distance < lowest_dist.distance):
                lowest_dist = dist
 
        return lowest_dist

    def evaluate(self, t):
        for p in self.primitives:
            p.evaluate(t)
        for m in self.pos_modifiers:
            m.evaluate(t)