from manimlib.constants import *
def get_surface(surface,fill_color=WHITE, stroke_color=None, fill_opacity=0.5, stroke_width=0, stroke_opacity=None):
    if not stroke_color:
        stroke_color=fill_color
    if not stroke_opacity:
        stroke_opacity = fill_opacity
    result = surface.copy()
    result.set_fill(fill_color, opacity=fill_opacity)
    result.set_stroke(stroke_color, width=stroke_width, opacity=stroke_opacity)
    return result