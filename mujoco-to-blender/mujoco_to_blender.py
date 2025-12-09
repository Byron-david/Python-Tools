import bpy
from lxml import etree
from pathlib import Path

# --- 1. SETUP PATHS DYNAMICALLY ---
# Get the folder where the current .blend file is saved
base_path = Path(bpy.path.abspath('//'))

# Ensure a Blender file is actually saved, otherwise this fails
if str(base_path) == '.':
    print("ERROR: Please save your .blend file first so the script knows where to look.")
else:
    print(f"Working in directory: {base_path}")

# Get name from selected object
if bpy.context.selected_objects:
    selected_obj = bpy.context.selected_objects[0]
    file_name = selected_obj.name
else:
    # Fallback if nothing selected
    file_name = "model" 
    print("No object selected. Defaulting to 'model.xml'")

# Construct paths using pathlib (Works on Windows/Mac/Linux)
# Assumes the XML file is named after the object (e.g., "Cube.xml")
main_xml_path = base_path / f"{file_name}.xml"
export_folder = base_path / 'export'

class Mesh_info:
    def __init__(self, textures, meshes, geoms):
        self.textures = textures
        self.meshes = meshes
        self.geoms = geoms

def parse_xml(file_path):
    """Parses XML if file exists."""
    if not file_path.exists():
        print(f"Error: File not found at {file_path}")
        return None
    return etree.parse(str(file_path))

# --- 2. START PARSING ---
root_tree = parse_xml(main_xml_path)
root = root_tree.getroot() if root_tree else None

def find_path(root, loc, attribute_name):
    """Finds attributes in the XML tree."""
    if root is None: return []
    
    path_list = []
    # Use generic xpath to find tags
    for pos in root.xpath(f".//{loc}[@{attribute_name}]"):
        path_list.append(pos.attrib[attribute_name])
    return path_list

def path_join_list(base_folder, relative_paths):
    """Joins the base folder with the relative paths found in XML."""
    full_paths = []
    for p in relative_paths:
        # Correctly joins paths regardless of OS
        full_paths.append(base_folder / p)
    return full_paths

# Find includes (dependencies)
# logic: looks for <include file="..."> inside the XML
include_files = find_path(root, 'include', 'file')
full_include_paths = path_join_list(base_path, include_files)

def get_geom(root, tag_name):
    '''get geom data and return a dict.'''
    if root is None: return {}

    b_count = 0
    geom_dict = {}

    # Process the main file first, then the included files
    # Create a list of all trees to process
    trees_to_process = [root]
    
    # Add included files to the processing list
    for f in full_include_paths:
        tree = parse_xml(f)
        if tree:
            trees_to_process.append(tree.getroot())

    for current_root in trees_to_process:
        for b in current_root.xpath("//body"):
            g_count = 0
            geom_list = []
            body_count = 'body' + str(b_count)
            
            # Store body attributes
            geom_list.append(b.attrib)
            geom_dict.update({body_count: b.attrib})
            b_count += 1

            for g in b:
                if g.tag == tag_name: # usually 'geom'
                    geom_count = body_count + 'geom' + str(g_count)
                    geom_list.append({geom_count: g.attrib})
                    geom_dict[body_count] = geom_list
                    g_count += 1

    return geom_dict

def parent_obj(obj_child, obj_parent):
    '''parent object'''
    bpy.ops.object.select_all(action='DESELECT')
    
    # The parent is the active object
    obj_parent.select_set(True)
    bpy.context.view_layer.objects.active = obj_parent
    
    # The child is selected but not active
    obj_child.select_set(True)
    
    bpy.ops.object.parent_set(type='OBJECT')

def prim_specs(geom_name, body_name, geom_size):
    '''Resize and parent object based on XML data'''
    if not bpy.context.selected_objects:
        return

    obj = bpy.context.selected_objects[0]
    obj.name = geom_name

    # Handle resizing based on how many dimensions are provided
    # Convert string "0.5 0.2" -> list [0.5, 0.2]
    if isinstance(geom_size, str):
        size_values = [float(x) for x in geom_size.split()]
    else:
        size_values = geom_size

    if len(size_values) == 3:
        obj.scale = (size_values[0], size_values[1], size_values[2])
    elif len(size_values) == 2:
        # Capsule/Cylinder logic often uses radius/height
        obj.scale = (size_values[0], size_values[0], size_values[1])
    elif len(size_values) == 1:
        # Sphere logic
        obj.scale = (size_values[0], size_values[0], size_values[0])

    # Try to find the objects in Blender data to parent them
    # Note: This requires the objects to already exist in Blender with these names
    if body_name in bpy.data.objects and geom_name in bpy.data.objects:
        g_parent = bpy.data.objects[body_name]
        g_child = bpy.data.objects[geom_name]
        parent_obj(g_child, g_parent)

# --- EXECUTE ---
if root is not None:
    geoms = get_geom(root, 'geom')
    print(f"Found {len(geoms)} bodies with geometry.")
    # Note: 'textures' and 'meshes' variables were not defined in your snippet
    # so I commented this out to prevent a crash:
    # mesh_spec = Mesh_info(textures, meshes, geoms)
