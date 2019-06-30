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
    "blender": (2, 80, 0),
    "category": "Sequencer",
    "wiki_url": "https://github.com/cgvirus/Blender-Compositor-Disc-Cache-Realtime-Preview-Addon"
    }




import bpy, os, shutil
from pathlib import Path
from bpy.types import (
    Header,
    Menu,
    Panel,
)


def render_it(context):

    # Auto set cache render path with scenename
    projpath = bpy.data.filepath
    directory = os.path.dirname(projpath)
    scn = bpy.context.scene
    scname = scn.name
    renderpath = Path("%s/compcache_temp/%s_cache/%s_cache" % (directory , scname, scname))
    bpy.context.scene.render.filepath = str(renderpath)

    #Refresh Render View
    bpy.ops.screen.frame_jump(end=False)
    #opengl render start
    bpy.ops.render.opengl('INVOKE_DEFAULT', animation=True, sequencer=True)



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

        #assigning blendmode to REPLACE
        bpy.data.scenes[scname].sequence_editor.sequences_all[default_place_holder].blend_type = 'REPLACE'
        
        # NOTE:default_place_holder is
        #the name of the created image strip
        
        #slicing extended strip to the preview region
        
        seqobj[default_place_holder].frame_final_start = start_frame
        # seqobj[default_place_holder].frame_final_end = end_frame

        bpy.ops.screen.animation_play()


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




def dleteCache(context):
    
    scn = bpy.context.scene
    filepath = scn.render.filepath
    #Delete directory
    directroy = str(Path(filepath).parents[0])
    shutil.rmtree(directroy)


class CompositorRenderCache(bpy.types.Operator):
    """Render the cache"""
    bl_idname = "sequencer.composit_render_cache"
    bl_label = "Render Cache"


    def execute(self, context):

        render_it(context)
        return {'FINISHED'}
        # try:
        #     render_it(context)
        #     return {'FINISHED'}
        # except:
        #     self.report({'ERROR'}, 'Please add the Scene Strip \
        #     \nIf done already then \
        #     \nSpecify temporary directory in Render Panel>Output')
        #     return {'CANCELLED'}



class CompositorDiscCache(bpy.types.Operator):
    """Starts the Cache preview"""
    bl_idname = "sequencer.composit_disc_cache"
    bl_label = "Preview Cache"


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
    """Clear cache strip from VSE"""
    bl_idname = "sequencer.composit_clear_cache"
    bl_label = "Clear Cache"


    def execute(self, context):
        try:
            clearcache(context)
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Cache to Clear')
            return {'CANCELLED'}




class CompositorDeleteCache(bpy.types.Operator):
    """Delete the cache Directory"""
    bl_idname = "sequencer.compositor_delete_cache"
    bl_label = "Delete Cache"


    def execute(self, context):
        try:
            dleteCache(context)
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Cache Directory to Delete')
            return {'CANCELLED'}




#UI

class vsedisccache(Menu):
    bl_label = "Disc Cahce"
    bl_idname = "SEQUENCER_MT_vsedisccache"
    # bl_space_type = "SEQUENCE_EDITOR"


    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        st = context.space_data
    
        # row = layout.row(align=True)
        # row = layout
        # props = layout.operator("render.opengl", text="Render Cache", icon='RENDER_ANIMATION')
        # props.animation = True
        # props.sequencer = True
        layout.operator("sequencer.composit_render_cache", text="Render Cache", icon='RENDER_ANIMATION')
        layout.operator("sequencer.composit_disc_cache", text="Preview Cache", icon='PLAY')
        layout.operator("sequencer.composit_clear_cache", text="Clear Cache", icon='CANCEL')
        layout.operator("sequencer.compositor_delete_cache", text="Delete Cache", icon='TRASH')





class vsedisccachebtn(Header):
    # bl_label = "Disc Cahce"
    bl_idname = "SEQUENCER_HT_vsedisccache"
    bl_space_type = "SEQUENCE_EDITOR"


    
    def draw(self, context):
        layout = self.layout
        st = context.space_data
        if st.view_type == 'SEQUENCER':
            row = layout.row(align=True)

            # props = row.operator("render.opengl", text="", icon='RENDER_ANIMATION')
            # props.animation = True
            # props.sequencer = True
            row.operator("sequencer.composit_render_cache", text="", icon='RENDER_ANIMATION')
            row.operator("sequencer.composit_disc_cache", text="", icon='PLAY')
            row.operator("sequencer.composit_clear_cache", text="", icon='CANCEL')
            row.operator("sequencer.compositor_delete_cache", text="", icon='TRASH')




def draw_item(self, context):
    layout = self.layout
    layout.menu(vsedisccache.bl_idname)





classes = (
    CompositorRenderCache,
    CompositorDiscCache,
    CompositorClearCache,
    CompositorDeleteCache,
    vsedisccache,
    vsedisccachebtn,
)   




def register():

    from bpy.utils import register_class
    
    for c in classes:
        bpy.utils.register_class(c)

    # lets add ourselves to the editor maenu
    bpy.types.SEQUENCER_MT_view.append(draw_item)





def unregister():
    
    from bpy.utils import unregister_class
    
    # remove operator and preferences
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    # lets add ourselves to the editor maenu
    bpy.types.SEQUENCER_MT_view.remove(draw_item)



if __name__ == "__main__":
    register()