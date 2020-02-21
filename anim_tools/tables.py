import warnings

from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.iterables import list_update
from manimlib.mobject.svg.tex_mobject import TexMobject
from manimlib.mobject.svg.tex_mobject import TextMobject
from manimlib.mobject.svg.text_mobject import Text
from manimlib.mobject.geometry import Line
from manimlib.constants import *

class Tools():
    def flatten(inlist):
        outlist=[]
        for element in inlist:
            for sub_element in element:
                outlist.append(sub_element)
        return outlist



class Table(VGroup): #TODO: Responsive Insertions and Deletion Specific Table position insertions.
    CONFIG={
            "tabledict":{},
            "buff_length":0.3,
            "line_color":WHITE,
            "raw_string_color":WHITE,
            "cell_height":0,
            "cell_width":0
        }

    def __init__(self, **kwargs): #__init__ is called everytime Table() is called.
        
        for item in kwargs: #Add everything that has been given in kwargs to the config.
                self.CONFIG[item]=kwargs[item] #Using digest config gave AttributeError: 'dict' object has no attribute '__dict__'
        
        VGroup.__init__(self) #Initialise Table as VGroup
        
        self.make_table() #Make the table with the parameters in CONFIG
    
    def get_table(**kwargs): #DEPRECATED! DO NOT USE
        warnings.warn('''
        Table.get_table() has been deprecated.
        Please use Table(tabledict=<dict>,buff_length=<float/int>,line_color=<HEX/RGB>,raw_string_color=<HEX/RGB>)
        instead. Table.get_table() now returns nothing.''')
    
    def make_table(self):
        #Get values from CONFIG
        tabledict=self.CONFIG["tabledict"]
        buff_length=self.CONFIG["buff_length"]
        line_color=self.CONFIG["line_color"]
        raw_string_color=self.CONFIG["raw_string_color"]
        
        #self is now the table. so self.add has replaced table.add in this function.
        
        fields=list(tabledict.keys()) #Since the data is recieved as a dict, the keys will be the fields

        #the for loop below checks that every field and record is of a valid type and converts to TextMobject if need be:
        for fieldnum in range(len(fields)):
            
            if isinstance(fields[fieldnum],(TextMobject,TexMobject,Text))==False:
                tabledict[TextMobject(fields[fieldnum],fill_color=raw_string_color)] = tabledict.pop(fields[fieldnum])
            
            fields=list(tabledict.keys())

            for recordnum in range(0,len(tabledict[fields[fieldnum]])):
                if isinstance(tabledict[fields[fieldnum]][recordnum],(TexMobject,TextMobject,Text))==False:
                    tabledict[fields[fieldnum]][recordnum]=TextMobject(tabledict[fields[fieldnum]][recordnum],fill_color=raw_string_color)
                else:
                    continue

        cell_length=( max(fields + Tools.flatten(tabledict.values()), key=lambda mobject:mobject.get_width()) ).get_width() + 2*buff_length #The length/height of a record/field of 
        cell_height=( max(fields + Tools.flatten(tabledict.values()), key=lambda mobject:mobject.get_height()) ).get_height()+ 2*buff_length #max length/height is the base cell size

        self.CONFIG["cell_height"]=cell_height
        self.CONFIG["cell_length"]=cell_length
        
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
            line=Line( start=(self[l].get_center()+ (cell_length/2,cell_height/2,0)), end =(self[l].get_center()+ (cell_length/2,-total_table_height,0)),color=line_color)
            self.add(line)

    def add_record(self,record,field_num,record_pos=-1):
        orig_submob_list=list(self.submobjects)
        records_in_required_field = len(self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]])
        records_to_skip=0

        if isinstance(record,TexMobject)==False and isinstance(record,TextMobject)==False and isinstance(record,Text)==False :
                record=TextMobject(record) #Mandatory Type Conversions


        for i in range(0,field_num): #Until you reach the field where the record should be added
            records_to_skip+=len(self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[i]]) #skip the records in the field
         
        fields_records_to_skip = len(self.CONFIG["tabledict"].keys()) + records_to_skip #Skip all the fields and the records you are supposed to.
        

        if record_pos!=-1: #If a custom record postion is given
            warnings.warn("Custom Record Positions are still in Development. May give unwanted results.")
            rec_index=fields_records_to_skip+record_pos #put the record there
        else:
            rec_index=fields_records_to_skip+records_in_required_field #Go to the end of the field and put the record there.
        
        assigned_field=list(self.CONFIG["tabledict"].keys())[field_num]

        vert_num=len(self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]])+1+0.5 #1 is added for field name 0.5 is added for half record width
        
        how_far_down=vert_num*self.CONFIG["cell_height"]/2 #How far down to move.
        
        record.move_to(assigned_field.get_center()-(0,how_far_down,0)) #Move the record to the assigned fields x coord and move required amount down
        
        if record_pos==-1:
            self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]].append(record) 
        else:
            self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]].insert(record_pos,record) #add the record to tabledict
        
        new_submob_list = orig_submob_list[:rec_index] + [record] + orig_submob_list[rec_index:] #make the new submob list and insert record at propre place.

        self.submobjects = list_update(self.submobjects, new_submob_list) #update self
      
        return record

    def remove_record(self,field_num,record_num):
        orig_submob_list=list(self.submobjects)
        records_in_required_field = len(self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]])
        records_to_skip=0

        for i in range(0,field_num): #Until you reach the field where the record should be added
            records_to_skip+=len(self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[i]]) #skip the records in the field
        
        fields_records_to_skip = len(self.CONFIG["tabledict"].keys()) + records_to_skip #Skip all the fields and the records you are supposed to.
        if record_num!=-1:
            rec_index=fields_records_to_skip+record_num
        else:
            rec_index=fields_records_to_skip+records_in_required_field-1
        
        self.CONFIG["tabledict"][list(self.CONFIG["tabledict"].keys())[field_num]].pop(record_num) #remove the value from tabledict
        
        return self.submobjects.pop(rec_index)

    def adjust_lines(self):
        tabledict=self.CONFIG["tabledict"]
        cell_height=self.CONFIG["cell_height"]

        vertlines=self.submobjects[-(len(tabledict)-1):]
        lowestmobject=min(self.submobjects[0:len(self.submobjects)-(len(tabledict))],key=lambda m:m.get_y())
        anims=[]
        
        for line in vertlines:
            curr_start, curr_end = line.get_start_and_end()
            anims.extend(
                [line.put_start_and_end_on,curr_start,(curr_end+(0,lowestmobject.get_y()-curr_end[1]-cell_height/4,0))] #Set the new bottom to the required position
                )
        
        return anims

    def adjust_positions(self):
            cell_height=self.CONFIG["cell_height"]
            tabledict=self.CONFIG["tabledict"]
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
                        anim_list.extend([record.shift,(UP*cell_height/2)])
                        del record
                    else:
                        TempData.pos_to_comp=record.get_center()
            
            
            return anim_list
