#!/usr/bin/python

"""

This module transforms six input images that form a cube map into an
equirectangular panorama image.

Folders tree is the following:
    
    Carla_cubemap2equirectangular
        |
        |--> cube2equi_main.py
        |--> cube2equi.py
        |--> output
        |--> input
            |
            |--> front
            |--> right
            |--> left
            |--> top
            |--> bottom

NOTE: Back images are not needed. They are automatically created.
    
Input images must be stored at folders front, right, left, top and 
bottom. 
Name formatting is of the type:
    '000000', '000001', ... , '000010', '000011', ... , '000100', '000101',etc
    
    
Example:
    Type the following command on an opened terminal in order to run the script

        $ python cube2equi_main.py
        
@author: Miguel Ángel Bueno Sánchez
@date: 29/10/2018

"""

from PIL import Image

from cube2equi import cubemap_to_equirectangular

import math


PATH = './input'
IMAGE_FORMAT = '.png'
TILE_SIZE = 1024


def main():
    """
    Loops through all cubemaps and generates an equirectangular projection 
    image for each one of them.
    """
    cubemap = Image.open(r'cubemap.png')
    output_height = math.floor(cubemap.size[0]/3)
    output_width = 2*output_height
    n = math.floor(cubemap.size[1]/3)
    
    output_img = Image.new('RGB', (output_width, output_height))
    print(output_img.size)

    for ycoord in range(0, output_height):
        for xcoord in range(0, output_width):
            corrx, corry, face = cubemap_to_equirectangular(xcoord,
                                                                  ycoord, 
                                                                  output_width, 
                                                                  output_height,
                                                                  n)
            output_img.putpixel((xcoord, ycoord), cubemap.getpixel((corrx,corry)))
    output_img.save('./output_equi'+'.png')


if __name__ == "__main__":
    main()