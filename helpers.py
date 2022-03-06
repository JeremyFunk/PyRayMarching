import math
import settings
import os
from scipy.spatial.transform import Rotation as R

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
    
def interpolate(v1, v2, f):
    return v1 * (1 - f) + v2 * f

def clamp(val, min, max):
    return min if val < min else (max if val > max else val)

def vec_dot(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1] + vec1[2] + vec2[2]

def vec_max(vec, val):
    return [max(vec[0], val), max(vec[1], val),max(vec[2], val)]
    
def vec_min(vec, val):
    return [min(vec[0], val), min(vec[1], val),min(vec[2], val)]

def matrix_vec_mul(matrix, d):
    x = d[0] * matrix[0][0] + d[1] * matrix[1][0] + d[2] * matrix[2][0] + matrix[3][0]
    y = d[0] * matrix[0][1] + d[1] * matrix[1][1] + d[2] * matrix[2][1] + matrix[3][1]
    z = d[0] * matrix[0][2] + d[1] * matrix[1][2] + d[2] * matrix[2][2] + matrix[3][2]
    w = 1 / (d[0] * matrix[0][3] + d[1] * matrix[1][3] + d[2] * matrix[2][3] + matrix[3][3])
    return [x * w, y * w, z * w]
    
def matrix_dir_mul(matrix, d):
    x = d[0] * matrix[0][0] + d[1] * matrix[1][0] + d[2] * matrix[2][0];
    y = d[0] * matrix[0][1] + d[1] * matrix[1][1] + d[2] * matrix[2][1];
    z = d[0] * matrix[0][2] + d[1] * matrix[1][2] + d[2] * matrix[2][2];
    return [x, y, z]

def matrix_matrix_mul(a, b):
    e = matrix_identity()
    for i in range(4):
        for j in range(4):
            e[i][j] = a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j] + a[i][3] * b[3][j]
    return e


def matrix_identity():
    return [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ]

def matrix_rotation(vec):
    x = math.radians(vec[0])
    x_cos = math.cos(x)
    x_sin = math.sin(x)
    x_mat = matrix_identity()

    x_mat[1][1] = x_cos
    x_mat[1][2] = -x_sin
    x_mat[2][1] = x_sin
    x_mat[2][2] = x_cos


    y = math.radians(vec[1])
    y_cos = math.cos(y)
    y_sin = math.sin(y)
    y_mat = matrix_identity()

    y_mat[0][0] = y_cos
    y_mat[0][2] = y_sin
    y_mat[2][0] = -y_sin
    y_mat[2][2] = y_cos

    
    z = math.radians(vec[2])
    z_cos = math.cos(z)
    z_sin = math.sin(z)
    z_mat = matrix_identity()

    z_mat[0][0] = z_cos
    z_mat[0][1] = -z_sin
    z_mat[1][0] = z_sin
    z_mat[1][1] = z_cos

    return matrix_matrix_mul(matrix_matrix_mul(x_mat, y_mat), z_mat)

def matrix_translation(rot, pos):
    rot_matrix = matrix_rotation(rot)
    rot_matrix[3][0] = pos[0]
    rot_matrix[3][1] = pos[1]
    rot_matrix[3][2] = pos[2]

    return rot_matrix

def matrix_transpose(matrix):
    t = matrix_identity()
    t[0][0] = matrix[0][0]
    t[0][1] = matrix[1][0]
    t[0][2] = matrix[2][0]
    t[0][3] = matrix[3][0]

    t[1][0] = matrix[0][1]
    t[1][1] = matrix[1][1]
    t[1][2] = matrix[2][1]
    t[1][3] = matrix[3][1]

    t[2][0] = matrix[0][2]
    t[2][1] = matrix[1][2]
    t[2][2] = matrix[2][2]
    t[2][3] = matrix[3][2]

    t[3][0] = matrix[0][3]
    t[3][1] = matrix[1][3]
    t[3][2] = matrix[2][3]
    t[3][3] = matrix[3][3]

    return t

def save_video():
    os.system("ffmpeg -r " + str(settings.fps) + " -i results/img%01d.png -vb 20M -vcodec mpeg4 -y results/movie.mp4")





# Copied from https://stackoverflow.com/questions/32114054/matrix-inversion-without-numpy
def _get_matrix_minor(m,i,j):
    return [row[:j] + row[j+1:] for row in (m[:i]+m[i+1:])]

def _get_matrix_deternminant(m):
    #base case for 2x2 matrix
    if len(m) == 2:
        return m[0][0]*m[1][1]-m[0][1]*m[1][0]

    determinant = 0
    for c in range(len(m)):
        determinant += ((-1)**c)*m[0][c]*_get_matrix_deternminant(_get_matrix_minor(m,0,c))
    return determinant

def matrix_inv(m):
    determinant = _get_matrix_deternminant(m)
    #special case for 2x2 matrix:
    if len(m) == 2:
        return [[m[1][1]/determinant, -1*m[0][1]/determinant],
                [-1*m[1][0]/determinant, m[0][0]/determinant]]

    #find matrix of cofactors
    cofactors = []
    for r in range(len(m)):
        cofactorRow = []
        for c in range(len(m)):
            minor = _get_matrix_minor(m,r,c)
            cofactorRow.append(((-1)**(r+c)) * _get_matrix_deternminant(minor))
        cofactors.append(cofactorRow)
    cofactors = matrix_transpose(cofactors)
    for r in range(len(cofactors)):
        for c in range(len(cofactors)):
            cofactors[r][c] = cofactors[r][c]/determinant
    return cofactors