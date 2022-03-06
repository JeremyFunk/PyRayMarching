from abc import ABCMeta, abstractmethod
from settings import width, height
from PIL import Image
import helpers
import numpy as np

class Film(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def write_pixel(self, x, y, col):
        pass
    
    def build_image(self) -> Image.Image:
        pass
      
    @abstractmethod
    def evaluate(self, t):
        pass
    
    @abstractmethod
    def prepare_render(self):
        pass
    
class BasicFilm(Film):
    def __init__(self):
        pass
        
    def write_pixel(self, x, y, col):
        self.data[x,y] = col
    
    def build_image(self):
        formatted = (np.clip(self.data, 0, 1) * 255).astype('uint8')
        return Image.fromarray(formatted)

    def evaluate(self, t):
        pass

    def prepare_render(self):
        self.data = np.zeros((width,height,3), dtype=np.float32 )

class FilteredFilm(Film):
    def __init__(self, color_filter):
        self.data = np.zeros((width,height,3), dtype=np.float32 )
        self.color_filter = color_filter
        
    def write_pixel(self, x, y, col):
        self.data[x,y] = self.color_filter.filter_color(x, y, col)
    
    def build_image(self):
        formatted = (np.clip(self.data, 0, 1) * 255).astype('uint8')
        return Image.fromarray(formatted)

    def evaluate(self, t):
        pass
    
    def prepare_render(self):
        self.data = np.zeros((width,height,3), dtype=np.float32 )