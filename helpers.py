import math
import settings
import os

def vec_len_squared(vec):
    return vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]

def vec_len(vec):
    return math.sqrt(vec_len_squared(vec))


def vec2_len_squared(vec):
    return vec[0] * vec[0] + vec[1] * vec[1]

def vec2_len(vec):
    return math.sqrt(vec2_len_squared(vec))

def vec_normalize(vec):
    vec_l = vec_len(vec)
    if vec_l > 0:
        len_inv = 1 / vec_l
        return [vec[0] * len_inv, vec[1] * len_inv, vec[2] * len_inv]
    return vec

def vec_convert_to_rgb(vec):
    return [vec[0] * 255, vec[1] * 255, vec[2] * 255]

def vec_clamp(vec, min, max):
    return [clamp(vec[0], min, max), clamp(vec[1], min, max), clamp(vec[2], min, max)]
    

def vec_interpolate(vec1, vec2, val):
    val_inv = 1 - val
    return [vec1[0] * val + vec2[0] * val_inv, vec1[1] * val + vec2[1] * val_inv, vec1[2] * val + vec2[2] * val_inv]
    
def clamp(val, min, max):
    return min if val < min else (max if val > max else val)

def vec_dot(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] + vec2[2]

def vec_max(vec, val):
    return [max(vec[0], val), max(vec[1], val),max(vec[2], val)]
    
def vec_min(vec, val):
    return [min(vec[0], val), min(vec[1], val),min(vec[2], val)]

def save_video():
    os.system("ffmpeg -r " + str(settings.fps) + " -i results/img%01d.png -vb 20M -vcodec mpeg4 -y results/movie.mp4")

