import os
import math
import random
import bpy
from yattag import Doc, intend

HEAD_CAM = bpy.data.objects['HeadCam']
RIGHT_CAM = bpy.data.objects['RightCam']

REF = bpy.data.objects['Reference']
SEG = bpy.data.objects['Segmented']

SKIN = bpy.data.materials['skin']
REF_DISP = REF.modifiers['Displace']
SEG_DISP = SEG.modifiers['Displace']

HAND = bpy.data.objects['c_hand_r']

PALM = bpy.data.objects['Armature'].pose.bones['palm_r']

THUMB_1 = bpy.data.objects['Armature'].pose.bones['thumb_01_r']
THUMB_2 = bpy.data.objects['Armature'].pose.bones['thumb_02_r']
THUMB_3 = bpy.data.objects['Armature'].pose.bones['thumb_03_r']

INDEX_1 = bpy.data.objects['Armature'].pose.bones['index_01_r']
INDEX_2 = bpy.data.objects['Armature'].pose.bones['index_02_r']
INDEX_3 = bpy.data.objects['Armature'].pose.bones['index_03_r']

MIDDLE_1 = bpy.data.objects['Armature'].pose.bones['middle_01_r']
MIDDLE_2 = bpy.data.objects['Armature'].pose.bones['middle_02_r']
MIDDLE_3 = bpy.data.objects['Armature'].pose.bones['middle_03_r']

RING_1 = bpy.data.objects['Armature'].pose.bones['ring_01_r']
RING_2 = bpy.data.objects['Armature'].pose.bones['ring_02_r']
RING_3 = bpy.data.objects['Armature'].pose.bones['ring_03_r']

PINKY_1 = bpy.data.objects['Armature'].pose.bones['pinky_01_r']
PINKY_2 = bpy.data.objects['Armature'].pose.bones['pinky_02_r']
PINKY_3 = bpy.data.objects['Armature'].pose.bones['pinky_03_r']

def rand_skin_color():
    new_diffuse = random.random()
    SKIN.diffuse_intensity = new_diffuse
    

def rand_displacement():
    new_mid_level = random.random()
    REF_DISP.mid_level = new_mid_level
    SEG_DISP.mid_level = new_mid_level
    

def rand_bone_loc(bone):
    limits = bone.constraints['Limit Distance']
    bone.location.x = limits.target.location.x + random.uniform(-1, 1) * limits.distance
    bone.location.y = limits.target.location.y + random.uniform(-1, 1) * limits.distance
    bone.location.z = limits.target.location.z + random.uniform(-1, 1) * limits.distance
    

def rand_bone_euler(bone):
    limits = bone.constraints['Limit Rotation']
    bone.rotation_euler.x = random.uniform(limits.min_x, limits.max_x)
    bone.rotation_euler.y = random.uniform(limits.min_y, limits.max_y)
    bone.rotation_euler.z = random.uniform(limits.min_z, limits.max_z)


def rand_hand_pose():
    #HAND
    rand_bone_loc(HAND)
    #THUMB
    rand_bone_euler(THUMB_1)
    rand_bone_euler(THUMB_2)
    rand_bone_euler(THUMB_3)
    #INDEX
    rand_bone_euler(INDEX_1)
    rand_bone_euler(INDEX_2)
    #MIDDLE
    rand_bone_euler(MIDDLE_1)
    rand_bone_euler(MIDDLE_2)
    #RING
    rand_bone_euler(RING_1)
    rand_bone_euler(RING_2)
    #PINKY
    rand_bone_euler(PINKY_1)
    rand_bone_euler(PINKY_2)
    #UPDATE
    bpy.context.scene.update()


def rand_all():
    #SKIN
    rand_skin_color()
    rand_displacement()
    #POSE
    rand_hand_pose()
    
    
def prep_ref(scene):
    REF.hide_render = False
    SEG.hide_render = True
    scene.render.use_antialiasing = True
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.color_mode = 'RGB'


def prep_seg(scene):
    REF.hide_render = True
    SEG.hide_render = False
    scene.render.use_antialiasing = False
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'BW'


def to_local_pos(pos, trans_mat):
    return (pos - trans_mat.to_translation()) * trans_mat
    

def bones_to_join_xml(tag, cam, root_bone):
    ##############################
    def bone_to_join_tag(bone):
        with tag('join', name=bone.name):
            pos = to_local_pos(bone.head, cam.matrix_world)
            with tag('head', x=pos.x, y=pos.y, z=pos.z):
                pass
            pos = to_local_pos(bone.tail, cam.matrix_world)
            with tag('tail', x=pos.x, y=pos.y, z=pos.z):
                pass
            for child in bone.children:
                bone_to_join_tag(child)
    ##############################
    bone_to_join_tag(root_bone)
    

if __name__ == "__main__":
    scene = bpy.context.scene
    prefix = scene.render.filepath
    
    for frame in range(scene.frame_start, scene.frame_end):
        scene.frame_current = frame
        rand_all()
        scene.update()
        
        #REFERENCE IMAGE
        prep_ref(scene)
        scene.camera = HEAD_CAM
        scene.render.filepath = prefix + "{:>04}_head_ref".format(frame) 
        bpy.ops.render.render(write_still=True)
        
        scene.camera = RIGHT_CAM
        scene.render.filepath = prefix + "{:>04}_right_ref".format(frame) 
        bpy.ops.render.render(write_still=True)
        
        #SEGMENTATION IMAGE
        prep_seg(scene)
        scene.camera = HEAD_CAM
        scene.render.filepath = prefix + "{:>04}_head_seg".format(frame)
        bpy.ops.render.render(write_still=True)
        
        scene.camera = RIGHT_CAM
        scene.render.filepath = prefix + "{:>04}_right_seg".format(frame)
        bpy.ops.render.render(write_still=True)
        
        #DEPTH IMAGE
        scene.use_nodes = True
        
        scene.camera = HEAD_CAM
        scene.render.filepath = prefix + "{:>04}_head_dep".format(frame)
        bpy.ops.render.render(write_still=True)
        
        scene.camera = RIGHT_CAM
        scene.render.filepath = prefix + "{:>04}_right_dep".format(frame)
        bpy.ops.render.render(write_still=True)
        
        scene.use_nodes = False
        
        #XML
        doc, tag, ~ = Doc().tagtext()
        
        with tag('view', name='head':)
            bones_to_join_xml(tag, HEAD_CAM, PALM)
        
        xml_string = indent(
            DOC.getvalue(),
            indentation = ' '*2,
            newline = '\r\n'
        )
        
        #RESET
        scene.render.filepath = prefix