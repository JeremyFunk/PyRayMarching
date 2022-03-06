from abc import ABCMeta, abstractmethod
from settings import max_dist, min_dist, step_number, small_step
import helpers
import math
import numpy as np
from dataclasses import dataclass

class Transition(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def transition(self, f):
        pass

class Smoothstep(Transition):
    def __init__(self, amount):
        self.amount = amount

    def transition(self, f):
        if(self.amount == 1):
            return (f * f * (3 - 2 * t));
        if(self.amount == 2):
            return f * f * f * (f * (f * 6 - 15) + 10);
        else:
            xsq = f * t; 
            xsqsq = xsq * xsq; 
            return xsqsq * (25.0 - 48.0 * f + xsq * (25.0 - xsqsq));
        
    
class CatmullRomSpline(Transition):
    def __init__(self, p0, p3):
        self.p0 = p0
        self.p3 = p3

    def transition(self, f):
        return self.catmull_rom_spline(f, self.p0, 0, 1, self.p3);

    def catmull_rom_spline(self, t, p0, p1, p2, p3):
        return 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t)