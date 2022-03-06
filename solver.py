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
    bounces: int
    normal: [float]
    position: [float]

class Solver(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def solve(self, pos, ray, bounces) -> IntersectionInfo:
        pass

    @abstractmethod
    def evaluate(self, t):
        pass

class GeneralSolver(Solver):
    def __init__(self, primitives: [primitive.Primitive], pos_modifiers: [modifiers.PosModifier]):
        self.primitives = primitives
        self.pos_modifiers = pos_modifiers
        
    def solve(self, pos, ray, bounces):
        res = self._solve_world(pos, ray, bounces)
        if not res[0]:
            return IntersectionInfo(False, res[1], res[2], None, res[3])
        normal = self._calculate_normal(res[3])
        return IntersectionInfo(True, res[1], res[2], normal, res[3])

    def _calculate_normal(self, pos):
        gradient_x = self._map_world([pos[0] + small_step, pos[1], pos[2]]) - self._map_world([pos[0] - small_step, pos[1], pos[2]])
        gradient_y = self._map_world([pos[0], pos[1] + small_step, pos[2]]) - self._map_world([pos[0], pos[1] - small_step, pos[2]])
        gradient_z = self._map_world([pos[0], pos[1], pos[2] + small_step]) - self._map_world([pos[0], pos[1], pos[2] - small_step])
        return helpers.vec_normalize([gradient_x, gradient_y, gradient_z])

    def _solve_world(self, pos, ray, bounces):
        total_dist = 0
        for i in range(step_number):
            dist = self._map_world(pos)
            if(dist < min_dist):
                return [True, total_dist, bounces, pos]
            if(dist > max_dist):
                return [False, total_dist, bounces, pos]

            estimator = dist * .99
            total_dist += estimator
            pos = [pos[0] + ray[0] * estimator, pos[1] + ray[1] * estimator, pos[2] + ray[2] * estimator]
        return [False, total_dist, step_number, pos]

    def _map_world(self, pos):
        
        lowest_dist = max_dist * 10
        for prim in self.primitives:
            dist = prim.map_primitive(pos)
            if(dist < lowest_dist):
                lowest_dist = dist

        displacement = 0
        for m in self.pos_modifiers:
            displacement += m.modify(pos)
            
        return lowest_dist + displacement

    def evaluate(self, t):
        for p in self.primitives:
            p.evaluate(t)
        for m in self.pos_modifiers:
            m.evaluate(t)