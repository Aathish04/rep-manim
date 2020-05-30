from manim.animation.animation import Animation
from manim.mobject.mobject import Mobject
def wait_while_updating(duration=1):
    return Animation(Mobject(), run_time=duration)