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
import modifiers
import light
from evaluator import InterpolatorEvaluator
import os
import transitions
from multiprocessing import freeze_support
import settings
import progressbar

freeze_support()

camera_o = camera.PinholeCamera()
color_filter1 = color_filter.GrayFilter(.99)
color_filter2 = color_filter.ColorShift([0, 0, 1], color_filter1)
film_o = film.FilteredFilm(color_filter2)
film_o = film.BasicFilm()
rotation = [
    InterpolatorEvaluator(0, 180, .5, True, transitions.Smoothstep(2)),
    InterpolatorEvaluator(0, 180, .5, True, transitions.Smoothstep(2)),
    InterpolatorEvaluator(0, 180, .5, True, transitions.Smoothstep(2)),
]

primitives = [
    # primitive.SpherePrimitive([0, 0, -10], InterpolatorEvaluator(2, 3, .5, True, transitions.Smoothstep(2))),
    # primitive.BoxPrimitive([0, 0, -5], [1,1,1], [0, 0, 0])
    # primitive.SiperskiPyramid([0, 0, 5])
    primitive.SmoothMergePrimitive(
        primitive.SpherePrimitive([InterpolatorEvaluator(5, 3, 1, True, transitions.Smoothstep(2)), 0, -15], InterpolatorEvaluator(2, 3, 1, True, transitions.Smoothstep(2)), rotation), 
        primitive.SpherePrimitive([InterpolatorEvaluator(-8, -2, 1, True, transitions.CatmullRomSpline(-3, 1)), 0, -15], InterpolatorEvaluator(2, 3, 1, True, transitions.Smoothstep(2))),
        primitive.MergeMode.Union,
        2
    )
]

# solver = solver.DisplacedSphereSolver([0, 0, -5], 2)
modifiers = [
    modifiers.Distort(InterpolatorEvaluator(0, .5, 2, True, None, .2), [0, 0, 0], 2.0),
    modifiers.Distort(InterpolatorEvaluator(.1, .2, 1, True, None, .4), [1, 1, 1], 4.0),
    modifiers.Distort(InterpolatorEvaluator(0, .1, .2, True, None, .6), [2, 2, 2], 8.0),
]
solver = solver.GeneralSolver(primitives, modifiers)
# shader = shader.SimpleLightShader([-3, -4, -2], [1, .2, .4])

lights = {
    light.PointLight([-10, 4, -2], [1, .2, 0], 300),
    light.PointLight([10 , -4, -8], [0, 1, 1], 300)
}
shader = shader.SimpleLightShader(lights)


if __name__ == "__main__":
    freeze_support()
    renderer_o = renderer.SolverRenderer(camera_o, film_o, solver, shader)

    if(settings.video_render):
        for frame in progressbar.progressbar(range(settings.start_frame, settings.end_frame)):
            renderer_o.evaluate(frame / settings.ups)
            renderer_o.prepare_render()
            renderer_o.render()
            img = renderer_o.get_image()
            img.save(os.path.join(settings.file_path, "img" + str(frame) + ".png"))


        helpers.save_video()
    else:
        renderer_o.evaluate(settings.still_render_t)
        renderer_o.prepare_render()
        renderer_o.render()


        img = renderer_o.get_image()
        img.save(os.path.join(settings.file_path, "result.png"))

        img.show()