bl_info = {
    "name": "URDF Exporter",
    "description": "Exports Blender files to URDF format",
    "author": "@byrondavid",
    "blender": (3, 5, 0),
    "location": "3D View > Tools",
}

import bpy
from bpy.props import (
    StringProperty,
    FloatProperty,
    BoolProperty,
    IntProperty,
    EnumProperty,
    PointerProperty,
)
from bpy.types import (
    Operator,
    PropertyGroup,
)
from bpy.props import *
from lxml import etree as ET
from pathlib import Path
import mathutils

scene = bpy.context.scene
collision_name = ""

class ExportObj:
    meshes = []

    def export_obj(
        self,
        file_path,
        obj,
        materials=True,
        path_mode="AUTO",
        groups=True,
        sep_obj=False,
    ):
        if obj.properties.primitive == "mesh":
            bpy.ops.export_scene.obj(
                filepath="{}{}.obj".format(file_path, obj.name),
                use_blen_objects=sep_obj,
                group_by_object=groups,
                use_selection=True,
                use_triangles=True,
                use_normals=True,
                use_uvs=True,
                use_materials=materials,
                path_mode=path_mode,
                axis_forward="Y",
                axis_up="Z",
            )

    def export(self):
        bpy.ops.object.select_all(action="DESELECT")

        for mesh in self.meshes:
            # duplicate mesh
            new_object = BlenderObject.copy_object(self, mesh)

            print(new_object)

            # select object mesh
            new_object.select_set(True)

            exporter.export_obj(file.path, mesh, materials=False)

            # delete copied object
            bpy.ops.object.delete()


class BlenderObject:
    obj_attributes = {
        "link": None,
        "mass": None,
        "origin": None,
        "pos": None,
        "size": None,
        "class": None,
        "material": None,
    }

    def __init__(self, obj):
        self.obj = obj
        self.location = self.vector_to_string(self.obj.location)
        self.rotation = self.vector_to_string(self.obj.rotation_euler)
        self.size = self.vector_to_string(self.obj.scale)
        self.sphere_size = str(round(self.obj.scale[0], 4))
        self.cylinder_size = self.vector_to_string(self.obj.scale[1:3])

    def get_base_obj_name(self):
        for obj in bpy.data.objects:
            if obj.type == "EMPTY":
                if obj.parent == None:
                    return obj.name

    def get_object_attributes(self):
        self.clear_attributes()

        if (
            self.obj.properties.mujoco_type == "GEOM"
            and self.obj.properties.primitive == "mesh"
        ):
            self.obj_attributes["mesh"] = self.obj.name
            self.obj_attributes["pos"] = self.location
            self.obj_attributes["euler"] = self.rotation
            # self.obj_attributes["material"] = self.obj.name

        if self.obj.properties.mujoco_type == "GEOM":
            self.obj_attributes["type"] = self.obj.properties.primitive
            self.obj_attributes["euler"] = self.rotation
            self.obj_attributes["pos"] = self.location
            # self.obj_attributes["material"] = self.obj.name

            # box and ellipsoid primitive mesh
            if (
                self.obj.properties.primitive == "box"
                or self.obj.properties.primitive == "ellipsoid"
            ):
                self.obj_attributes["size"] = self.size

            # Capsule and Cylinder primitive mesh
            if (
                self.obj.properties.primitive == "cylinder"
                or self.obj.properties.primitive == "capsule"
            ):
                self.obj_attributes["size"] = self.cylinder_size

            # Sphere primitive mesh
            if self.obj.properties.primitive == "sphere":
                self.obj_attributes["size"] = self.sphere_size

        if (
            self.obj.properties.mujoco_type == "COLLISION"
            or self.obj.properties.is_collision == True
        ):
            self.obj_attributes["type"] = self.obj.properties.primitive
            self.obj_attributes["euler"] = self.rotation
            self.obj_attributes["pos"] = self.location
            self.obj_attributes["class"] = "collision"

            if self.obj.properties.primitive == "mesh":
                self.obj_attributes["mesh"] = self.obj.name

            if (
                self.obj.properties.primitive == "box"
                or self.obj.properties.primitive == "ellipsoid"
            ):
                self.obj_attributes["size"] = self.size

            if (
                self.obj.properties.primitive == "cylinder"
                or self.obj.properties.primitive == "capsule"
            ):
                self.obj_attributes["size"] = self.cylinder_size

            # Sphere collision
            if self.obj.name and self.obj.properties.primitive == "sphere":
                self.obj_attributes["size"] = self.sphere_size

    def clear_attributes(self):
        self.obj_attributes = {
            "type": None,
            "mesh": None,
            "euler": None,
            "pos": None,
            "size": None,
            "class": None,
            "material": None,
        }

    def copy_object(self, object):
        """Duplicate mesh object"""
        object_name = bpy.data.objects[object.name]

        # copy object
        new_object = object_name.copy()
        new_object.data = object_name.data.copy()

        new_object.animation_data_clear()
        bpy.context.collection.objects.link(new_object)

        # select new object
        bpy.data.objects[new_object.name].select_set(True)

        # clear parent
        bpy.ops.object.parent_clear(type="CLEAR")

        # set transforms to 0
        new_object.location = (0, 0, 0)
        new_object.rotation_euler = (0, 0, 0)

        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

        return bpy.data.objects[new_object.name]

    def vector_to_string(self, obj_vector):
        """Get XYZ data and convert it to "x y z" format."""
        vectors = ""

        for v in obj_vector:
            v = round(v, 4)
            if (v == 0.0) or (v == -0.0):
                v = 0
            else:
                pass
            vectors += str(v) + " "

        if vectors[:-1] == "0 0 0":
            return None

        else:
            return str(vectors[:-1])

    def joint_axis(self):
        if self.obj.joint_axis == "X":
            return "1 0 0"
        elif self.obj.joint_axis == "Y":
            return "0 1 0"
        else:
            return "0 0 1"


