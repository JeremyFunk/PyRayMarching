from abc import ABCMeta, abstractmethod
import helpers
from evaluator import convert_to_evaluator
class Filter(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self, filter = None):
        self.filter = filter
    
    def filter_color(self, x, y, col):
        res = self._filter(x, y, col)
        return res if self.filter == None else self.filter.filter_color(x, y, res)
    
    @abstractmethod
    def _filter(self, x, y, col):
        pass

    @abstractmethod
    def evaluate(self, t):
        pass
    
class ColorShift(Filter):
    def __init__(self, color_shift, filter = None):
        super().__init__(filter)
        self.color_shift_ev = convert_to_evaluator(color_shift)
    
    def evaluate(self, t):
        self.color_shift = self.color_shift_ev.evaluate(t)

    def _filter(self, x, y, col):
        return [col[0] + self.color_shift[0], col[1] + self.color_shift[1], col[2] + self.color_shift[2]]
    
class GrayFilter(Filter):
    def __init__(self, strength, filter = None):
        super().__init__(filter)
        self.strength_ev = convert_to_evaluator(strength)
    
    def evaluate(self, t):
        self.strength = self.strength_ev.evaluate(t)

    def _filter(self, x, y, col):
        gray_shifted = (col[0] + col[1] + col[2]) * .333
        gray_shifted_vec = [gray_shifted, gray_shifted, gray_shifted]

        if self.strength == 1:
            return gray_shifted_vec
        return helpers.vec_interpolate(gray_shifted_vec, col, self.strength)
    