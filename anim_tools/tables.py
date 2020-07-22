import warnings
from typing import *

from manimlib.utils.iterables import list_update

from manimlib.animation.creation import ShowCreation
from manimlib.animation.transform import Transform
from manimlib.animation.transform import ApplyMethod
from manimlib.animation.composition import AnimationGroup

from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Line

from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.numbers import DecimalNumber
from manimlib.mobject.numbers import Integer


from manimlib.constants import *

class Tools():
    def flatten(inlist):
        outlist=[]
        for element in inlist:
            for sub_element in element:
                outlist.append(sub_element)
        return outlist



class Table(VGroup): #TODO: Specific Table position insertions.
    CONFIG={
            "tabledict":{},
            "vbuff_length":None,
            "hbuff_length":None,
            "buff_length":0.3,
            "line_color":WHITE,
            "raw_string_color":WHITE,
        }

    def __init__(self,tabledict,**kwargs): #__init__ is called everytime Table() is called.

        for item in kwargs: #Add everything that has been given in kwargs to the config.
                self.CONFIG[item]=kwargs[item] #Using digest config gave AttributeError: 'dict' object has no attribute '__dict__'

        if not self.CONFIG["tabledict"]:
            self.tabledict:dict = tabledict
        self.buff_length:Union[float,int]=self.CONFIG["buff_length"]
        self.vbuff_length=self.buff_length if self.CONFIG["vbuff_length"] is None else self.CONFIG["vbuff_length"]
        self.hbuff_length=self.buff_length if self.CONFIG["hbuff_length"] is None else self.CONFIG["hbuff_length"]
        self.line_color:Union[str,hex]=self.CONFIG["line_color"]
        self.raw_string_color:Union[str,hex]=self.CONFIG["raw_string_color"]
        self.unchanged:bool=True
        # self.cell_height
        # self.cell_length

        VGroup.__init__(self) #Initialise Table as VGroup

        self.make_table() #Make the table with the parameters in CONFIG
        self.move_to(ORIGIN)

    def scale(self, scale_factor, **kwargs): #custom scale function updates the cell length and table length as required
        if self.unchanged==False:
            self.cell_length*=scale_factor
            self.cell_height*=scale_factor
        """
        Default behavior is to scale about the center of the mobject.
        The argument about_edge can be a vector, indicating which side of
        the mobject to scale about, e.g., mob.scale(about_edge = RIGHT)
        scales about mob.get_right().
        Otherwise, if about_point is given a value, scaling is done with
        respect to that point.
        """
        self.apply_points_function_about_point(
            lambda points: scale_factor * points, **kwargs
        )
        return self

    def make_table(self):

        self.unchanged=True #unchanged becomes False when some record or field has been added.

        #Get values from CONFIG
        tabledict=self.tabledict
        buff_length=self.buff_length
        hbuff_length=self.hbuff_length
        vbuff_length=self.vbuff_length
        line_color=self.line_color
        raw_string_color=self.raw_string_color

        #self is now the table. so self.add has replaced table.add in this function.

        fields=list(tabledict.keys()) #Since the data is recieved as a dict, the keys will be the fields

        #the for loop below checks that every field and record is of a valid type and converts to TextMobject if need be:
        for fieldnum in range(len(fields)):

            if isinstance(fields[fieldnum],(TextMobject,TexMobject,Text,DecimalNumber,Integer))==False:
                tabledict[TextMobject(fields[fieldnum],fill_color=raw_string_color)] = tabledict.pop(fields[fieldnum])

            fields=list(tabledict.keys())

            for recordnum in range(0,len(tabledict[fields[fieldnum]])):
                if isinstance(tabledict[fields[fieldnum]][recordnum],(TexMobject,TextMobject,Text,DecimalNumber,Integer))==False:
                    tabledict[fields[fieldnum]][recordnum]=TextMobject(tabledict[fields[fieldnum]][recordnum],fill_color=raw_string_color)
                else:
                    continue

        cell_length=( max(fields + Tools.flatten(tabledict.values()), key=lambda mobject:mobject.get_width()) ).get_width() + 2*hbuff_length #The length/height of a record/field of
        cell_height=( max(fields + Tools.flatten(tabledict.values()), key=lambda mobject:mobject.get_height()) ).get_height()+ 2*vbuff_length #max length/height is the base cell size

        self.cell_height=cell_height
        self.cell_length=cell_length

        #The first position is set like so.

        field_position=[ (cell_length-TexMobject(fields[0]).get_width())/2 + TexMobject(fields[0]).get_width()/2, 0,0 ] #The initial position of the first field.

        #NOTE: Coordinates of TexMobjects in Manim are taken from centre, not top-right. Adjustments have been made by adding half the width of the object in all calculations.

        total_table_width=(cell_length*len(fields)) #The remaining width and height will be successively added
        total_table_height=cell_height*(len(max(tabledict.values(),key=len))+1)#while drawing the Mobjects to the screen. +1 is added to account for headings.

        for n in range(0,len(fields)):

            field=fields[n]
            field_length=field.get_width() #This is the length that the actual field name will take up on-screen

            if n+1<len(fields): #This gets the nxt field if it exists and chooses an empty TexMobject if it doesn't
                next_field=(fields[n+1])
            else:
                next_field=TexMobject("")

            next_field_length=next_field.get_width() #Gets the next fields length


            field.move_to(field_position)


            space_to_right_of_field=(cell_length-field_length)/2

            space_to_left_of_next_field=(cell_length-next_field_length)/2

            space_to_leave= space_to_right_of_field + space_to_left_of_next_field + next_field_length/2

            #next_field_length/2 is added to account for the fact that coordinates are taken from centre and not left edges.

            self.add(field)
            field_position=field.get_right()+(space_to_leave,0,0)

        for keynum in range(len(tabledict.keys())):
            key=list(tabledict.keys())[keynum] #gets the actual key
            recordlist=tabledict[key] #selects the list with the records for

            if recordlist!=[]:

                record_position=[self[keynum].get_center()[0], -((cell_height-fields[keynum].get_height())/2 + fields[keynum].get_height()/2 + cell_height ),0]

                #the record position is set to be the [center of the field it belongs to, buffer space above the record + centered height of the record, 0  ]

                for recordnum in range(len(recordlist)):# for each record for
                    record=recordlist[recordnum] # the selected field


                    if recordnum+1<len(recordlist): #This gets the nxt record if it exists and chooses an empty TexMobject if it doesn't
                        next_record=recordlist[recordnum+1]
                    else:
                        next_record=TexMobject("")


                    record.move_to(record_position)
                    record_position=record.get_center()+(0,-cell_height,0)
                    self.add(record)
            else:
                pass

        line_hor=Line(start=(0,-2*cell_height/3,0),end=(total_table_width,-2*cell_height/3,0),color=line_color)
        self.add(line_hor) #This is the horizontal separator

        for l in range (len(fields)-1): #These create the vertical separators.
            line=Line( start=(self[l].get_center()+ (cell_length/2,cell_height/2,0)),
            end =(self[l].get_center()+ (cell_length/2,-total_table_height,0)),
            color=line_color)

            self.add(line)

    def add_record(self,record,field_num,record_pos=-1):
        self.unchanged=False

        orig_submob_list=list(self.submobjects)
        records_in_required_field = len(self.tabledict[list(self.tabledict.keys())[field_num]])
        records_to_skip=0

        if isinstance(record,(TexMobject,TextMobject,Text,DecimalNumber,Integer))==False :
                record=TextMobject(record) #Mandatory Type Conversions


        for i in range(0,field_num): #Until you reach the field where the record should be added
            records_to_skip+=len(self.tabledict[list(self.tabledict.keys())[i]]) #skip the records in the field

        fields_records_to_skip = len(self.tabledict.keys()) + records_to_skip #Skip all the fields and the records you are supposed to.


        if record_pos!=-1: #If a custom record postion is given
            warnings.warn("Custom Record Positions are still in Development. May give unwanted results.")
            rec_index=fields_records_to_skip+record_pos #put the record there
        else:
            rec_index=fields_records_to_skip+records_in_required_field #Go to the end of the field and put the record there.

        assigned_field=list(self.tabledict.keys())[field_num]

        vert_num=len(self.tabledict[list(self.tabledict.keys())[field_num]])+1+0.5 #1 is added for field name 0.5 is added for half record width

        how_far_down=vert_num*self.cell_height/2 #How far down to move.

        record.move_to(assigned_field.get_center()-(0,how_far_down,0)) #Move the record to the assigned fields x coord and move required amount down

        if record_pos==-1:
            self.tabledict[list(self.tabledict.keys())[field_num]].append(record)
        else:
            self.tabledict[list(self.tabledict.keys())[field_num]].insert(record_pos,record) #add the record to tabledict

        new_submob_list = orig_submob_list[:rec_index] + [record] + orig_submob_list[rec_index:] #make the new submob list and insert record at propre place.

        self.submobjects = list_update(self.submobjects, new_submob_list) #update self

        return record

    def remove_record(self,field_num,record_num):
        orig_submob_list=list(self.submobjects)
        records_in_required_field = len(self.tabledict[list(self.tabledict.keys())[field_num]])
        records_to_skip=0

        for i in range(0,field_num): #Until you reach the field where the record should be added
            records_to_skip+=len(self.tabledict[list(self.tabledict.keys())[i]]) #skip the records in the field

        fields_records_to_skip = len(self.tabledict.keys()) + records_to_skip #Skip all the fields and the records you are supposed to.
        if record_num!=-1:
            rec_index=fields_records_to_skip+record_num
        else:
            rec_index=fields_records_to_skip+records_in_required_field-1

        self.tabledict[list(self.tabledict.keys())[field_num]].pop(record_num) #remove the value from tabledict

        return self.submobjects.pop(rec_index)

    def get_record(self,field_num,record_num):
        orig_submob_list=list(self.submobjects)
        records_in_required_field = len(self.tabledict[list(self.tabledict.keys())[field_num]])
        records_to_skip=0

        for i in range(0,field_num): #Until you reach the field where the record should be added
            records_to_skip+=len(self.tabledict[list(self.tabledict.keys())[i]]) #skip the records in the field

        fields_records_to_skip = len(self.tabledict.keys()) + records_to_skip #Skip all the fields and the records you are supposed to.
        if record_num!=-1:
            rec_index=fields_records_to_skip+record_num
        else:
            rec_index=fields_records_to_skip+records_in_required_field-1

        return self.submobjects[rec_index]

    def get_field(self, field_num):
        return self.submobjects[field_num]

    def add_field(self,field,field_pos=-1):
        self.unchanged==False

        tabledict=self.tabledict
        cell_height=self.cell_height
        cell_length=self.cell_length
        field_index=len(tabledict)

        if isinstance(field,(Text,TextMobject,TexMobject,DecimalNumber,Integer))==False:
            field=TextMobject(field)

        firstfield=self.submobjects[0]
        new_field_pos=firstfield.get_center()+((len(tabledict)*cell_length/2),0,0)

        field.move_to(new_field_pos)

        self.submobjects=self.submobjects[:field_index] + [field] + self.submobjects[field_index:]
        tabledict[field]=[]
        return field

    def adjust_lines(self):
        tabledict=self.tabledict
        cell_height=self.cell_height
        cell_length=self.cell_length

        vertlines=self.submobjects[-(len(tabledict)-1):]
        lowestmobject=min(self.submobjects[0:len(self.submobjects)-(len(tabledict))],key=lambda m:m.get_y())
        rightestmobject=max(self.submobjects[:len(tabledict)],key=lambda m:m.get_x())
        anims=[]

        for line in vertlines:
            curr_start, curr_end = line.get_start_and_end()
            if line.get_angle()*DEGREES==0:#This only happens when a field has been added, but a vertical separator doesnt exist for it.
                new_end=np.array(
                    curr_end+(rightestmobject.get_x()-curr_end[0]+cell_length/4,0,0)
                    )

                newsep=Line( #This is the vertical separator for the new field.
                start=(rightestmobject.get_center() - (cell_length/4,-cell_height/4,0)),
                end =(rightestmobject.get_center() - (cell_length/4,+rightestmobject.get_y()-lowestmobject.get_y()+cell_height/4,0)),
                color=self.line_color)

                anims.append(ShowCreation(newsep))
                self.add(newsep)
            else:
                new_end=np.array(
                    (curr_end)+(0,lowestmobject.get_y()-curr_end[1]-cell_height/4,0)
                    )

            new_line=Line(curr_start,new_end,color=self.line_color)
            anims.append(Transform(line,new_line)) #Set the new bottom to the required position
        return AnimationGroup(*anims)

    def adjust_positions(self):
            cell_height=self.cell_height
            tabledict=self.tabledict
            fields=tabledict.keys()
            anim_list=[]

            #VERY VERY TACKY. MUST CHANGE:
            class TempData(): #I mean, really? Thats a performance hog if I've ever seen one...
                pos_to_comp=0
                records=[]


            for field in fields:
                TempData.records=tabledict[field]
                TempData.pos_to_comp=field.get_center()

                for record in TempData.records:
                    if np.abs(record.get_center()[1]-TempData.pos_to_comp[1])>cell_height: #if the distance between two records #greater than one cell height
                        TempData.pos_to_comp=record.get_center()  #Set the position to compare

                        anim_list.extend(
                            [record.shift,(UP*cell_height/2)]
                            )

                        del record
                    else:
                        TempData.pos_to_comp=record.get_center()


            return ApplyMethod(*anim_list)