def radians_to_degrees(degree):
    radian = degree / 57.32
    return radian


class XML:
    worldbody = ""

    def __init__(self, root):
        self.root = root

    def add_attribute(self, body, attribute_name, attribute):
        body.set(attribute_name, attribute)

    def pretty(self, root):
        return ET.ElementTree(root)

    def element_attributes(self, **kwargs):
        return {k: v for k, v in kwargs.items() if v is not None or v}

    def write_main_xml(self):
        mytool = scene.my_tool
        for obj in bpy.data.objects:
            if obj.properties.primitive == "mesh" and mytool.export_files == True:
                ExportObj.meshes.append(obj)

            if obj.properties.mujoco_type == "LINK" and obj.parent == None:
                file_name = file.path + obj.name + ".xml"

                self.add_attribute(self.root, "model", file.name)
                self.write_depend_link(obj)

                # asset = ET.SubElement(
                #     self.worldbody, "include", file="assets/" + obj.name + ".xml"
                # )

                # include = ET.SubElement(
                #     self.worldbody,
                #     "include",
                #     file="assets/" + file.name + "_dependencies.xml",
                # )

                self.worldbody = ET.SubElement(self.root, "worldbody")
                main_body = ET.SubElement(
                    self.worldbody, "body", attrib={"childclass": obj.name}
                )
                self.mujoco_body_link(main_body, obj, None)

                # floor = ET.SubElement(worldbody, "geom", name = 'floor', size = '10 10 .0075', type = 'plane',  condim = '3')

                tree = self.pretty(self.root)
                tree.write(file_name, pretty_print=True)

        return {"FINISHED"}

    def urdf_joint(self, robot, obj, obj_loc, obj_rot):
        if obj.parent:
            if obj.joint_type == "None":
                pass
            else:
                joint = ET.SubElement(
                    robot, "joint", name="joint_" + obj.name, type=str(obj.joint_type)
                )
                parent = ET.SubElement(joint, "parent", link=obj.parent.name)
                child = ET.SubElement(joint, "child", link=obj.name)
                origin = ET.SubElement(joint, "origin", xyz=obj_loc, rpy=obj_rot)
                if (obj.joint_type == "prismatic") or (obj.joint_type == "revolute"):
                    axis = ET.SubElement(
                        joint, "axis", xyz=blender_object.joint_axis(obj)
                    )
                    limit = ET.SubElement(
                        joint,
                        "limit",
                        effort="0",
                        lower=str(obj.lower_limit),
                        upper=str(obj.upper_limit),
                        velocity="1",
                    )

    def urdf_body_link(self, previous_body, obj, parent):
        """Create Body, Geom and Joint data in XML"""
        blend_obj = BlenderObject(obj)

        if parent == None:
            body = ET.SubElement(
                previous_body,
                "body",
                attrib=self.element_attributes(
                    name=obj.name,
                    pos=blend_obj.location,
                    euler=blend_obj.rotation,
                ),
            )
        else:
            link_loc = (
                parent.matrix_world.inverted() @ obj.matrix_world.to_translation()
            )

            body = ET.SubElement(
                previous_body,
                "body",
                attrib=self.element_attributes(
                    name=obj.name,
                    pos=blend_obj.vector_to_string(link_loc),
                    euler=blend_obj.rotation,
                ),
            )


        # if obj.properties.mujoco_joint == True:
        #     self.create_joint(body, obj)

        for child in obj.children:
            blend_child = BlenderObject(child)
            blend_child.get_object_attributes()

            ## CLEAN Up ##
            if parent != None:
                true_loc = (
                    obj.matrix_world.inverted() @ child.matrix_world.to_translation()
                )

                blend_child.obj_attributes["pos"] = blend_obj.vector_to_string(true_loc)
            ## CLEAN UP ###
            material = None

            # make sure object has materials
            if child.type == "EMPTY" or child.properties.primitive == None:
                pass
            elif child.data.materials:
                blend_child.obj_attributes["material"] = child.data.materials[0].name

            if (
                child.properties.mujoco_type == "GEOM"
                or child.properties.mujoco_type == "COLLISION"
            ):
                geom = ET.SubElement(
                    body,
                    "geom",
                    attrib=self.element_attributes(**blend_child.obj_attributes),
                )

        # Additional loop added for correct ordering in xml
        for child in obj.children:
            if child.properties.mujoco_type == "LINK":
                self.mujoco_body_link(body, child, obj)

    def write_depend_link(self, obj):
        blend_obj = BlenderObject(obj)
        compiler = ET.SubElement(
            self.root,
            "compiler",
            inertiafromgeom="auto",
            inertiagrouprange="4 4",
            angle="radian",
        )
        size = ET.SubElement(self.root, "size", njmax="1000", nconmax="500")
        default_materials = True
        asset = ET.SubElement(self.root, "asset")
        new_material = ET.SubElement(
            asset,
            "material",
            name="collision",
            rgba="0.3 0.3 1 0.5",
        )

        # for image in bpy.data.images:
        #     if ".png" in image.name:
        #         new_texture = ET.SubElement(
        #             asset,
        #             "texture",
        #             name=image.name,
        #             type="cube",
        #             height="1",
        #             width="1",
        #             file=image.name,
        #         )

        for material in bpy.data.materials:
            if material.name == "Dots Stroke":
                pass
            elif material.name != "collision":
                new_material = ET.SubElement(
                    asset,
                    "material",
                    attrib=self.element_attributes(
                        name=material.name,
                        shininess=str(material.specular_intensity),
                        rgba=blend_obj.vector_to_string(material.diffuse_color),
                    ),
                )

        visual = ET.SubElement(self.root, "visual")
        map = ET.SubElement(
            visual, "map", fogstart="1.5", fogend="5", force="0.1", znear="0.1"
        )
        quality = ET.SubElement(visual, "quality", shadowsize="16384", offsamples="24")
        map = ET.SubElement(visual, "global", offwidth="800", offheight="800")

        default = ET.SubElement(self.root, "default")
        default_class = ET.SubElement(default, "default", attrib={"class": obj.name})
        joint = ET.SubElement(
            default_class, "joint", attrib={"limited": "true", "damping": "1"}
        )
        geom_basecol = ET.SubElement(
            default_class,
            "geom",
            attrib={
                "contype": "0",
                "conaffinity": "0",
                "group": "1",
                "type": "mesh",
            },
        )
        position = ET.SubElement(
            default_class, "position", attrib={"ctrllimited": "true"}
        )
        collision = ET.SubElement(
            default_class,
            "default",
            attrib={"class": "collision"},
        )
        geom_collision = ET.SubElement(
            collision,
            "geom",
            attrib={
                "contype": "1",
                "conaffinity": "1",
                "condim": "4",
                "group": "4",
                "material": "collision",
            },
        )

        # within all 3d models
        for obj in bpy.data.objects:
            if (
                obj.properties.mujoco_type == "GEOM"
                and obj.properties.primitive == "mesh"
            ):
                obj_asset_name = obj.name + ".obj"
                asset2 = ET.SubElement(
                    asset, "mesh", name=obj.name, file=obj_asset_name
                )

            if obj.properties.mujoco_joint == True:
                actuators = ET.SubElement(self.root, "actuator")
                joint_name = obj.mujoco_joint_name
                range = (
                    round(radians_to_degrees(obj.joint_range_min), 4),
                    round(radians_to_degrees(obj.joint_range_max), 4),
                )
                actuator = ET.SubElement(
                    actuators,
                    "position",
                    attrib={
                        "name": obj.name,
                        "kp": "2",
                        "joint": joint_name,
                        # "class": bpy.context.scene.mujoco_name,
                        "ctrlrange": blend_obj.vector_to_string(range),
                    },
                )
            else:
                pass


