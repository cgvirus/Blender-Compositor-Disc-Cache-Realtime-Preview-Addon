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


import bpy, addon_utils, os, shutil
from os.path import basename, dirname
from sys import platform
from pathlib import Path
from bpy.props import StringProperty
from bpy.types import (
    Operator, 
    AddonPreferences,
    Header,
    Menu,
    Panel
)


class CompositorDiscCachePrefs(bpy.types.AddonPreferences):
    bl_idname = __package__

    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "Compositor Disc Cache":
            filepath = mod.__file__

    if platform == "win32":
        templatepath= str(Path(filepath).parent) + str(Path('/Template/Comp_VSE_Template.blend'))
    else:
        templatepath= str(Path(filepath).parent) + str(Path('/Template/Comp_VSE_Template.blend'))
    
    
    templatefilepath: bpy.props.StringProperty(
        name="Blender Template",
        subtype='FILE_PATH',
        default = str(templatepath)
    )

    templatename: bpy.props.StringProperty(
    name="Blender Template",
    # subtype='FILE_PATH',
    default = "Comp_VSE"
    )


    def draw(self, context):
        layout = self.layout
        layout.label(text="""Blender file path to import the template from""")
        layout.prop(self, "templatefilepath")
        layout.label(text="""The template to import""")
        layout.prop(self, "templatename")



def import_template(context):

    templatefilepath = Path(context.preferences.addons[__package__].preferences.templatefilepath)
    templatename = context.preferences.addons[__package__].preferences.templatename


    try:
        bpy.data.workspaces[templatename]
        bpy.context.window.workspace = bpy.data.workspaces[templatename]
    except:
        bpy.ops.wm.append(
        filepath="Comp_VSE_Template.blend",
        directory= str(str(templatefilepath)+ str(Path("/WorkSpace/"))),
        filename = templatename)
        bpy.context.window.workspace = bpy.data.workspaces[templatename]

    try:
        bpy.data.scenes["Comp.001"]
        bpy.context.window.scene = bpy.data.scenes["Comp.001"]
    except:
        bpy.ops.wm.append(
        filepath="Comp_VSE_Template.blend",
        directory= str(str(templatefilepath)+ str(Path("/Scene/"))),
        filename="Comp.001")
        bpy.context.window.scene = bpy.data.scenes["Comp.001"]




def render_it(context):

    # Auto set cache render path with scenename
    projpath = bpy.data.filepath
    projname = bpy.path.basename(projpath)
    directory = os.path.dirname(projpath)
    scn = bpy.context.scene
    scname = scn.name
    renderpath = Path("%s/%s_compcache_temp/%s_cache/%s_cache" % (directory , projname, scname, scname))
    bpy.context.scene.render.filepath = str(renderpath)

    olddisptype = bpy.context.preferences.view.render_display_type

    if  bpy.context.preferences.view.render_display_type != 'NONE':
        bpy.context.preferences.view.render_display_type = 'NONE'

    if bpy.data.scenes[scname].frame_preview_start <= 0:
        bpy.data.scenes[scname].frame_preview_start = 1
        bpy.data.scenes[scname].frame_current = 1
    

    frame_preview_start = bpy.data.scenes[scname].frame_preview_start
    frame_preview_end = bpy.data.scenes[scname].frame_preview_end
    frame_org_start = bpy.data.scenes[scname].frame_start
    frame_org_end = bpy.data.scenes[scname].frame_end
    

    bpy.data.scenes[scname].frame_start = frame_preview_start
    bpy.data.scenes[scname].frame_end = frame_preview_end

    
    #Refresh Render View
#    bpy.data.scenes[scname].frame_current = bpy.data.scenes[scname].frame_start
    bpy.ops.screen.frame_jump(end=False)
    bpy.data.scenes[scname].render.use_sequencer = False


    bpy.ops.render.render('INVOKE_DEFAULT', animation=True, use_viewport=True)
    
    def go_back():
        bpy.data.scenes[scname].frame_start = frame_org_start
        bpy.data.scenes[scname].frame_end = frame_org_end
        bpy.context.preferences.view.render_display_type = olddisptype
        
    bpy.app.timers.register(go_back, first_interval=0.5)
    



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
    elif img_formt == "TARGA_RAW":
        img_formt = "tga"
    elif img_formt == "BMP":
        img_formt = "bmp"
    elif img_formt == "IRIS":
        img_formt = "rgb"
    elif img_formt == "JPEG2000":
        img_formt = "jp2"
    elif img_formt == "CINEON":
        img_formt = "cin"
    elif img_formt == "DPX":
        img_formt = "dpx"
    elif img_formt == "OPEN_EXR":
        img_formt = "exr"
    elif img_formt == "OPEN_EXR_MULTILAYER":
        img_formt = "exr"
    elif img_formt == "HDR":
        img_formt = "hdr"
    elif img_formt == "TIFF":
        img_formt = "tif"
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

        #2.93 has weird glicth
        if bpy.app.version[:2] == (2, 93):
            bpy.ops.sequencer.image_strip_add( \
            directory = filepath, \
            files = file, \
            relative_path=True, \
            frame_start=0, \
            channel=15, \
            replace_sel=True, \
            use_placeholders=True, \
            )
        else:
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
    elif img_formt == "TARGA_RAW":
        img_formt = "tga"
    elif img_formt == "BMP":
        img_formt = "bmp"
    elif img_formt == "IRIS":
        img_formt = "rgb"
    elif img_formt == "JPEG2000":
        img_formt = "jp2"
    elif img_formt == "CINEON":
        img_formt = "cin"
    elif img_formt == "DPX":
        img_formt = "dpx"
    elif img_formt == "OPEN_EXR":
        img_formt = "exr"
    elif img_formt == "OPEN_EXR_MULTILAYER":
        img_formt = "exr"
    elif img_formt == "HDR":
        img_formt = "hdr"
    elif img_formt == "TIFF":
        img_formt = "tif"
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




