from manimlib.animation.animation import Animation
from manimlib.mobject.mobject import Mobject
def wait_while_updating(duration=1):
    return Animation(Mobject(), run_time=duration)