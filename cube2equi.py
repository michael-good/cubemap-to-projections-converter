#!/usr/bin/python

"""

@author: Miguel Ángel Bueno Sánchez
@date: 29/10/2018

"""

import math

def spherical_coordinates(i, j, width, height):
    """
    Computes spherical coordinates of an input pixel on the output
    image.
    :param i: horizontal pixel coordinate on output image.
    :param j: vertical pixel coordinate on output image.
    :param width: dimension of output image.
    :param height: dimension of output image.
    :return: spherical coordinates.
    """
    
    x = 2*i/width - 1
    y = 2*j/height - 1
    return y*math.pi/2, x*math.pi                         

def cartesian_coordinates(phi, theta):
    """
    Transforms spherical coordinates into cartesian.
    :param phi: spherical coordinate.
    :param theta: spherical coordinate.
    :return: x, y, z cartesian coordinates.
    """
    
    return(math.cos(phi)*math.cos(theta),
           math.sin(phi),
           math.cos(phi)*math.sin(theta))

def get_face(x, y, z):
    """
    Finds which face of a cube map a 3D vector with origin
    at the center of the cube points to
    :param x, y, z: cartesian coordinates
    :return: string that indicates the face
    """
    
    max_axis = max(abs(x), abs(y), abs(z))
    
    if math.isclose(max_axis, abs(x)):
        return 'X+' if x < 0 else 'X-'
    elif math.isclose(max_axis, abs(y)):
        return 'Y+' if y < 0 else 'Y-'
    elif math.isclose(max_axis, abs(z)):
        return 'Z+' if z < 0 else 'Z-'

def tile_coordinates(face, x, y, z):
    """
    Finds u,v coordinates (image coordinates) for a given
    3D vector.
    :param face: face where the vector points to.
    :param x, y, z: vector cartesian coordinates.
    :return: uv image coordinates.
    """
    
    if face == 'X+':
        sc = -z
        tc = y
        ma = abs(x)
    elif face == 'X-':
        sc = z
        tc = y
        ma = abs(x)
    elif face == 'Y+':
        sc = z
        tc = x
        ma = abs(y)
    elif face == 'Y-':
        sc = z
        tc = -x
        ma = abs(y)
    elif face == 'Z-':
        sc = -x
        tc = y
        ma = abs(z)
    elif face == 'Z+':
        sc = x
        tc = y
        ma = abs(z)
    return (sc/ma + 1)/2, (tc/ma + 1)/2

def tile_origin_coordinates(face, n):
    """
    Finds the position of each tile on the cube map.
    :param face: face where a vector points to.
    :param n: tiles size.
    :return: the position of each tile on the cube map.
    """
    
    if face == 'X+':
        return 3*n, n
    elif face == 'X-':
        return n, n
    elif face == 'Y+':
        return n, 0
    elif face == 'Y-':
        return n, 2*n
    elif face == 'Z+':
        return 0, n
    elif face == 'Z-':
        return 2*n, n

def final_coordinates(face, x, y, n):
    """
    Finds coordinates on the 2D cube map image of a 3D
    vector.
    :param face: face where a 3D vector points to.
    :param x, y: image coordinates.
    :param n: tiles size.
    :return: coordinates on the 2D cube map image.
    """
    
    face_coords = tile_origin_coordinates(face, n)
    normalized_x = math.floor(x*n)
    normalized_y = math.floor(y*n)

    if normalized_x < 0:
        normalized_x = 0
    elif normalized_x >= n:
        normalized_x = n-1
    if normalized_y < 0:
        normalized_x = 0
    elif normalized_y >= n:
        normalized_y = n-1
        
    return face_coords[0] + normalized_x, \
           face_coords[1] + normalized_y, face

def cubemap_to_equirectangular(i, j, w, h, n):
    """
    Receives the location of a pixel on the output canvas 
    and finds which pixel of the cube map image corresponds
    to that position.
    :param i: horizontal pixel coordinate on output image.
    :param j: vertical pixel coordinate on output image.
    :param w: dimension of output image.
    :param h: dimension of output image.
    :param n: tiles size.
    :return: coordinates on the 2D cube map image.
    """
    
    spherical = spherical_coordinates(i, j, w, h)
    vector_coords = cartesian_coordinates(spherical[0], spherical[1])
    face = get_face(vector_coords[0], vector_coords[1], vector_coords[2])
    raw_face_coords = tile_coordinates(face, vector_coords[0], 
                                       vector_coords[1], vector_coords[2])

    return final_coordinates(face, raw_face_coords[0], 
                             raw_face_coords[1], n)