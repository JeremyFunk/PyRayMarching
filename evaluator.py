from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
from dataclasses import dataclass

class Evaluator(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def evaluate(self, t) -> float:
        pass

class FloatEvaluator(Evaluator):
    def __init__(self, val):
        self.val = val
        pass
        
    def evaluate(self, t):
        return self.val
    

class InterpolatorEvaluator(Evaluator):
    def __init__(self, val_min, val_max, interval, oscilate = False):
        self.val_min = val_min
        self.val_max = val_max
        self.interval = interval
        self.oscilate = oscilate
        pass
        
    def evaluate(self, t):
        f = (t % interval) / self.interval

        if self.oscilate and t % (interval * 2) > interval:
            f = 1 - f
            
        return self.val_min * (1 - f) + self.val_max * f
        

class Vector3Evaluator(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def evaluate(self, t) -> [float]:
        pass

class ConstructVector3Evaluator(Vector3Evaluator):
    def __init__(self, x: Evaluator, y: Evaluator, z: Evaluator):
        self.x = x
        self.y = y
        self.z = z
    
    def evaluate(self, t) -> [float]:
        return [
            self.x.evaluate(t),
            self.y.evaluate(t),
            self.z.evaluate(t)
        ]



class CastVector3Evaluator(Vector3Evaluator):
    def __init__(self, e: Evaluator):
        self.e = e
    
    def evaluate(self, t) -> [float]:
        res = self.e.evaluate(t)
        return [res, res, res]

def convert_to_evaluator(f):
    if isinstance(f, int) or isinstance(f, float):
        return FloatEvaluator(f)

    if isinstance(f, list):
        if(len(f) == 3):
            return ConstructVector3Evaluator(FloatEvaluator(f[0]), FloatEvaluator(f[1]), FloatEvaluator(f[2]))
        else:
            raise Exception("Unknown length of evaluator")
    
    return f