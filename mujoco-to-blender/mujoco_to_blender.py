import lxml
from lxml import etree
from pathlib import Path
import bpy

objects = bpy.data.objects
import_path = Path(
    'C:\\Users\\byrondavid\\Documents\\Adept\\proco\\50_tools\\chisel1\\')
base_path = bpy.path.abspath('//')
file_name = bpy.context.selected_objects[0].name
file_path = base_path + 'export\\' + file_name
export_folder = base_path + 'export'


class Mesh_info:
    def __init__(self, textures, meshes, geoms):
        self.textures = textures
        self.meshes = meshes
        self.geoms = geoms


def parse_xml(name):
    join_path = Path(base_path) / name
    parse = etree.parse(str(join_path))
    return parse


root = parse_xml(path)


def find_path(root, loc, file_path):
    path_list = []
    for pos in root.xpath(".//{}[@{}]" .format(loc, file_path)):
        path_list.append(pos.attrib[file_path])
    return path_list


def find_path_name(root, loc, attr1, attr2):
    path_list = []
    for pos in root.xpath(".//{}[@{} and @{}]" .format(loc, attr1, attr2,)):
        path_list.append(pos.attrib[attr2])
    return path_list


def path_join_list(base_path, path_list):
    path_join = []
    for p in path_list:
        path_join.append(Path.home() / base_path / p)
    return path_join


path_list = find_path(root, 'include', 'file')


def get_geom(root, geom):
    '''get geom data and return a dict.'''
    b_count = 0
    geom_dict = {}

    for f in path_join_list(base_path, path_list):
        root = parse_xml(f)

        for b in root.xpath("//body"):
            g_count = 0
            geom_list = []
            body_count = 'body' + str(b_count)
            geom_list.append(b.attrib)
            geom_dict.update({body_count: b.attrib})
            b_count += 1

            for g in b:
                if g.tag == 'geom':
                    geom_count = body_count + 'geom' + str(g_count)
                    geom_list.append({geom_count: g.attrib})
                    geom_dict[body_count] = geom_list
                    g_count += 1
                else:
                    pass

    return geom_dict


def parent_obj(obj_0, obj_1):
    '''parent object'''
    # deselect all object
    bpy.ops.object.select_all(action='DESELECT')

    # select the object for the 'parenting'
    obj_0.select_set(True)
    obj_1.select_set(True)

    # the active object will be the parent of all selected object
    bpy.context.view_layer.objects.active = obj_0

    bpy.ops.object.parent_set()


def prim_specs(geom_name, body_name, geom_size):
    '''get obj name and parent'''
    obj = bpy.context.selected_objects[0]

    # change name
    obj.name = geom_name
    if len(geom_size) == 3:
        bpy.ops.transform.resize(
            value=(float(geom_size[0]), float(geom_size[1]), float(geom_size[2])))
    elif len(geom_size) == 2:
        bpy.ops.transform.resize(
            value=(float(geom_size[0]), float(geom_size[0]), float(geom_size[1])))
    else:
        bpy.ops.transform.resize(
            value=(float(geom_size[0]), float(geom_size[0]), float(geom_size[0])))

    g_0 = objects[body_name]
    g_1 = objects[geom_name]

    parent_obj(g_0, g_1)


geoms = get_geom(root, 'geom')
mesh_spec = Mesh_info(textures, meshes, geoms)
get_geom(root, 'geom')
