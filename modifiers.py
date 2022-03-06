from abc import ABCMeta, abstractmethod
import helpers
from evaluator import convert_to_evaluator
import math

class PosModifier(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def modify(self, pos) -> [float]:
        pass
    
    @abstractmethod
    def evaluate(self, t):
        pass
    

class DistanceModifier(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def modify(self, d) -> float:
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
        m = math.sin(self.distortion_freq * pos[0] + self.distortion_offset[0]) * math.sin(self.distortion_freq * pos[1] + self.distortion_offset[1]) * math.sin(self.distortion_freq * pos[2] + self.distortion_offset[2]) * self.distortion_fac
        return [pos[0] + m, pos[1] + m, pos[2] + m]

class Twist(PosModifier):
    def __init__(self, amount):
        self.amount_ev = convert_to_evaluator(amount)
    
    def evaluate(self, t):
        self.amount = self.amount_ev.evaluate(t)

    def modify(self, pos):
        c = math.cos(self.amount * pos[1])
        s = math.sin(self.amount * pos[1])

        return [c * pos[0] - s * pos[2], s * pos[0] + c * pos[2], pos[1]]


class Bend(PosModifier):
    def __init__(self, amount):
        self.amount_ev = convert_to_evaluator(amount)
    
    def evaluate(self, t):
        self.amount = self.amount_ev.evaluate(t)

    def modify(self, pos):
        c = math.cos(self.amount * pos[0])
        s = math.sin(self.amount * pos[0])
        m = [[c, -s], [s, c]]

        return [c * pos[0] - s * pos[1], s * pos[0] + c * pos[1], pos[2]]


class Repetition(PosModifier):
    def __init__(self, repetition_period):
        self.repetition_period_ev = convert_to_evaluator(repetition_period)
    
    def evaluate(self, t):
        self.repetition_period = self.repetition_period_ev.evaluate(t)

    def modify(self, pos):
        return [
            ((pos[0] + .5 * self.repetition_period) % self.repetition_period) - .5 * self.repetition_period,
            ((pos[1] + .5 * self.repetition_period) % self.repetition_period) - .5 * self.repetition_period,
            ((pos[2] + .5 * self.repetition_period) % self.repetition_period) - .5 * self.repetition_period
        ]
class RepetitionLimited(PosModifier):
    def __init__(self, repetition_period, limiter):
        self.repetition_period_ev = convert_to_evaluator(repetition_period)
        self.limiter_ev = convert_to_evaluator(limiter)
    
    def evaluate(self, t):
        self.repetition_period = self.repetition_period_ev.evaluate(t)
        self.limiter = self.limiter_ev.evaluate(t)

    def modify(self, pos):
        return [
            (pos[0] - self.repetition_period * helpers.clamp(round(pos[0] / self.repetition_period), -self.limiter[0], self.limiter[0])),
            (pos[1] - self.repetition_period * helpers.clamp(round(pos[1] / self.repetition_period), -self.limiter[1], self.limiter[1])),
            (pos[2] - self.repetition_period * helpers.clamp(round(pos[2] / self.repetition_period), -self.limiter[2], self.limiter[2]))
        ]


class Round(DistanceModifier):
    def __init__(self, thickness):
        self.thickness_ev = convert_to_evaluator(thickness)
    
    def evaluate(self, t):
        self.thickness = self.thickness_ev.evaluate(t)

    def modify(self, dist):
        return abs(dist)-self.thickness


# class Onion(DistanceModifier):
#     def __init__(self, rad):
#         self.rad_ev = convert_to_evaluator(rad)
    
#     def evaluate(self, t):
#         self.rad = self.rad_ev.evaluate(t)

#     def modify(self, dist):
#         return dist - self.rad