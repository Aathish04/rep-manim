from manimlib.constants import *
from manimlib.mobject.three_dimensions import Sphere
from manimlib.mobject.types.vectorized_mobject import VGroup
from ..anim_tools import shading
from ..maths_tools import coordinates

class ThomsonsAtom(VGroup):
    """
    Returns a VGroup depicting Thomson's Atom.

    Parameters
    ----------
    shell_config (dict) = { 1:{"radius":1.0,"electron_count":4,"colour":YELLOW_C},
                            2:{"radius":1.5,"electron_count":4,"colour":YELLOW_B} }
    cloud_radius (int,float) = 2
    """
    CONFIG={
        "shell_config":{ #gives info about each shell and electrons inside.
            1:{"radius":1.0,"electron_count":4,"colour":YELLOW_C},
            2:{"radius":1.5,"electron_count":4,"colour":YELLOW_B}
        },
        "cloud_radius":2
    }
    def __init__(self,shell_config=None,cloud_radius=None):
        VGroup.__init__(self)
        if not shell_config:
            self.shell_config=self.CONFIG["shell_config"]
        if not cloud_radius:
            self.cloud_radius=self.CONFIG["cloud_radius"]
        self.make_atom()
        self.move_to(ORIGIN)

    def get_electron_coordinates_list(self,electron_count):
        #Special Edge Case for 2 Electrons.
        if electron_count==1: #Edge case for Hydrogen. DO NOT RUN if shell is greater than 1
            print("1 point generated")
            return([[0,0,0]])
        elif electron_count==2: #Edge case for 2 electrons.
            print("2 points generated")
            return([[0,0,1],[0,0,-1]])
        else:
            #Algorithm used was mostly  taken from https://www.cmu.edu/biolphys/deserno/pdf/sphere_equi.pdf . Explanations in code added by me.

            #For some reason unbeknownst to me, this algorithm's output varies HIGHLY depending on radius. If the radius is lesser than one, it creates way more electrons than requested.
            #If the radius is more than one, this creates not enough electrons. ;( As a result, I've had to force this to use only radius one, and change the apparent radius later on, by scaling the model up.

            inner_radius=1

            electron_coordinate_list=[]
            inner_area=4*(PI*inner_radius**2)
            area_per_electron=inner_area/electron_count
            pseudo_length_per_electron=np.sqrt(area_per_electron) #This is the side length of a square where the area of it is the area per electron on the sphere.
            #Now, we need to get a value of angular space, such that angular space between electrons on latitude and longitude per electron is equal
            #As a first step to obtaining this, we must make another value holding a whole number approximation of the ratio between PI and the pseudo_length. This will give the number of
            #possible latitudes.

            possible_count_of_lats=np.round(PI/pseudo_length_per_electron)

            approx_length_per_electron_lat=PI/possible_count_of_lats #This is the length between electrons on a latitude
            approx_length_per_electron_long=area_per_electron/approx_length_per_electron_lat #This is the length between electrons on a longitude

            for electron_num_lat in range(int(possible_count_of_lats.item())): #The int(somenumpyvalue.item()) is used because Python cannot iterate over a numpy integer and it must be converted to normal int.
                pol_ang=PI*(electron_num_lat+0.5)/possible_count_of_lats #The original algorithm recommended pol_ang=PI*(electron_num_lat+0.5)/possible_count_of_lats. The 0.5 appears to be added in order to get a larger number of coordinates.
                #not sure if removing the 0.5 affects results. It didnt do so drastically, so what gives? Anyway, this gets the polar angle as PI*(latitudenumber)/totalnumberoflatitudes.

                possible_count_of_longs=np.round(2*PI*np.sin(pol_ang)/approx_length_per_electron_long)

                for electron_num_long in range(int(possible_count_of_longs.item())):

                    azim_ang=(2*PI)*(electron_num_long)/possible_count_of_longs #This gets the azimuthal angle as 2PI*longitudenumber/totalnumberoflongitudes

                    electron_coordinate=coordinates.spherical_to_cartesian(pol_ang, azim_ang,inner_radius) #Converts the recieved spherical coordinates to cartesian so Manim can easily handle them.
                    electron_coordinate_list.append(electron_coordinate) #Add this coordinate to the electron_coordinate_list

                    #print("Got coordinates: ",electron_coordinate) #Print the coordinate recieved.

            print(len(electron_coordinate_list)," points generated.") #Print the amount of electrons will exist. Comment these two lines out if you don't need the data.
            return electron_coordinate_list

    def make_atom(self):

        electron_dict={} #This holds all the electrons in the format {"shell_n":electron}

        for shell in self.shell_config:
            electron_dict[shell]=VGroup()
            tempVGroup=VGroup()
            if self.shell_config[shell]["electron_count"]==0:
                continue
            else:
                for electron_coordinate in self.get_electron_coordinates_list(self.shell_config[shell]["electron_count"]): #for each electron coordinate in get_electron_coordinates where the radius of the inner circle is 1 and electron_count electrons are needed:
                    electron=shading.get_surface(surface=Sphere(radius=0.08),fill_color=self.shell_config[shell]["colour"],fill_opacity=1)
                    electron.move_to(electron_coordinate)
                    electron_dict[shell].add(electron)
            tempVGroup=VGroup(*electron_dict[shell])
            tempVGroup.space_out_submobjects(self.shell_config[shell]["radius"])

        positivecloud = shading.get_surface(surface = Sphere(radius=2),fill_color=DARK_BLUE)

        # atom=VGroup(*electron_dict["shell_1"],*electron_dict["shell_2"],positivecloud)
        self.add(positivecloud)
        for shell in electron_dict:
            self.add(electron_dict[shell])

    def get_electrons(self):
        return self[1:]

    def get_cloud(self):
        return self[0]