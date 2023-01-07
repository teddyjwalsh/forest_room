import numpy as np

SPOTLIGHT = 0
POINTLIGHT = 1
DIRECTIONAL = 2
AMBIENT = 3

class Light(object):
    def __init__(self):
        self.position = np.array([0.0,0.0,0.0])
        self.color = np.array([0.0,0.0,0.0])
        self.type = SPOTLIGHT
        self.direction = np.array([0.0,0.0,0.0])
        self.spot_angle = 180

def normalize(in_vec):
    return in_vec/np.linalg.norm(in_vec)

def is_point_in_cone(cone_loc, cone_dir, cone_angle, point):
    cone_to_point = normalize(point - cone_loc)
    angle = np.acos(np.dot(cone_to_point, cone_dir))
    return angle < cone_angle

class LightScene(object):
    def __init__(self):
        self.real_lights = []
        self.abstract_lights = []

    # Translates abstract lights into
    # Best representation the real lights
    # can provide
    def translate(self):
        print("TRANS")
        for real_light in self.real_lights:
            real_light.color = np.array([0.0,0.0,0.0])
        for abs_light in self.abstract_lights:
            for real_light in self.real_lights:
                abs_dir = abs_light.direction
                abs_loc = abs_light.position
                distance = np.linalg.norm(abs_loc - real_light.position)
                distance_factor = 1.0/(distance**2)
                if abs_light.type == POINTLIGHT:
                    abs_dir = real_light.direction
                elif abs_light.type == AMBIENT:
                    abs_dir = real_light.direction
                    distance_factor = 1.0
                elif abs_light.type == DIRECTIONAL:
                    if np.dot(abs_dir, real_light.direction) < 0:
                        continue
                    distance_factor = 1.0
                else:
                    if not is_point_in_cone(abs_loc, abs_dir, abs_light.spot_angle, real_light.position):
                        continue
                dot_factor = np.dot(abs_dir, real_light.direction)
                real_light.color += abs_light.color*dot_factor*distance_factor
                print("TEST2", real_light.color, dot_factor, distance_factor)