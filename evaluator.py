from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step, epsilon
import helpers
import math
import transitions
from dataclasses import dataclass

class Evaluator(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, offset = 0):
        self.offset = offset
        pass
        
    def evaluate(self, t) -> float:
        return self._evaluate(t + self.offset)
    
    @abstractmethod
    def _evaluate(self, t) -> float:
        pass

class FloatEvaluator(Evaluator):
    def __init__(self, val, offset = 0):
        super().__init__(offset)
        self.val = val
        
    def _evaluate(self, t):
        return self.val
    

class InterpolatorEvaluator(Evaluator):
    def __init__(self, val_min, val_max, interval, oscilate = True, transition_function: transitions.Transition = None, offset = 0):
        super().__init__(offset)
        self.val_min = val_min
        self.val_max = val_max
        self.interval = interval
        self.oscilate = oscilate
        self.transition_function = transition_function
        
    def _evaluate(self, t):
        f = 0
        if(t != 0):
            f = (t % self.interval) / self.interval

        if(self.transition_function != None):
            f = self.transition_function.transition(f)

        

        if self.oscilate and t % (self.interval * 2) >= self.interval - epsilon:
            f = 1 - f
            
        return self.val_min * (1 - f) + self.val_max * f
        

class Vector3Evaluator(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, offset = 0):
        self.offset = offset
        
    def evaluate(self, t) -> [float]:
        return self._evaluate(t + self.offset)
    
    @abstractmethod
    def _evaluate(self, t) -> [float]:
        pass

class ConstructVector3Evaluator(Vector3Evaluator):
    def __init__(self, x: Evaluator, y: Evaluator, z: Evaluator, offset = 0):
        super().__init__(offset)
        self.x = x
        self.y = y
        self.z = z
    
    def _evaluate(self, t) -> [float]:
        return [
            self.x.evaluate(t),
            self.y.evaluate(t),
            self.z.evaluate(t)
        ]



class CastVector3Evaluator(Vector3Evaluator):
    def __init__(self, e: Evaluator, offset = 0):
        super().__init__(offset)
        self.e = e
    
    def _evaluate(self, t) -> [float]:
        res = self.e.evaluate(t)
        return [res, res, res]

def convert_to_evaluator(f):
    if isinstance(f, int) or isinstance(f, float):
        return FloatEvaluator(f)

    if isinstance(f, list):
        if(len(f) == 3):
            return ConstructVector3Evaluator(convert_to_evaluator(f[0]), convert_to_evaluator(f[1]), convert_to_evaluator(f[2]))
        else:
            raise Exception("Unknown length of evaluator")
    
    return f