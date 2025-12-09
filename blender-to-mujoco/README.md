# Mujoco Exporter for Blender

A Blender Addon to export 3D scenes, meshes, and kinematic chains directly to the Mujoco XML (`.xml`) format. This tool bridges the gap between Blender's modeling capabilities and Mujoco's physics simulation environment.

## Features

* **Scene Export:** Converts Blender object hierarchy into Mujoco XML nested bodies.
* **Geometry Support:** Supports native primitives (Box, Sphere, Cylinder, Capsule, Ellipsoid) and arbitrary Meshes (`.obj`).
* **Physics Properties:** Configure Collision bodies versus Visual geometries.
* **Joint Configuration:** Add Hinge, Slide, and Ball joints with axis selection and limits (min/max).
* **Automatic Conversion:** Handles coordinate system conversion (Blender XYZ to Mujoco ZYX).
* **Material Support:** Exports basic material colors and texture references.

## Requirements

* **Blender:** Version 3.5.0 or higher.
* **Python Dependencies:** `lxml` (Standard with most Blender installations).

## Installation

1.  Download the `mujoco_exporter.py` file from this repository.
2.  Open Blender.
3.  Go to **Edit > Preferences > Add-ons**.
4.  Click **Install...** and select the downloaded `.py` file.
5.  Enable the addon by checking the box next to **Development: Mujoco Exporter**.

## Usage

### 1. The Interface
Once installed, the control panel is located in the 3D View Sidebar.
* Press `N` to open the Sidebar.
* Locate the **Mujoco** tab.

### 2. Setting Object Properties
To export an object correctly, you must assign it a **Mujoco Type** in the panel properties.

| Mujoco Type | Description |
| :--- | :--- |
| **None** | Object is ignored during export. |
| **Link** | Acts as a Mujoco `<body>`. Use this for the parent objects in your kinematic chain. |
| **Geometry** | Visual meshes attached to a body (`<geom>`). |
| **Collision** | Invisible geometry used for physics calculations (`<geom>` with collision class). |
| **Light** | Exports as a Mujoco light source. |
| **Site** | Exports as a `<site>` (useful for sensors or attachment points). |

### 3. Rigging the Hierarchy
The exporter relies on Blender's parenting system to build the XML tree.

1.  **Root Body:** Create a "Link" object.
2.  **Joints:** If a "Link" requires a joint, check **Mujoco Joint** in the panel. Select the Type (Hinge/Slide), Axis (X/Y/Z), and Range limits.
3.  **Visuals/Collisions:** Parent your "Geometry" or "Collision" objects to the specific "Link" object.

### 4. Exporting
1.  In the **Mujoco Export** panel (bottom section), select an output directory.
2.  (Optional) Check **Export OBJ Files** if you are using custom meshes. This will generate `.obj` files alongside the XML.
3.  Click **Export XML**.

## Configuration Options

### Primitives
When setting an object to **Geometry** or **Collision**, you must define the **Primitive** type:
* **Mesh:** Uses the actual geometry (exports as `.obj`).
* **Box/Sphere/Capsule/Cylinder/Ellipsoid:** Uses the object's scale to define the primitive size in XML.

### Joints
* **Joint Name:** Optional. If left blank, it defaults to `{Object_Name}_joint`.
* **Ranges:** Defined in degrees for Hinge joints, and units for Slide joints.

## Known Limitations
* Complex node shaders are not fully supported; only Diffuse color and Image Texture nodes are parsed.
* The addon currently looks for a tab labeled "Mujcoo" (Typo in source) or "Mujoco" depending on the version.
