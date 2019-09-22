"""

@author: michael-good

"""
import numpy as np

import math

np.warnings.filterwarnings("ignore", category=RuntimeWarning)


def spherical_to_cartesian(r, phi, fov):
    """
    Transforms spherical coordinates to cartesian
    :param r: matrix with computed pixel heights
    :param phi: matrix with computed pixel angles
    :param fov: desired field of view
    :return: x,y,z cartesian coordinates
    """
    theta = r * fov / 2
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)

    return x, y, z


def get_spherical_coordinates(output_height, output_width):
    """
    Finds spherical coordinates on the output image
    :param output_height: height of output image
    :param output_width: width of output image
    :return: two matrices that contain spherical coordinates
             for all pixels of the output image
    """
    cc = (int(output_height / 2), int(output_width / 2))

    y = np.arange(0, output_height, 1)
    x = np.arange(0, output_width, 1)

    xx, yy = np.meshgrid(y, x)

    bias = np.ones((output_width, output_height)) * cc[0]

    xx = np.subtract(xx, bias)
    yy = np.subtract(yy, bias)
    xx = np.divide(xx, bias)
    xx[:, -1] = 1
    yy = np.divide(yy, -bias)
    yy[-1, :] = -1

    r = np.sqrt(xx ** 2 + yy ** 2)
    r[r > 1] = np.nan
    r[r < 0] = 0

    phi = np.zeros((output_height, output_width))
    phi[:672, 672:] = np.arcsin(np.divide(yy[:672, 672:], r[:672, 672:]))
    phi[:, :672] = np.pi - np.arcsin(np.divide(yy[:, :672], r[:, :672]))
    phi[673:, 672:] = 2 * np.pi + np.arcsin(np.divide(yy[673:, 672:], r[673:, 672:]))
    phi[cc[0], cc[1]] = 0

    return r, phi


def get_face(x, y, z):
    """
    Finds which face of a cube map a 3D vector with origin
    at the center of the cube points to
    :param x, y, z: cartesian coordinates
    :return: string that indicates the face
    """

    max_axis = max(abs(x), abs(y), abs(z))

    if math.isclose(max_axis, abs(x)):
        return 'right' if x < 0 else 'left'
    elif math.isclose(max_axis, abs(y)):
        return 'bottom' if y < 0 else 'top'
    elif math.isclose(max_axis, abs(z)):
        return 'back' if z < 0 else 'front'


def raw_face_coordinates(face, x, y, z):
    """
    Finds u,v coordinates (image coordinates) for a given
    3D vector
    :param face: face where the vector points to
    :param x, y, z: vector cartesian coordinates
    :return: uv image coordinates
    """

    if face == 'left':
        u = z
        v = -y
        ma = abs(x)
    elif face == 'right':
        u = -z
        v = -y
        ma = abs(x)
    elif face == 'bottom':
        u = -x
        v = -z
        ma = abs(y)
    elif face == 'top':
        u = -x
        v = z
        ma = abs(y)
    elif face == 'back':
        u = x
        v = y
        ma = abs(z)
    elif face == 'front':
        u = -x
        v = -y
        ma = abs(z)
    else:
        raise Exception('Tile ' + face + 'does not exist')

    return (u / ma + 1) / 2, (v / ma + 1) / 2


def tile_origin_coordinates(face, face_size):
    """
    Finds the position of each tile on the cube map
    :param face: face where a vector points to
    :return: the position of each tile on the cube map
    """

    face_origin = {
        'left': (0, face_size),
        'front': (face_size, face_size),
        'right': (2 * face_size, face_size),
        'back': (3 * face_size, face_size),
        'top': (face_size, 0),
        'bottom': (face_size, 2 * face_size),
    }

    return face_origin.get(face)


def normalized_coordinates(face, x, y, n):
    """
    Finds coordinates on the 2D cube map image of a 3D
    vector
    :param face: face where a 3D vector points to
    :param x, y: image coordinates
    :param n: tiles size
    :return: coordinates on the 2D cube map image
    """

    tile_origin_coords = tile_origin_coordinates(face, n)

    tile_x = math.floor(x * n)
    tile_y = math.floor(y * n)

    if tile_x < 0:
        tile_x = 0
    elif tile_x >= n:
        tile_x = n - 1
    if tile_y < 0:
        tile_y = 0
    elif tile_y >= n:
        tile_y = n - 1

    x_cubemap = tile_origin_coords[0] + tile_x
    y_cubemap = tile_origin_coords[1] + tile_y

    return x_cubemap, y_cubemap
