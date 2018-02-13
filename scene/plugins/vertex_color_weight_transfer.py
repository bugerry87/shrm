import bpy
from mathutils import Color
import random
from bpy.props import *
import bmesh


############ INFO ###############
bl_info = {
    "name": "Weight Vertex Color ",
    "author": "Kursad Karatas, Gerald Baulig",
    "version": (0, 1, 0),
    "blender": (2, 6 ,6),
    "location": "View3D > Vertex Paint > Paint > Weight to Vertex Colors",
    "description": "Copies Weights to Vertex Colors and reverse",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"}


############ NEW FUNCS ###############
def copyWeight2VertexCol(context, method):
    ao = context.active_object
    try:
        #Check to see if we have at least one vertex group
        assert ao.vertex_groups
    except:
        return {'WARNING'}, 'No Vertex Groups to copy'
    
    col = Color()
    col.h = 0
    col.s = 0
    col.v = 0

    for vkey in ao.vertex_groups.keys():
        vgrp = ao.vertex_groups.get(vkey)
        vcol = ao.data.vertex_colors.get(vkey)
        if not vcol:
            vcol = ao.data.vertex_colors.new(vkey)
        
        for poly in ao.data.polygons:
            for loop in poly.loop_indices:
                vert_index = ao.data.loops[loop].vertex_index
                weight = 0   
                                       
                #Check to see if the vertex has any group association
                try:
                    weight = vgrp.weight(vert_index)
                except:
                    vcol.data[loop].color = (0, 0, 0)
                    continue
    
                #Colored
                if method:
                    col.h = weight / 1.5
                    col.s = 1
                    col.v = 1
                #Gray 
                else:
                    col.v = weight
                    
                vcol.data[loop].color = (col.b, col.g, col.r)
                
    return {'INFO'}, 'Copied %d Vertex Groups to Vertex Colors' % len(ao.vertex_groups.keys())


def copyVertexCol2Weight(context):
    ao = context.active_object
    try:
        #Check to see if we have at least one vertex color
        assert ao.data.vertex_colors
    except:
        return {'WARNING'}, 'No Vertex Colors to copy'

    for vkey in ao.data.vertex_colors.keys():
        vcol = ao.data.vertex_colors.get(vkey)
        vgrp = ao.vertex_groups.get(vkey)
        if not vgrp:
            vgrp = ao.vertex_groups.new(vkey)
        
        for poly in ao.data.polygons:
            for loop in poly.loop_indices:
                color = Color(vcol.data[loop].color)
                vert_index = ao.data.loops[loop].vertex_index
                
                #Ignore if pur black 
                if color.v == 0:
                    continue
                
                #Check if grayscale mode
                if color.s == 0:
                    vgrp.add([vert_index], color.v, 'REPLACE')
                else:
                    vgrp.add([vert_index], color.h * 1.5, 'REPLACE')
                    
    return {'INFO'}, 'Copied %d Vertex Colors to Vertex Groups' % len(ao.vertex_groups.keys())


def bakeVertexCol2Texture(context):
    ao = context.active_object

    try:
        assert ao.data.vertex_colors
    except:
        return {'WARNING'}, 'No Vertex Colors to copy'
    
    try:
        assert ao.data.uv_textures[0]
    except:
        return {'ERROR'}, 'UVMap required'
    
    uvmap = ao.data.uv_textures[0]
    scene = bpy.data.scenes[0]

    for vkey in ao.data.vertex_colors.keys():
        vcol = ao.data.vertex_colors.get(vkey)
        vcol.active_render = True
        tex_name = vkey + "_weights"
        
        try:
            assert bpy.data.images[tex_name]
            print("Image(", tex_name, ")", " already exist")
        except:
            bpy.ops.image.new(name=tex_name)
            print("New Image(", tex_name, ")")

        img = bpy.data.images[tex_name]
        
        for face in uvmap.data:
            face.image = img
        
        scene.render.bake_type = 'VERTEX_COLORS'
        scene.render.use_bake_to_vertex_color = False
        scene.render.use_bake_clear = False
        bpy.ops.object.bake_image()
    
    return {'INFO'}, "Done"
    

################# OPERATORS ################
class Weight2VertexCol(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.weight2vertexcol"
    bl_label = "Weight to Vertex Colors"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    method = bpy.props.BoolProperty(
        name="Color", 
        description="Choose the coloring method", 
        default=False)
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        type, msg = copyWeight2VertexCol(context, self.method)
        self.report(type, msg)
        context.active_object.data.update()
        return {'FINISHED'}
    

class VertexCol2Weight(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.vertexcol2weight"
    bl_label = "Vertex Colors to Weight"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        type, msg = copyVertexCol2Weight(context)
        self.report(type, msg)
        context.active_object.data.update()
        return {'FINISHED'}


class VertexCol2Texture(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.vertexcol2texture"
    bl_label = "Vertex Colors to Texture"
    bl_space_type = "VIEW_3D"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        type, msg = bakeVertexCol2Texture(context)
        self.report(type, msg)
        context.active_object.data.update()
        return {'FINISHED'}


############ Register ############
def draw_operators(self, context):
    self.layout.operator("object.vertexcol2weight")
    self.layout.operator("object.weight2vertexcol")
    self.layout.operator("object.vertexcol2texture")


def register():
    bpy.utils.register_class(Weight2VertexCol)
    bpy.utils.register_class(VertexCol2Weight)
    bpy.utils.register_class(VertexCol2Texture)
    bpy.types.VIEW3D_MT_paint_vertex.append(draw_operators)
    bpy.types.VIEW3D_MT_paint_weight.append(draw_operators)


def unregister():
    try:
        bpy.types.VIEW3D_MT_paint_vertex.remove(draw_operators)
        bpy.types.VIEW3D_MT_paint_weight.remove(draw_operators) 
        bpy.utils.unregister_class(Weight2VertexCol)
        bpy.utils.unregister_class(VertexCol2Weight)
        bpy.utils.unregister_class(VertexCol2Texture)
    except:
        return

############## MAIN #############
if __name__ == "Weight2VertexCol":
    unregister()
    register()