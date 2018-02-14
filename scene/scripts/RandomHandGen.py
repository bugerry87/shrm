import sys
import os
import math
import random
import bpy
from mathutils import Vector, Quaternion

PLUGINS = os.path.dirname(bpy.data.filepath) +"/plugins/"
if not PLUGINS in sys.path:
    print("include %s to system path" % PLUGINS)
    sys.path.append(PLUGINS)
from yattag import Doc, indent

HEAD_CAM = bpy.data.objects['HeadCam']
RIGHT_CAM = bpy.data.objects['RightCam']

REF = bpy.data.objects['Reference']
SEG = bpy.data.objects['Segmented']

SKIN = bpy.data.materials['skin']
REF_DISP = REF.modifiers['Displace']
SEG_DISP = SEG.modifiers['Displace']

TARGET = bpy.data.objects['c_hand_r']
PALM = bpy.data.objects['Armature'].pose.bones['palm_r']


def rand_skin_color():
    new_diffuse = random.random()
    SKIN.diffuse_intensity = new_diffuse
    

def rand_displacement():
    new_mid_level = random.random()
    REF_DISP.mid_level = new_mid_level
    SEG_DISP.mid_level = new_mid_level
    

def rand_location(obj):
    try:
        limits = obj.constraints['Limit Distance']
    except:
        print("%s has no constrains named 'Limit Distance'" % obj)
        return
    
    rot = Quaternion((
        random.uniform(-1, 1),
        random.uniform(-1, 1), 
        random.uniform(-1, 1),
        random.uniform(-1, 1),
        ))
    pos = Vector((1, 0, 0))
    pos.rotate(rot)
    pos = pos * limits.distance
    obj.location = pos


def rand_euler(obj):
    try:
        limits = obj.constraints['Limit Rotation']
    except:
        print("%s has no constrains named 'Limit Rotation'" % obj)
        return
    
    obj.rotation_euler.x = random.uniform(limits.min_x, limits.max_x)
    obj.rotation_euler.y = random.uniform(limits.min_y, limits.max_y)
    obj.rotation_euler.z = random.uniform(limits.min_z, limits.max_z)


def rand_pose(obj):
    rand_location(obj)
    rand_euler(obj)
    for child in obj.children:
        rand_pose(child)


def rand_hand_pose():
    rand_location(TARGET)
    rand_pose(PALM)


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


def render(scene, cam, filename):
    prefix = scene.render.filepath
    scene.camera = cam
    scene.render.filepath = prefix + filename 
    bpy.ops.render.render(write_still=True)
    scene.render.filepath = prefix


if __name__ == "__main__":
    scene = bpy.context.scene
    
    for frame in range(scene.frame_start, scene.frame_end):
        scene.frame_current = frame
        rand_all()
        scene.update()
        
        #REFERENCE IMAGE
        prep_ref(scene)
        render(scene, HEAD_CAM, "{:>04}_head_ref".format(frame))
        render(scene, RIGHT_CAM, "{:>04}_right_ref".format(frame))
        
        #SEGMENTATION IMAGE
        prep_seg(scene)
        render(scene, HEAD_CAM, "{:>04}_head_seg".format(frame))
        render(scene, RIGHT_CAM,"{:>04}_right_seg".format(frame))
        
        #DEPTH IMAGE
        scene.use_nodes = True
        render(scene, HEAD_CAM, "{:>04}_head_dep".format(frame))
        render(scene, RIGHT_CAM, "{:>04}_right_dep".format(frame))
        scene.use_nodes = False
        
        #XML
        doc, tag, _ = Doc().tagtext()
        
        with tag('view', name='head'):
            bones_to_join_xml(tag, HEAD_CAM, PALM)
            
        with tag('view', name='right'):
            bones_to_join_xml(tag, RIGHT_CAM, PALM)
        
        xml_string = indent(
            doc.getvalue(),
            indentation = ' '*2,
            newline = '\r\n'
        )
        
        file = open(bpy.path.abspath(prefix) + "{:>04}_annotation.xml".format(frame), 'w')
        file.write(xml_string)
        file.close()