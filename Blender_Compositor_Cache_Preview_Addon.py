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
    "version": (1, 0),
    "blender": (2, 79, 0),
    "category": "Sequencer",
    "warning":     ""
    }

import bpy, os
from bpy.types import Header, Menu, Panel



def cache_it(context):
    
    scn = bpy.context.scene
    scname = scn.name
    seqobj = scn.sequence_editor.sequences_all
    img_formt = str(scn.render.image_settings.file_format)

    if img_formt == "JPEG":
        img_formt = "jpg"
    elif img_formt == "PNG":
    	img_formt = "png"
    elif img_formt == "TARGA":
    	img_formt = "tga"
    else:
    	img_formt = "png"

    filepath = scn.render.filepath
    cachename = bpy.path.basename(filepath)
    default_place_holder = cachename + "0000"+"." + img_formt
    
    end_frame = bpy.data.scenes[scname].frame_preview_end or \
                bpy.data.scenes[scname].frame_end
    start_frame = bpy.data.scenes[scname].frame_preview_start or \
                bpy.data.scenes[scname].frame_start

    def cachecreate():      

        #opengl render start
        bpy.ops.render.opengl(animation=True, sequencer=True)
        
        #Listing and sorting rendered files directory to create imagestrip
        dirc= os.path.dirname(filepath)
        lst = sorted(os.listdir(dirc))
        
        #Without 0000.jpg/extension placeholder will not create
        #later this place holder name becomes image strip name automatically
        #We will pull this image name for many functions (deletion and condition)
        
        file=[{'name': default_place_holder}, ]
        for i in lst:
            frame={"name":i}
            file.append(frame)
        
        #creating Image Strip From listed directory
        bpy.ops.sequencer.image_strip_add( \
        directory = dirc, \
        files = file, \
        relative_path=True, \
        frame_start=0, \
        channel=15, \
        replace_sel=True, \
        use_placeholders=True, \
        )
        
        # NOTE:default_place_holder is
        #the name of the created image strip
        
        #slicing extended strip to the preview region
        seqobj[default_place_holder].frame_final_start = start_frame
        seqobj[default_place_holder].frame_final_end = end_frame



    oldcachelist = [strips for strips in seqobj \
                if strips.name.startswith(cachename)]


    #If there is a old cache>Delete else start cacahing

    if oldcachelist != [] :
        oldcache = bpy.data.scenes[scname].sequence_editor.sequences_all[default_place_holder]
        oldcache.select = True
        bpy.ops.sequencer.delete()
        cachecreate()
        
    else:
        cachecreate()
    
    
def clearcache(context):
    
    scn = bpy.context.scene
    scname = scn.name
    seqobj = scn.sequence_editor.sequences_all
    img_formt = str(scn.render.image_settings.file_format)

    if img_formt == "JPEG":
        img_formt = "jpg"
    elif img_formt == "PNG":
    	img_formt = "png"
    elif img_formt == "TARGA":
    	img_formt = "tga"
    else:
    	img_formt = "png"

    filepath = scn.render.filepath
    cachename = bpy.path.basename(filepath)
    default_place_holder = cachename + "0000"+"." + img_formt

    #Simply delete exisiting cache 
    oldcache = bpy.data.scenes[scname].sequence_editor.sequences_all[default_place_holder]
    oldcache.select = True
    bpy.ops.sequencer.delete()



    
class CompositorDiscCache(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sequencer.composit_disc_cache"
    bl_label = "Compositor Disc Cache"


    def execute(self, context):
        try:
            cache_it(context)
            return {'FINISHED'}
        except:
            self.report({'ERROR'}, 'Please add the Scene Strip \
            \nIf done already then \
            \nSpecify temporary directory in Render Panel>Output')
            return {'CANCELLED'}
    
class CompositorClearCache(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "sequencer.composit_clear_cache"
    bl_label = "Compositor Clear Cache"


    def execute(self, context):
        try:
            clearcache(context)
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Cache File to Clear')
            return {'CANCELLED'}

#UI
class VseDiscCachePanel(Header):
    
    bl_space_type = "SEQUENCE_EDITOR"
    bl_idname = "SEQUENCER_OT_vsedisccache"
    
    def draw(self, context):
        layout = self.layout
        st = context.space_data
        scene = context.scene

        row = layout.row(align=True)
        
        st.view_type == 'SEQUENCER'
        row = layout.row(align=True)
        row.operator("sequencer.composit_disc_cache", text="Cache Preview")
        row.operator("sequencer.composit_clear_cache", text="Clear Cache")
    
      

def register():
    
    bpy.utils.register_class(CompositorDiscCache)
    bpy.utils.register_class(CompositorClearCache)
    bpy.utils.register_class(VseDiscCachePanel)

def unregister():

    bpy.utils.unregister_class(CompositorDiscCache)
    bpy.utils.unregister_class(CompositorClearCache)
    bpy.utils.unregister_class(VseDiscCachePanel)
    
    
if __name__ == "__main__":
    register()
