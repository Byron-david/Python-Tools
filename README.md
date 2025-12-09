# Blender Robotics Tools

A collection of Python-based Blender addons designed to bridge the gap between Blender's 3D modeling environment and robotics simulators like **Mujoco** and **ROS/Gazebo**.

## 📂 Tools Included

This repository contains three distinct tools. Click the tool name to view its specific documentation and usage guide.

| Tool | Folder | Description |
| :--- | :--- | :--- |
| **[Mujoco Exporter](./mujoco_exporter)** | `/mujoco_exporter` | Export Blender scenes and kinematic chains to **Mujoco XML** (`.xml`). |
| **[Mujoco Importer](./mujoco_importer)** | `/mujoco_importer` | Import **Mujoco XML** files into Blender, reconstructing hierarchy and geometry. |
| **[URDF Exporter](./urdf_exporter)** | `/urdf_exporter` | Export Blender rigged models to **URDF** format for ROS/Gazebo. |

## 🚀 Installation

Each tool functions as a standalone Blender Addon.

1.  Navigate to the folder of the tool you wish to use.
2.  Download the `.py` script (e.g., `mujoco_exporter.py`).
3.  Open **Blender** and go to **Edit > Preferences > Add-ons**.
4.  Click **Install...** and select the `.py` file.
5.  Enable the addon by checking the box in the list.

## 🛠 Prerequisites

* **Blender 3.5+**
* **Python Dependencies:** `lxml` (Standard in most environments, but required for XML parsing).

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

**Author:** @byrondavid