class ImportCompVseTemplate(bpy.types.Operator):
    """Import vse comp template"""
    bl_idname = "import.import_vse_comp_template"
    bl_label = "import vse comp template"


    def execute(self, context):

        try:
            import_template(context)
            return {'FINISHED'}
        except:
            self.report({'ERROR'},'No template found!')
            return {'CANCELLED'}


class CompositorRenderCache(bpy.types.Operator):
    """Render the cache"""
    bl_idname = "sequencer.composit_render_cache"
    bl_label = "Render Cache"


    def execute(self, context):
        if bpy.data.is_saved:
            
            render_it(context)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}





class CompositorDiscCache(bpy.types.Operator):
    """Starts the Cache preview"""
    bl_idname = "sequencer.composit_disc_cache"
    bl_label = "Preview Cache"


    def execute(self, context):
        try:
            cache_it(context)
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No cache to preview')
            return {'CANCELLED'}



class CompositorClearCache(bpy.types.Operator):
    """Clear cache strip from VSE"""
    bl_idname = "sequencer.composit_clear_cache"
    bl_label = "Clear Cache"


    def execute(self, context):
        try:
            clearcache(context)
            self.report({'INFO'}, 'Cache Cleared')
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
            self.report({'INFO'}, 'Cache Deleted')
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Cache Directory to Delete')
            return {'CANCELLED'}


class RenderCompVse(bpy.types.Operator):
    """Delete the cache Directory"""
    bl_idname = "sequencer.compositor_render_animation"
    bl_label = "Compositor Vse Render Animation"


    def execute(self, context):
        try:
            bpy.ops.screen.frame_jump(end=False)
            bpy.context.scene.render.resolution_percentage = 100
            bpy.context.scene.render.use_sequencer = False
            bpy.ops.render.render('INVOKE_DEFAULT', animation=True, use_viewport=True)
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'Render Interupted')
            return {'CANCELLED'}



# UI


class vsedisccache(Menu):
    bl_label = "Disc Cahce"
    bl_idname = "SEQUENCER_MT_vsedisccache"


    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        st = context.space_data
    
        layout.operator("sequencer.composit_render_cache", text="Render Cache", icon='RENDER_ANIMATION')
        layout.operator("sequencer.composit_disc_cache", text="Preview Cache", icon='PLAY')
        layout.operator("sequencer.composit_clear_cache", text="Clear Cache", icon='CANCEL')
        layout.operator("sequencer.compositor_delete_cache", text="Delete Cache", icon='TRASH')



def draw_file_export(self,context):
    layout = self.layout
    layout.operator("import.import_vse_comp_template", text="Import Compositor VSE pipline template")   


def draw_in_header(self, context):
    layout = self.layout
    st = context.space_data
    if st.view_type == 'SEQUENCER':
        row = layout.row(align=True)

        # layout.separator_spacer()

        row.operator("sequencer.composit_render_cache", text="", icon='RENDER_ANIMATION')
        row.operator("sequencer.composit_disc_cache", text="", icon='PLAY')
        row.operator("sequencer.composit_clear_cache", text="", icon='CANCEL')
        row.operator("sequencer.compositor_delete_cache", text="", icon='TRASH')


def draw_item(self, context):
    layout = self.layout
    layout.menu(vsedisccache.bl_idname)

def draw_render_anim(self,context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT'
    layout.operator("sequencer.compositor_render_animation", text="Render Compositor VSE pipline", icon='RENDER_ANIMATION')  





classes = (
    CompositorDiscCachePrefs,
    ImportCompVseTemplate,
    CompositorRenderCache,
    CompositorDiscCache,
    CompositorClearCache,
    CompositorDeleteCache,
    RenderCompVse,
    vsedisccache
)   




def register():

    from bpy.utils import register_class
    
    for c in classes:
        bpy.utils.register_class(c)

    # lets add ourselves to the editor menu
    bpy.types.TOPBAR_MT_file_import.append(draw_file_export)
    bpy.types.SEQUENCER_MT_view.append(draw_item)
    bpy.types.SEQUENCER_HT_header.append(draw_in_header)
    bpy.types.TOPBAR_MT_render.append(draw_render_anim)





def unregister():
    
    from bpy.utils import unregister_class
    
    # remove operator and preferences
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

    # lets remove ourselves from the editor menu
    bpy.types.TOPBAR_MT_file_import.remove(draw_file_export)
    bpy.types.SEQUENCER_MT_view.remove(draw_item)
    bpy.types.SEQUENCER_HT_header.remove(draw_in_header)
    bpy.types.TOPBAR_MT_render.remove(draw_render_anim)



if __name__ == "__main__":
    register()
