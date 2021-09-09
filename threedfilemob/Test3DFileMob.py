from manim import *
from os import path
# Go to https://github.com/Aathish04/manim/blob/objmobject/manim/mobject/three_d_file_mobjects.py for the actual mobject.
class Test(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(
            phi=-45 * DEGREES, theta=-135 * DEGREES, gamma=-55 * DEGREES
        )
        filename = "coloured/airboat/airboat.obj"
        model = OBJMobject(
            path.abspath(
                path.dirname(__file__) + path.sep + "ref_models" + path.sep + filename
            )
        ).scale(0.5)
        self.add(model)
