import os
import bpy
import random

WDIR = os.path.dirname(os.path.dirname(__file__))
BGD_DIR = os.path.join(WDIR, "..\\dataset\\bgd")
BGDS = [os.path.join(BGD_DIR, f) for f in os.listdir(BGD_DIR) if os.path.isfile(os.path.join(BGD_DIR, f))]
CURR_BGD = bpy.data.images['bgdtex']
SKIN = bpy.data.materials['ted2']

def on_pre_render(scene):
    if bpy.data.scenes['Scene'].render.use_antialiasing:
        bgd_path = random.choice(BGDS)
        CURR_BGD.filepath = bgd_path
        bpy.types.Image(CURR_BGD).reload()
        SKIN.diffuse_intensity = random.random()

def register():
    bpy.app.handlers.render_pre.append(on_pre_render)

def unregister():
    bpy.app.handlers.render_pre.remove(on_pre_render)
    
if __name__ == "__main__":
    register()