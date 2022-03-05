from abc import ABCMeta, abstractmethod
import camera
import film
from settings import width, height, tile_size, threads
import solver
import shader
from multiprocessing import Pool

class Renderer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, camera: camera.Camera):
        self.camera = camera
        pass
        
    @abstractmethod
    def render(self):
        pass
    
    
    @abstractmethod
    def display(self):
        pass
    
    
class CameraRayRenderer(Renderer):
    def __init__(self, camera: camera.Camera, film: film.Film):
        super().__init__(camera)
        self.film = film
        pass
        
    def render(self):
        for x in range(width):
            for y in range(height):
                self.film.write_pixel(x, y, self.camera.generate_ray(x, y))
                
    def display(self):
        image = self.film.build_image()
        image.show()

class SolverRenderer(Renderer):
    def __init__(self, camera: camera.Camera, film: film.Film, solver: solver.Solver, shader: shader.Shader):
        super().__init__(camera)
        self.film = film
        self.solver = solver
        self.shader = shader
        pass
        
    def render(self):
        tiles_x = width / tile_size
        tiles_y = height / tile_size

        if tiles_x % 1 != 0:
            tiles_x = int(tiles_x) + 1
            
        if tiles_y % 1 != 0:
            tiles_y = int(tiles_y) + 1
        process_data = []
        for tile_x in range(tiles_x):
            for tile_y in range(tiles_y):
                max_x = (tile_x + 1) * tile_size
                max_y = (tile_y + 1) * tile_size
                if(max_x >= width):
                    max_x = width - 1
                if(max_y >= height):
                    max_y = height - 1
                
                # self._render_thread(tile_x * tile_size, tile_y * tile_size, max_x, max_y)

                process_data.append((tile_x * tile_size, tile_y * tile_size, max_x, max_y))
        pool = Pool(threads)
        result = pool.starmap(self._render_thread, process_data)
        pool.close()
        pool.join()
        for e in result:
            for x in range(len(e['data'])):
                for y in range(len(e['data'][x])):
                    self.film.write_pixel(x + e['position'][0], y + e['position'][1], e['data'][x][y])
        
    def _render_thread(self, min_x, min_y, max_x, max_y):
        elements = []
        for x in range(min_x, max_x):
            curX = []
            for y in range(min_y, max_y):
                ray = self.camera.generate_ray(x, y)
                solve = self.solver.solve([0,0,0], ray, 0)
                # col = [1 / solve.dist, 1 / solve.dist, 1 / solve.dist
                col = self.shader.shade(solve)
                curX.append(col)
            elements.append(curX)
        return {'data': elements, 'position': [min_x, min_y, max_x, max_y]}
                
                
    def display(self):
        image = self.film.build_image()
        image.show()
