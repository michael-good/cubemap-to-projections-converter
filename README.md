# cubemap-to-projections-converter

## Project Overview

A simple GUI that allows the user to convert a 360 degrees cubemap image into both an equirectangular image panorama and a fisheye image with the specified field of view. 

## Requirements

Just two:
  - Pillow
  - Numpy

More information within requirements.txt.
  
## How to run

# Linux / MAC

With Python 3 and all requirements installed, just run the following command in the folder of the project:

`<addr>` python3 cubemap-converter.py

# Windows

Open a command line in the project root folder and type the following:

`<addr>` python cubemap-converter.py


## Input files

Input image must be a cubemap with the following structure (see also cubemap.png image):

![Alt Text](/cubemap.png)

Bear in mind that all 6 tiles must be of the same size.

## Output files

There can be two different outputs:
  - Fisheye image with a certain resolution specified by the user.
  - Equirectangular image. Its dimensions are fixed and depend on the input image size.

## Contact information

Name: Miguel Ángel Bueno Sánchez

email: miguelangelbuenos@gmail.com
