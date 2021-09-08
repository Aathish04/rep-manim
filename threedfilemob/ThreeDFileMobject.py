from manim import *
from os import path


class OBJVMobject(VGroup):
    # TODO: Colours; Free-form curves/surfaces; smoothing groups

    def _parse_obj_file(self):
        isint = lambda s: s.isdigit() or (s.startswith("-") and s[1:].isdigit())

        groups = None  # Not all obj files specify groups. Set default group to None
        material = WHITE  # Default material is white in colour.
        for line in self.textlines:
            if line.startswith("#") or len(line.strip()) == 0:
                continue
            linedata = line.split()

            if linedata[0] == "v":
                self.vertices.append(list(map(float, linedata[1:4])))
            elif linedata[0] == "vn":
                self.vertex_normals.append(list(map(float, linedata[1:4])))
            elif linedata[0] == "vt":
                self.texture_vertices.append(list(map(float, linedata[1:4])))
            elif linedata[0] == "g":
                groups = (
                    linedata[1:] if len(linedata) > 1 else None
                )  # If no group names are mentioned use None.
            elif linedata[0] == "usemtl":
                material = linedata[1]
            elif linedata[0] == "f":
                face_info = {"group": groups, "material": material}
                face_info["vertices"] = [
                    {
                        ("vertex", "texture_vertex", "vertex_normal")[i]: (
                            self.vertices,
                            self.texture_vertices,
                            self.vertex_normals,
                        )[i][
                            int(index) - 1 if int(index) >= 1 else int(index)
                        ]  # Indexing starts from 1. Reverse indexing also possible.
                        if isint(index)
                        else None
                        for i, index in enumerate(text_vertex_data.split("/"))
                    }
                    for text_vertex_data in linedata[1:]
                ]
                self.faces_info.append(face_info)

    def _build_faces(self):
        for face_info in self.faces_info:
            vertex_list = [
                face_vertex["vertex"] for face_vertex in face_info["vertices"]
            ]
            face = ThreeDVMobject().set_points_as_corners(
                vertex_list + [vertex_list[0]]
            )
            self.add(face)

    def __init__(self, fp, **kwargs):

        VGroup.__init__(self, **kwargs)

        self.vertices = []
        self.vertex_normals = []
        self.texture_vertices = []

        self.faces_info = []
        with open(fp, "r") as f:
            self.textlines = f.readlines()

        self._parse_obj_file()
        self._build_faces()

        self.set_fill(color=DARK_BLUE, opacity=0.6)
        self.set_stroke(
            color=RED,
            width=0,
            opacity=0.8,
        )


class Test(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(
            phi=-45 * DEGREES, theta=-135 * DEGREES, gamma=-55 * DEGREES
        )
        filename = "coloured/airboat/airboat.obj"
        model = OBJVMobject(
            path.abspath(
                path.dirname(__file__) + path.sep + "ref_models" + path.sep + filename
            )
        ).shift(UP * 0.5)
        with open(
            "/Users/aathishs/Projects/Python/ManimStuff/rep-manim/threedfilemob/ThreeDFileMobject.json",
            "w",
        ) as f:
            import json

            json.dump(model.faces_info, f)
        self.add(model)
