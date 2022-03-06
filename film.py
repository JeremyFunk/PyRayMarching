from abc import ABCMeta, abstractmethod
from settings import width, height
from PIL import Image
import helpers
import numpy as np
from postprocessors import PostProcessor
from dataclasses import dataclass

@dataclass
class FilmReturn:
    raw: Image.Image
    processed: Image.Image

class Film(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self, post_processor: [PostProcessor]):
        self.post_processor = post_processor
    
    @abstractmethod
    def write_pixel(self, x, y, col):
        pass
    
    def build_image(self) -> FilmReturn:
        u = self._build_image()
        for p in self.post_processor:
            self.data = p.process_image(self.data)
        return FilmReturn(u, self._build_image())

    @abstractmethod
    def _build_image(self) -> Image.Image:
        pass
      
    @abstractmethod
    def evaluate(self, t):
        for p in self.post_processor:
            p.evaluate(t)
    
    def prepare_render(self):
        self.data = np.zeros((width,height,3), dtype=np.float32 )
    
class BasicFilm(Film):
    def __init__(self, post_processor = []):
        super().__init__(post_processor)
        
    def write_pixel(self, x, y, col):
        self.data[x,y] = col
    
    def _build_image(self):
        formatted = (np.clip(self.data, 0, 1) * 255).astype('uint8')
        return Image.fromarray(formatted)

    def evaluate(self, t):
        super().evaluate(t)


class FilteredFilm(Film):
    def __init__(self, color_filter, post_processor = []):
        super().__init__(post_processor)
        self.data = np.zeros((width,height,3), dtype=np.float32 )
        self.color_filter = color_filter
        
    def write_pixel(self, x, y, col):
        self.data[x,y] = self.color_filter.filter_color(x, y, col)
    
    def _build_image(self):
        formatted = (np.clip(self.data, 0, 1) * 255).astype('uint8')
        return Image.fromarray(formatted)

    def evaluate(self, t):
        super().evaluate(t)