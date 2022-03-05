from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import primitive
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

class DisplacedSphereSolver(Solver):
    def __init__(self, pos, rad):
        self.pos = pos
        self.rad = rad
        pass
        
    def solve(self, pos, ray, bounces):
        res = self._solve_sphere(pos, ray, bounces)
        if not res[0]:
            return IntersectionInfo(False, res[1], res[2], None, res[3])
        normal = self._calculate_normal(res[3])
        return IntersectionInfo(True, res[1], res[2], normal, res[3])

    def _calculate_normal(self, pos):
        gradient_x = self._map_sphere([pos[0] + small_step, pos[1], pos[2]]) - self._map_sphere([pos[0] - small_step, pos[1], pos[2]])
        gradient_y = self._map_sphere([pos[0], pos[1] + small_step, pos[2]]) - self._map_sphere([pos[0], pos[1] - small_step, pos[2]])
        gradient_z = self._map_sphere([pos[0], pos[1], pos[2] + small_step]) - self._map_sphere([pos[0], pos[1], pos[2] - small_step])
        return helpers.vec_normalize([gradient_x, gradient_y, gradient_z])

    def _solve_sphere(self, pos, ray, bounces):
        total_dist = 0
        for i in range(step_number):
            dist = self._map_sphere(pos)
            if(dist < min_dist):
                return [True, total_dist, bounces, pos]
            if(dist > max_dist):
                return [False, total_dist, bounces, pos]

            estimator = dist * .99
            total_dist += estimator
            pos = [pos[0] + ray[0] * estimator, pos[1] + ray[1] * estimator, pos[2] + ray[2] * estimator]
        return [False, total_dist, step_number, pos]

    def _map_sphere(self, pos):
        displacement = math.sin(5.0 * pos[0]) * math.sin(5.0 * pos[1]) * math.sin(5.0 * pos[2]) * .25

        dist_vec = [pos[0] - self.pos[0], pos[1] - self.pos[1], pos[2] - self.pos[2]]
        dist = helpers.vec_len(dist_vec) - self.rad
        return dist + displacement




class GeneralSolver(Solver):
    def __init__(self, primitives: [primitive.Primitive], distortion: bool = False):
        self.primitives = primitives
        self.distortion = distortion
        pass
        
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

        if self.distortion:
            displacement = math.sin(5.0 * pos[0]) * math.sin(5.0 * pos[1]) * math.sin(5.0 * pos[2]) * .25
            return lowest_dist + displacement
            
        return lowest_dist