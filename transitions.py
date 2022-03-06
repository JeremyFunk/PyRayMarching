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
        
    