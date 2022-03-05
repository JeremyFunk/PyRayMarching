import numpy as np
from PIL import Image
import camera
import helpers
import film
import color_filter
import renderer
import solver
import shader
import primitive
from multiprocessing import freeze_support

freeze_support()

camera_o = camera.PinholeCamera()
color_filter1 = color_filter.GrayFilter(.99)
color_filter2 = color_filter.ColorShift([0, 0, 1], color_filter1)
film_o = film.FilteredFilm(color_filter2)
film_o = film.BasicFilm()

primitives = [
    primitive.SpherePrimitive([0, 0, 5], 2)
    # primitive.SiperskiPyramid([0, 0, 5])
]

# solver = solver.DisplacedSphereSolver([0, 0, -5], 2)
solver = solver.GeneralSolver(primitives, True)
# shader = shader.SimpleLightShader([-3, -4, -2], [1, .2, .4])
shader = shader.NormalShader()


import multiprocessing as mp

def my_func(x,y):
    print(x*y)
if __name__ == "__main__":
    freeze_support()
    
    renderer = renderer.SolverRenderer(camera_o, film_o, solver, shader)
    renderer.render()
    renderer.display()