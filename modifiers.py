from abc import ABCMeta, abstractmethod
import helpers
from evaluator import convert_to_evaluator
import math

class PosModifier(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def modify(self, pos):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        pass
    
class Distort(PosModifier):
    def __init__(self, distortion_fac, distortion_offset):
        self.distortion_fac_ev = convert_to_evaluator(distortion_fac)
        self.distortion_offset_ev = convert_to_evaluator(distortion_offset)
    
    def evaluate(self, t):
        self.distortion_fac = self.distortion_fac_ev.evaluate(t)
        self.distortion_offset = self.distortion_offset_ev.evaluate(t)

    def modify(self, pos):
        return math.sin(5.0 * pos[0] + self.distortion_offset[0]) * math.sin(5.0 * pos[1] + self.distortion_offset[1]) * math.sin(5.0 * pos[2] + self.distortion_offset[2]) * self.distortion_fac