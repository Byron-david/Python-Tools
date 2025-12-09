# Mujoco XML Importer for Blender

A Python utility script for Blender (`bpy`) designed to parse Mujoco XML simulation files. It reads the XML structure (including nested `<include>` files), extracts body and geometry attributes, and applies them to Blender objects to reconstruct the simulation scene.

## Key Features

* **Dynamic Pathing:** Automatically detects the XML file location based on where your current Blender project is saved (Works on Windows, Mac, and Linux).
* **Recursive Parsing:** Recursively finds and parses files linked via `<include file="...">` tags.
* **Geometry Extraction:** Scrapes `<body>` and `<geom>` attributes from the XML.
* **Blender Integration:**
    * Renames Blender objects to match Mujoco IDs.
    * Resizes objects based on Mujoco primitive specs (Box, Cylinder, Sphere).
    * Automates parenting of Geometry objects to Body objects.

## Dependencies

* **Blender:** Tested on Blender 3.x+
* **Python Libraries:**
    * `lxml` (Required for XML parsing).
    * `pathlib` (Standard library, used for cross-platform path handling).

> **Note:** Blender uses its own bundled Python environment. If `import lxml` fails, you may need to install it specifically into Blender's python path via pip.

## Setup & Usage

### 1. File Organization (Crucial)
The script uses **relative paths**. For it to work, you must structure your files like this:

```text
MyProjectFolder/
├── robot_arm.blend      <-- Save your Blender file here
├── robot_arm.xml        <-- Your main XML file (Must match .blend name)
├── assets/              <-- Any included folders
│   └── dependencies.xml
