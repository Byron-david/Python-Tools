# Mujoco XML Importer for Blender

A Python utility script for Blender (`bpy`) designed to parse Mujoco XML simulation files. It reads the XML structure (including nested `<include>` files), extracts body and geometry attributes, and applies them to Blender objects to reconstruct the simulation scene or update object properties.

## Features

* **Recursive Parsing:** Automatically finds and parses files linked via `<include file="...">` tags.
* **Geometry Extraction:** Scrapes `<body>` and `<geom>` attributes from the XML.
* **Blender Integration:**
    * Renames Blender objects to match Mujoco IDs.
    * Resizes objects based on Mujoco primitive specs (handling 3D boxes, 2D cylinders/capsules, and 1D spheres).
    * Automates parenting of Geometry objects to Body objects.

## Dependencies

* **Blender:** Tested on Blender 3.x+
* **Python Libraries:**
    * `lxml` (Required for XML parsing. **Note:** Blender uses its own bundled Python environment. You may need to install `lxml` specifically into Blender's python path via pip).
    * `pathlib` (Standard library)

## Configuration (Important)

**Before running this script, you must update the file paths.**

The script currently contains hardcoded paths to a specific user directory. Open the script and locate the `import_path` variable at the top:

```python
# CHANGE THIS PATH to the folder containing your Mujoco XML files
import_path = Path('C:\\Path\\To\\Your\\XML\\Folder\\') 

# Ensure the 'path' variable passed to parse_xml is defined
# Example: root = parse_xml("model.xml")
