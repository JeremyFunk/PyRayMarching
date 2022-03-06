from abc import ABCMeta, abstractmethod
import camera
import film
from settings import width, height, tile_size, threads, end_frame, start_frame, fps, ups, file_path
import solver
import shader
from multiprocessing import Pool
import time
import os

class Renderer(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass
        
    @abstractmethod
    def render(self):
        pass
    
    
    @abstractmethod
    def get_image(self) -> film.FilmReturn:
        pass
    
    
    @abstractmethod
    def evaluate(self, t):
        pass
    
    @abstractmethod
    def prepare_render(self):
        pass

class CameraRayRenderer(Renderer):
    def __init__(self, camera: camera.Camera, film: film.Film):
        self.camera = camera
        self.film = film
        pass
        
    def render(self):
        for x in range(width):
            for y in range(height):
                self.film.write_pixel(x, y, self.camera.generate_ray(x, y)[0])
                
    def get_image(self):
        return self.film.build_image()

    def evaluate(self, t):
        pass

    def prepare_render(self):
        pass

class SolverRenderer(Renderer):
    def __init__(self, camera: camera.Camera, film: film.Film, solver: solver.Solver, shader: shader.Shader):
        self.camera = camera
        self.film = film
        self.solver = solver
        self.shader = shader
        pass
        
    def render(self):
        render_time = time.perf_counter()
        if(threads == 1):
            e = self._render_thread(0, 0, width, height)
            # print("Render took:" + str(time.perf_counter() - render_time))
            for x in range(len(e['data'])):
                for y in range(len(e['data'][x])):
                    self.film.write_pixel(x + e['position'][0], y + e['position'][1], e['data'][x][y])
            # print("Total took:" + str(time.perf_counter() - render_time))
            return

        tiles_x = width / tile_size
        tiles_y = height / tile_size

        if tiles_x % 1 != 0:
            tiles_x = tiles_x + 1
        if tiles_y % 1 != 0:
            tiles_y = tiles_y + 1

        tiles_x = int(tiles_x)
        tiles_y = int(tiles_y)

        process_data = []
        for tile_x in range(tiles_x):
            for tile_y in range(tiles_y):
                max_x = (tile_x + 1) * tile_size
                max_y = (tile_y + 1) * tile_size
                if(max_x >= width):
                    max_x = width
                if(max_y >= height):
                    max_y = height
                
                # self._render_thread(tile_x * tile_size, tile_y * tile_size, max_x, max_y)

                process_data.append((tile_x * tile_size, tile_y * tile_size, max_x, max_y))
        pool = Pool(threads)
        result = pool.starmap(self._render_thread, process_data)
        pool.close()
        pool.join()
        # print("Render took:" + str(time.perf_counter() - render_time))
        for e in result:
            for x in range(len(e['data'])):
                for y in range(len(e['data'][x])):
                    self.film.write_pixel(y + e['position'][1], x + e['position'][0], e['data'][x][y])
        
        # print("Total took:" + str(time.perf_counter() - render_time))
        
    def _render_thread(self, min_x, min_y, max_x, max_y):
        elements = []
        for x in range(min_x, max_x):
            curX = []
            for y in range(min_y, max_y):
                ray = self.camera.generate_ray(x, y)
                solve = self.solver.solve(ray[1], ray[0])
                # col = [1 / solve.dist, 1 / solve.dist, 1 / solve.dist
                col = self.shader.shade(solve, x, y)
                curX.append(col)
            elements.append(curX)
        return {'data': elements, 'position': [min_x, min_y, max_x, max_y]}
                
                
    def get_image(self):
        return self.film.build_image()

    def evaluate(self, t):
        self.camera.evaluate(t)
        self.solver.evaluate(t)
        self.film.evaluate(t)
        self.shader.evaluate(t)

    def prepare_render(self):
        self.film.prepare_render()