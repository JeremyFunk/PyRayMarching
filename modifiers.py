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
    def __init__(self, distortion_fac, distortion_offset, distortion_freq):
        self.distortion_fac_ev = convert_to_evaluator(distortion_fac)
        self.distortion_offset_ev = convert_to_evaluator(distortion_offset)
        self.distortion_freq_ev = convert_to_evaluator(distortion_freq)
    
    def evaluate(self, t):
        self.distortion_fac = self.distortion_fac_ev.evaluate(t)
        self.distortion_offset = self.distortion_offset_ev.evaluate(t)
        self.distortion_freq = self.distortion_freq_ev.evaluate(t)

    def modify(self, pos):
        return math.sin(self.distortion_freq * pos[0] + self.distortion_offset[0]) * math.sin(self.distortion_freq * pos[1] + self.distortion_offset[1]) * math.sin(self.distortion_freq * pos[2] + self.distortion_offset[2]) * self.distortion_fac