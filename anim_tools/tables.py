import warnings
from typing import *

from manim.utils.iterables import list_update
from manim.animation.creation import ShowCreation
from manim.animation.transform import Transform, ApplyMethod
from manim.animation.composition import AnimationGroup
from manim.mobject.types.vectorized_mobject import VGroup
from manim.mobject.geometry import Line
from manim.mobject.svg.tex_mobject import MathTex, Tex
from manim.mobject.svg.text_mobject import Text
from manim.mobject.numbers import DecimalNumber, Integer
import manim.utils.color as C
from manim.constants import *


class Table(VGroup):

    def __init__(self, tabledict, **kwargs):
        super().__init__()

        self.config = {
            "data": tabledict,
            "vbuff_length": 0.3,
            "hbuff_length": 0.3,
            "buff_length": 0.3,
            "line_color": C.WHITE,
            "raw_string_color": C.WHITE,
        }

        self.config.update(kwargs)

        self.data = tabledict

        self.buff_length = self.config["buff_length"]
        self.vbuff_length = self.config["vbuff_length"]
        self.hbuff_length = self.config["hbuff_length"]

        self.line_color = self.config["line_color"]
        self.raw_string_color = self.config["raw_string_color"]

        self._draw_table()  # Make the table with the parameters in config
        self.move_to(ORIGIN)

    def _draw_table(self):
        # if the headers and columns are not manim objects, convert them
        self._type_convert_table_header()
        self._type_convert_table_columns()

        self._set_dimensions()

        self._draw_headers()
        self._draw_columns()
        self._draw_table_lines()

    def _type_convert_table_header(self):
        for key in self.data.keys():
            if isinstance(key, (float, int)):
                key = str(key)

            if isinstance(key, (MathTex, Text, DecimalNumber, Integer)) == False:
                self.data[MathTex(
                    key, fill_color=self.raw_string_color)] = self.data.pop(key)

    def _type_convert_table_columns(self):
        def convert(val):
            if isinstance(val, (float, int)):
                val = str(val)
            if isinstance(val, (MathTex, Text, DecimalNumber, Integer)) == False:
                return Tex(val, fill_color=self.raw_string_color)
            return val

        for key, vals in self.data.items():
            self.data[key] = list(map(convert, vals))

    def _set_dimensions(self):
        fields = list(self.data.keys())
        # find the max width and height across all headers and row items
        dims = [(i.get_width(), i.get_height())
                for column in self.data.values() for i in column] + \
            [(i.get_width(), i.get_height()) for i in fields]

        max_width, max_height = map(max, map(list, zip(*dims)))

        self.cell_length = max_width + 2*self.hbuff_length
        self.cell_height = max_height + 2*self.vbuff_length

        # The remaining width and height will be successively added
        self.table_width = (self.cell_length*len(fields))
        # while drawing the Mobjects to the screen. +1 is added to account for headings.
        self.table_height = self.cell_height * \
            (max(map(len, self.data.values())))+1

    def _draw_headers(self):
        # Coordinates of TexMobjects in Manim are taken from centre, hence the /2 in the calculations below
        def buffer(x): return (self.cell_length-x)/2

        # The initial position of the first field.
        field_position = [
            self.cell_length / 2,
            0,
            0]
        fields = list(self.data.keys())
        for field, next in zip(fields, fields[1:] + [MathTex("")]):
            field.move_to(field_position)
            self.add(field)

            # calculate the next field's position
            right_buf, next_left_buf = buffer(field.get_width()), buffer(next.get_width())
            space_to_leave = right_buf + next_left_buf + next.get_width()/2

            # next/2: coordinates are taken from center and not left edges

            field_position = field.get_right()+(space_to_leave, 0, 0)

    def _draw_columns(self):
        for key, records in self.data.items():
            for record in records:
                # the record position is set to be the
                # [
                #     center of the field it belongs to,
                #     buffer space above the record + centered height of the record,
                #     0
                # ]

                record_position = [
                    key.get_center()[0],
                    -(self.cell_height / 2 + self.cell_height),
                    0]
                for record in records:
                    record.move_to(record_position)
                    record_position = record.get_center()+(0, - self.cell_height, 0)
                    self.add(record)

    def _draw_table_lines(self):
        fields = list(self.data.keys())

        line_hor = Line(start=(0, -2*self.cell_height/3, 0),
                        end=(self.table_width, -2*self.cell_height/3, 0), color=self.line_color)
        self.add(line_hor)  # This is the horizontal separator

        for l in range(len(fields)-1):  # These create the vertical separators.
            line = Line(start=(self[l].get_center() + (self.cell_length/2, self.cell_height/2, 0)),
                        end=(self[l].get_center() +
                             (self.cell_length/2, -self.table_height, 0)),
                        color=self.line_color)

            self.add(line)

    def add_record(self, record, field_num, record_pos=-1):
        orig_submob_list = list(self.submobjects)
        records_in_required_field = len(
            self.data[list(self.data.keys())[field_num]])
        records_to_skip = 0

        if isinstance(record, (MathTex, Text, DecimalNumber, Integer)) == False:
            record = Tex(record)  # Mandatory Type Conversions

        for i in range(0, field_num):  # Until you reach the field where the record should be added
            # skip the records in the field
            records_to_skip += len(
                self.data[list(self.data.keys())[i]])

        # Skip all the fields and the records you are supposed to.
        fields_records_to_skip = len(self.data.keys()) + records_to_skip

        if record_pos != -1:  # If a custom record postion is given
            warnings.warn(
                "Custom Record Positions are still in Development. May give unwanted results.")
            rec_index = fields_records_to_skip+record_pos  # put the record there
        else:
            # Go to the end of the field and put the record there.
            rec_index = fields_records_to_skip+records_in_required_field

        assigned_field = list(self.data.keys())[field_num]

        # 1 is added for field name 0.5 is added for half record width
        vert_num = len(
            self.data[list(self.data.keys())[field_num]])+1+0.5

        how_far_down = vert_num*self.cell_height/2  # How far down to move.

        # Move the record to the assigned fields x coord and move required amount down
        record.move_to(assigned_field.get_center()-(0, how_far_down, 0))

        if record_pos == -1:
            self.data[list(self.data.keys())[
                field_num]].append(record)
        else:
            self.data[list(self.data.keys())[field_num]].insert(
                record_pos, record)  # add the record to tabledict

        # make the new submob list and insert record at propre place.
        new_submob_list = orig_submob_list[:rec_index] + \
            [record] + orig_submob_list[rec_index:]

        self.submobjects = list_update(
            self.submobjects, new_submob_list)  # update self

        return record

    def remove_record(self, field_num, record_num):
        orig_submob_list = list(self.submobjects)
        records_in_required_field = len(
            self.data[list(self.data.keys())[field_num]])
        records_to_skip = 0

        for i in range(0, field_num):  # Until you reach the field where the record should be added
            # skip the records in the field
            records_to_skip += len(
                self.data[list(self.data.keys())[i]])

        # Skip all the fields and the records you are supposed to.
        fields_records_to_skip = len(self.data.keys()) + records_to_skip
        if record_num != -1:
            rec_index = fields_records_to_skip+record_num
        else:
            rec_index = fields_records_to_skip+records_in_required_field-1

        self.data[list(self.data.keys())[field_num]].pop(
            record_num)  # remove the value from tabledict

        return self.submobjects.pop(rec_index)

    def get_record(self, field_num, record_num):
        orig_submob_list = list(self.submobjects)
        records_in_required_field = len(
            self.data[list(self.data.keys())[field_num]])
        records_to_skip = 0

        for i in range(0, field_num):  # Until you reach the field where the record should be added
            # skip the records in the field
            records_to_skip += len(
                self.data[list(self.data.keys())[i]])

        # Skip all the fields and the records you are supposed to.
        fields_records_to_skip = len(self.data.keys()) + records_to_skip
        if record_num != -1:
            rec_index = fields_records_to_skip+record_num
        else:
            rec_index = fields_records_to_skip+records_in_required_field-1

        return self.submobjects[rec_index]

    def get_field(self, field_num):
        return self.submobjects[field_num]

    def add_field(self, field, field_pos=-1):
        tabledict = self.data
        cell_height = self.cell_height
        cell_length = self.cell_length
        field_index = len(tabledict)

        if isinstance(field, (Text, MathTex, DecimalNumber, Integer)) == False:
            field = Tex(field)

        firstfield = self.submobjects[0]
        new_field_pos = firstfield.get_center()+((len(tabledict)*cell_length/2), 0, 0)

        field.move_to(new_field_pos)

        self.submobjects = self.submobjects[:field_index] + \
            [field] + self.submobjects[field_index:]
        tabledict[field] = []
        return field

    def adjust_lines(self):
        tabledict = self.data
        cell_height = self.cell_height
        cell_length = self.cell_length

        vertlines = self.submobjects[-(len(tabledict)-1):]
        lowestmobject = min(self.submobjects[0:len(
            self.submobjects)-(len(tabledict))], key=lambda m: m.get_y())
        rightestmobject = max(
            self.submobjects[:len(tabledict)], key=lambda m: m.get_x())
        anims = []

        for line in vertlines:
            curr_start, curr_end = line.get_start_and_end()
            # This only happens when a field has been added, but a vertical separator doesnt exist for it.
            if line.get_angle()*DEGREES == 0:
                new_end = np.array(
                    curr_end+(rightestmobject.get_x() -
                              curr_end[0]+cell_length/4, 0, 0)
                )

                newsep = Line(  # This is the vertical separator for the new field.
                    start=(rightestmobject.get_center() - \
                           (cell_length/4, -cell_height/4, 0)),
                    end=(rightestmobject.get_center() - (cell_length/4, + \
                                                         rightestmobject.get_y()-lowestmobject.get_y()+cell_height/4, 0)),
                    color=self.line_color)

                anims.append(ShowCreation(newsep))
                self.add(newsep)
            else:
                new_end = np.array(
                    (curr_end)+(0, lowestmobject.get_y() -
                                curr_end[1]-cell_height/4, 0)
                )

            new_line = Line(curr_start, new_end, color=self.line_color)
            # Set the new bottom to the required position
            anims.append(Transform(line, new_line))
        return AnimationGroup(*anims)

    def adjust_positions(self):
        cell_height = self.cell_height
        tabledict = self.data
        fields = tabledict.keys()
        anim_list = []

        # VERY VERY TACKY. MUST CHANGE:
        class TempData():  # I mean, really? Thats a performance hog if I've ever seen one...
            pos_to_comp = 0
            records = []

        for field in fields:
            TempData.records = tabledict[field]
            TempData.pos_to_comp = field.get_center()

            for record in TempData.records:
                # if the distance between two records #greater than one cell height
                if np.abs(record.get_center()[1]-TempData.pos_to_comp[1]) > cell_height:
                    TempData.pos_to_comp = record.get_center()  # Set the position to compare

                    anim_list.extend(
                        [record.shift, (UP*cell_height/2)]
                    )

                    del record
                else:
                    TempData.pos_to_comp = record.get_center()

        return ApplyMethod(*anim_list)
