# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "Compositor Disc Cache",
    "description": "Creates Disc Cache Through VSE for Compositor ",
    "author": "Fahad Hasan Pathik CGVIRUS",
    "version": (4, 0),
    "blender": (2, 40, 0),
    "category": "Sequencer",
    "wiki_url": "https://github.com/cgvirus/Blender-Compositor-Disc-Cache-Realtime-Preview-Addon"
    }

import bpy
from . import Blender_Compositor_Cache_Preview_Addon


modules = Blender_Compositor_Cache_Preview_Addon


def register():
    from bpy.utils import register_class
    modules.register()


def unregister():
    from bpy.utils import unregister_class
    modules.unregister()


if __name__ == "__main__":
    register()