class FileStructure:
    def __init__(self, path):
        self.path = path
        self.name = ""
        self.directory = ""

    def file_name(self):
        self.name = Path(self.path).stem

    def file_directory(self):
        self.directory = Path(self.path).parent


class MUJOCO_BUTTON(Operator):
    """Exports XML file in Mujoco format."""

    bl_idname = "mujoco_panel.button"
    bl_label = "Export XML"

    # ExportHelper mixin class uses this
    # filename_ext = ".xml"

    # filter_glob: StringProperty(
    #     default="*.xml",
    #     options={"HIDDEN"},
    #     maxlen=255,  # Max internal buffer length, longer would be clamped.
    # )
    # split_files: BoolProperty(
    #     name="Export Separate Files",
    #     description="Split multiple objects into separate xml files",
    #     default=False,
    # )

    def execute(self, context):
        mytool = scene.my_tool

        file.path = bpy.path.abspath(mytool.my_path)
        file.file_directory()
        file.file_name()

        xml = XML(ET.Element("mujoco"))
        xml.write_main_xml()

        exporter.export()
        return {"FINISHED"}


class MUJOCO_PT_PANEL(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Mujcoo"
    bl_label = "Mujcoo Export"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        # scn = context.scene
        mytool = scene.my_tool
        obj_data = obj.properties

        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        col = layout.column()

        subcol = col.column()

        layout.prop(obj, "name")
        layout.prop(obj_data, "mujoco_type")
        if obj_data.mujoco_type == "COLLISION":
            layout.prop(obj_data, "primitive")
        if obj_data.mujoco_type == "GEOM":
            layout.prop(obj_data, "primitive")
            layout.prop(obj_data, "is_collision")
        if obj_data.mujoco_type == "LINK":
            layout.prop(obj_data, "mujoco_joint")
        if obj_data.mujoco_joint == True:
            layout.prop(obj_data, "joint_type")
            layout.prop(obj_data, "mujoco_joint_name")
            layout.prop(obj_data, "joint_direction")
            layout.prop(
                obj_data,
                "joint_range_min",
            )
            layout.prop(obj_data, "joint_range_max")

        layout.prop(mytool, "export_files")

        layout.prop(mytool, "my_path")

        layout.operator("mujoco_panel.button")


class MyObjectProperties(PropertyGroup):
    joint_type: EnumProperty(
        name="Joint type",
        items=[
            ("None", "None", "None"),
            ("fixed", "fixed", "fixed"),
            ("revolute", "revolute", "revolute"),
            ("prismatic", "prismatic", "prismatic"),
        ],
    )

    joint_axis: EnumProperty(
        name="Joint axis", items=[("X", "X", "X"), ("Y", "Y", "Y"), ("Z", "Z", "Z")]
    )

    lower_limit: FloatProperty(
        name="Lower Limit",
        description="Minimum range of joint",
        default=0
    )

    upper_limit: FloatProperty(
        name="Upper Limit",
        description="Maximum range of joint",
        default=0
    )

    file_name: StringProperty(
        name="Robot's name:", 
        default="robot"
    )

    is_collision: BoolProperty(
        name="Is Collision", description="Mesh is collision", default=False
    )

    mujoco_joint: BoolProperty(
        name="Mujoco Joint", description="Adds Mujoco joint", default=False
    )

    mujoco_type: EnumProperty(
        name="Mujoco Type",
        items=[
            ("NONE", "None", "Not Specified"),
            ("LINK", "Link", "Mujoco Body"),
            ("GEOM", "Geometry", "Mesh Geometry"),
            ("LIGHT", "Light", "Mujoco Light"),
            ("COLLISION", "Collision", "Mujoco Primitive Collision"),
            ("SITE", "Site", "Mujoco Site"),
        ],
    )

    primitive: EnumProperty(
        name="Primitive",
        items=[
            ("box", "Box", "Mujoco Box Primitive"),
            ("mesh", "Mesh", "Mesh.obj"),
            ("cylinder", "Cylinder", "Mujoco Cylinder Primitive"),
            ("capsule", "Capsule", "Mujoco Capsule Primitive"),
            ("sphere", "Sphere", "Mujoco Sphere Primitive"),
            ("ellipsoid", "Ellipsoid", "Mujoco Ellipsoid Primitive"),
        ],
    )

    joint_type: EnumProperty(
        name="Joint Type",
        items=[
            ("HINGE", "Hinge", "Mujoco Hinge Joint"),
            ("SLIDE", "Slide", "Mujoco Slide Joint"),
            ("BALL", "Ball", "Mujoco Ball Joint"),
        ],
    )

    joint_direction: EnumProperty(
        name="ZYX",
        items=[("X", "X", "X axis"), ("X", "Y", "Y axis"), ("X", "Z", "Z axis")],
    )

    mujoco_joint_name: StringProperty(
        name="Joint Name", description="Name joint:", default="", maxlen=1024
    )

    joint_range_min: IntProperty(
        name="Min Range",
        description="Minimum range of joint",
        default=0,
    )

    joint_range_max: IntProperty(
        name="Max Range",
        description="Maximum range of joint",
        default=0,
    )


class MyProperties(PropertyGroup):
    export_files: BoolProperty(
        name="Export OBJ Files", 
        description="Exports OBJ files with XML", default=False
    )

    my_path: StringProperty(
        name="Directory",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype="DIR_PATH",
    )


file = FileStructure(None)
exporter = ExportObj()

# Class regiistration (Blender 2.8+)
classes = (
    MyProperties,
    MyObjectProperties,
    MUJOCO_PT_PANEL,
    MUJOCO_BUTTON,
)


def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)
    bpy.types.Object.properties = PointerProperty(type=MyObjectProperties)


def unregister():
    from bpy.utils import unregister_class

    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool
    del bpy.types.Object.properties


if __name__ == "__main__":
    register()
