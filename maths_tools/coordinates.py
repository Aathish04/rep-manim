#Some tools that are useful for coordinate manipulation and whatnot.
from manimlib.imports import *
def spherical_to_cartesian(pol_ang,azim_ang,radius): #This function converts given spherical coordinates (theta, phi and radius) to cartesian coordinates.
        return np.array((radius*np.sin(pol_ang) * np.cos(azim_ang),
                            radius*np.sin(pol_ang) * np.sin(azim_ang),
                            radius*np.cos(pol_ang))
                            )