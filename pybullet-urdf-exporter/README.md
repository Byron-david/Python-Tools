# URDF Exporter for Blender

A Blender Addon designed to export 3D models and kinematic chains directly to the **Unified Robot Description Format (URDF)**. This tool simplifies the process of creating robots for ROS (Robot Operating System), Gazebo, and other physics simulators by allowing you to rig and define properties directly within the Blender interface.

## Features

* **Kinematic Chain Export:** Uses Blender's parent-child hierarchy to automatically generate the URDF tree structure.
* **Joint Configuration:** Supports standard URDF joint types (**Fixed**, **Revolute**, **Prismatic**) with configurable axes and limits.
* **Geometry & Collision:** Define separate visual geometry and collision meshes for physics engines.
* **Automatic Mesh Export:** Automatically exports associated meshes as `.obj` files alongside the URDF.
* **Limit Handling:** Set lower and upper limits for joint motion directly in the UI.

## Requirements

* **Blender:** Version 3.5.0 or higher.
* **Python Dependencies:** `lxml` (for XML generation).

## Installation

1.  Download the `urdf_exporter.py` file.
2.  Open Blender.
3.  Go to **Edit > Preferences > Add-ons**.
4.  Click **Install...** and select the file.
5.  Enable the addon by checking the box next to **Import-Export: URDF Exporter**.

## Usage

### 1. Interface Location
The tools are located in the 3D View Sidebar (N-Panel).
* Press `N` in the 3D viewport.
* Click the **URDF** (or *Mujcoo*) tab.



### 2. Defining Links (Bodies)
In URDF, a "Link" is a rigid body.
1.  Select an object in Blender (e.g., the base of your robot).
2.  In the panel, set the **Type** to **Link**.
3.  This object effectively becomes a `<link>` in the URDF file.

### 3. Defining Joints
Joints are defined on the **Child** object relative to its parent.
1.  Parent the child object to the parent object (Ctrl+P).
2.  Select the child object.
3.  In the panel, check **URDF Joint**.
4.  Configure the joint properties:
    * **Type:** Fixed, Revolute (Hinge), or Prismatic (Slider).
    * **Axis:** X, Y, or Z.
    * **Limits:** Set the **Lower Limit** and **Upper Limit** (in radians or meters).



### 4. Visuals vs. Collisions
You can attach separate geometry to your Links.
1.  Create a mesh (e.g., a simple cube for collision).
2.  Parent it to the main "Link" object.
3.  In the panel, set its **Type** to **Collision**.
4.  Set the **Primitive** type (Box, Cylinder, Sphere, or Mesh).

### 5. Exporting
1.  Go to the **Export** section at the bottom of the panel.
2.  Select the output directory.
3.  (Optional) Check **Export OBJ Files** to generate mesh assets.
4.  Click **Export XML/URDF**.

## Property Reference

| Property | Description |
| :--- | :--- |
| **Link** | Defines the object as a physical body in the chain. |
| **Collision** | Defines the object as a collision shape (invisible physics boundary). |
| **Joint Type** | `Revolute` (rotates), `Prismatic` (slides), `Fixed` (no movement). |
| **Joint Axis** | The local axis (X, Y, Z) around which the joint moves. |
| **Limits** | Hard stops for the joint movement (Lower/Upper). |

## Development

**Author:** @byrondavid
**Blender API:** 3.5.0

### Known Issues
* Ensure that rotation transforms are applied (Ctrl+A -> Rotation) before exporting to ensure axes align correctly in the simulation.
* The exporter currently uses the Z-axis as "Up" by default.
