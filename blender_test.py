import bpy
import mathutils
import sys
import numpy as np
import os
import math
script_dir = "C:\\Users\\tjwal\\projects\\rainforest"
if not script_dir in sys.path:
    sys.path.append(script_dir)
import light_cycle
import imp
imp.reload(light_cycle)

output_dir = "C:\\Users\\tjwal\\projects\\rainforest"
num_frames = 1


for i in range(0,num_frames):

    lc_lights = []

    scene_lights = [ob for ob in bpy.data.objects if ob.type == 'LIGHT']
    for light_ob in scene_lights:
        light = light_ob.data
        if "rgb led" in light_ob.name:
            print(light_ob.name)
            forward = mathutils.Vector([0.0,0.0,-1.0])
            rot =(light_ob.rotation_euler.to_quaternion())
            forward.rotate(rot)
            print(forward)
            light.show_cone = False
            new_light = light_cycle.Light()
            new_light.direction = np.array(forward)
            new_light.position = np.array(light_ob.location)
            new_light.type = light_cycle.SPOTLIGHT
            new_light.name = light_ob.name
            lc_lights.append(new_light)

    ls =light_cycle.LightScene()
    ls.real_lights = lc_lights

    cur_angle = (i*1.0/num_frames)*2*3.14159 + 335*3.14159/180
    hor_factor1 = (0.7*max(0, math.cos(cur_angle)) + 0.3)**2
    hor_factor2 = (0.55*max(0, math.cos(cur_angle)) + 0.45)**2

    new_abstract = light_cycle.Light()
    new_abstract.type = light_cycle.DIRECTIONAL
    new_abstract.color = np.array([253.0/255, hor_factor2*251.0/255, hor_factor1*211.0/255])
    new_abstract.direction = light_cycle.normalize(np.array([math.sin(cur_angle),0.0, -math.cos(cur_angle)]))
    ls.abstract_lights.append(new_abstract)

    new_abstract = light_cycle.Light()
    new_abstract.type = light_cycle.AMBIENT
    new_abstract.color = np.array([0.07,0.08,0.2])*2.0
    new_abstract.direction = light_cycle.normalize(np.array([0.7,0.0,-0.4]))
    ls.abstract_lights.append(new_abstract)
    
    '''
    new_abstract = light_cycle.Light()
    new_abstract.type = light_cycle.AMBIENT
    new_abstract.color = np.array([133.0/255, 138.0/255, 143.0/255])
    new_abstract.direction = light_cycle.normalize(np.array([-0.1,0.0,-0.8]))
    ls.abstract_lights.append(new_abstract)
    '''

    ls.translate()

    for rl in ls.real_lights:
        bpy_obj = bpy.data.objects[rl.name]
        print(mathutils.Vector(rl.color))
        bpy_obj.data.color = mathutils.Vector(rl.color)
    print(hor_factor1, hor_factor2)
    #bpy.context.scene.render.filepath = os.path.join(output_dir, str(i))
    #bpy.ops.render.render(write_still = True)