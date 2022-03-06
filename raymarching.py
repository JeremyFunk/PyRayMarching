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
import postprocessors

freeze_support()

camera_o = camera.PinholeCamera([0, 0, InterpolatorEvaluator(2, 1.4, 3, True, transitions.Smoothstep(2))], [0, 0, 0])
color_filter1 = color_filter.GrayFilter(.99)
color_filter2 = color_filter.ColorShift([0, 0, 1], color_filter1)
film_o = film.FilteredFilm(color_filter2)
film_o = film.BasicFilm([postprocessors.BloomPostProcessor()])
rotation = [
    InterpolatorEvaluator(160, 180, 3, True, transitions.Smoothstep(2)),
    0,
    0
]

# solver = solver.DisplacedSphereSolver([0, 0, -5], 2)
pos_modifiers = [
    # modifiers.Distort(InterpolatorEvaluator(0, .5, 2, True, None, .2), [0, 0, 0], 2.0),
    # modifiers.Distort(InterpolatorEvaluator(.1, .2, 1, True, None, .4), [1, 1, 1], 4.0),
    # modifiers.Distort(InterpolatorEvaluator(0, .1, .2, True, None, .6), [2, 2, 2], 8.0),
    # modifiers.Repetition(10)
    # modifiers.RepetitionLimited(4, [3, 4, 1]),
    # modifiers.Twist(InterpolatorEvaluator(0, 10, 1, True, transitions.Smoothstep(2)))
    # modifiers.Bend(.1)     
]

dist_modifiers = [
    # modifiers.Round(1)
    # modifiers.Onion(.5)
]

primitives = [
    # primitive.SpherePrimitive([0, 0, -40], 2),
    # primitive.BoxPrimitive([0, 0, -30], [1,1,1], [0, 0, 0], pos_modifiers=pos_modifiers, dist_modifiers=dist_modifiers)
    # primitive.Torus([0, 0, -5], radius=2, ring_diameter=1, rot=[0, 0, 0], pos_modifiers=pos_modifiers, dist_modifiers=dist_modifiers)
    primitive.Mandelbulb2([0, 0, 0], InterpolatorEvaluator(10, 30, 20, True), rotation)
    # primitive.SiperskiPyramid([0, 0, 5])
    # primitive.SmoothMergePrimitive(
    #     primitive.SpherePrimitive([InterpolatorEvaluator(5, 3, 1, True, transitions.Smoothstep(2)), -5, -15], InterpolatorEvaluator(2, 3, 1, True, transitions.Smoothstep(2)), rotation), 
    #     primitive.SpherePrimitive([InterpolatorEvaluator(-8, -2, 1, True, transitions.CatmullRomSpline(-3, 1)), -5, -15], InterpolatorEvaluator(2, 3, 1, True, transitions.Smoothstep(2))),
    #     primitive.MergeMode.Union,
    #     2
    # )
]

solver = solver.GeneralSolver(primitives, [])


lights = {
    light.PointLight([-10, 4, -2], [1, .2, 0], 300),
    light.PointLight([10 , -4, -8], [0, 1, 1], 300)
}
# shader_o = shader.ColorShader()
shader_o = shader.FractalShader([.4, .1, .2], [.9, .2, .3], 30, [InterpolatorEvaluator(-45, 90, 3), -45, -45])
shader_o.set_background_shader(shader.BackgroundLinearYGradient([0.05, 0.02, 0.04], [0.1, 0.06, 0.06], 0, 1))
# shader_o = shader.SimpleLightShader(lights)


if __name__ == "__main__":
    freeze_support()
    renderer_o = renderer.SolverRenderer(camera_o, film_o, solver, shader_o)

    if(settings.video_render):
        for frame in progressbar.progressbar(range(settings.start_frame, settings.end_frame)):
            renderer_o.evaluate(frame / settings.ups)
            renderer_o.prepare_render()
            renderer_o.render()
            img = renderer_o.get_image()
            img.raw.save(os.path.join(settings.file_path, "img_raw" + str(frame) + ".png"))
            img.processed.save(os.path.join(settings.file_path, "img" + str(frame) + ".png"))


        helpers.save_video()
    else:
        renderer_o.evaluate(settings.still_render_t)
        renderer_o.prepare_render()
        renderer_o.render()


        img = renderer_o.get_image()
        img.raw.save(os.path.join(settings.file_path, "result_raw.png"))
        img.processed.save(os.path.join(settings.file_path, "result.png"))

        img.processed.show()