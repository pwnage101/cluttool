#!/usr/bin/env python3
#
# Copyright (C) 2018 Troy Sankey
# This file is released under the GNU GPL, version 3 or a later revision.
# For further details see the COPYING file
#
# References:
# - Hald CLUT reference: http://www.quelsolaar.com/technology/clut.html
# - 3D LUT (3DL) reference: http://download.autodesk.com/us/systemdocs/pdf/lustre_color_management_user_guide.pdf#page=14

import sys
import click

SUPPORTED_BIT_DEPTHS = [8, 10]
SUPPORTED_IMAGE_FILETYPES = ['png']

# The 3DL format begins with a list of values (i.e. sampling intervals) from
# minimum to maximum (i.e. 0-255 for 8-bit depth) which are uniformly
# distributed, describing the "segmentation".  The specification does not state
# how many segments should be allowed, but it does offer an example header for
# 10-bit values using 17 sampling intervals (copied verbatim below).  For 8-bit
# values, the segmentation is perfectly uniform if we instead use 16 sampling
# intervals, so that is what I've decided to use for this tool.
#
# According to a random source on the internet, LUT interval counts anywhere
# from 5 to 64 are common, but 17 is usually good enough when using a good
# interpolation method.
#
# More info:
# http://download.autodesk.com/us/systemdocs/pdf/lustre_color_management_user_guide.pdf#page=14
#
HEADER_3DL_INTERVALS = {
    8:  '0 17 34 51 68 85 102 119 136 153 170 187 204 221 238 255',
    10: '0 64 128 192 256 320 384 448 512 576 640 704 768 832 896 960 1023',
}

# The PMM header describes the width and height of the image in pixels,
# followed by the maximum color component value.
HEADER_PPM_FMT = 'P3 {} {} {}'

# The higher this number, the wider the aspect ratio of the identity image.
# The current value of 4 tends to make the resulting image square when using
# the 16- or 17-sample headers above.
IDENTITY_IMAGE_COLUMN_MULTIPLIER = 4


def fatal_error(message):
    """
    Display an error message and exit.
    """
    click.echo(message)
    sys.exit(1)


def max_value_for_bit_depth(bit_depth):
    if not isinstance(bit_depth, int):
        raise TypeError
    return (2**bit_depth)-1


def generate_identity_data(bit_depth):
    if bit_depth not in HEADER_3DL_INTERVALS
        raise NotImplementedError('{}-bit color depth is not supported'.format(bit_depth))
    intervals = HEADER_3DL_INTERVALS[bit_depth] 
    interval_values = intervals.split()
    interval_count = len(interval_values)
    width = interval_count * IDENTITY_IMAGE_COLUMN_MULTIPLIER
    height = math.ceil(interval_count**3/width)
    data = []
    for r in interval_values:
        for g in interval_values:
            for b in interval_values:
                data.extend([r, g, b])
    return data, width, height


def generate_identity_png(out_filename, bit_depth):
    """
    Create an "identity" 3DL PNG file.
    """
    data, width, height = generate_identity_data(bit_depth)
    writer = png.writer(
        width=width,
        height=height,
        bitdepth=bit_depth,
    )
    writer.write_array(out_filename, data)

@click.group()
def cli():
    """
    This is the top level command, which doesn't do anything on its own.
    """
    pass

@cli.command()
@click.argument(
    'output_filename',
    type=click.Path(exists=False)
)
@click.option(
    'bit_depth', '--bit-depth',
    help='bit depth represented by 3DL identity image',
    default=SUPPORTED_BIT_DEPTHS[0],
    type=click.Choice(SUPPORTED_BIT_DEPTHS)
)
def identity_image(bit_depth, filetype):
    """
    Generate a 3D LUT "identity" image to use with your favorite image editor.
    """
    generate_identity_image_func = {
        'png': generate_identity_png,
    }[filetype]
    generate_identity_image_func(out_filename, bit_depth)


@click.argument(
    'transformed_image_filename',
    type=click.Path(exists=True, dir_okay=False)
)
def lut_from_transformed_image(transformed_image_filename):
    """
    Generate a 3D LUT file (.3dl) based on the given transformed image file.
    """
    if '.' not in transformed_image_filename:
        raise ValueError('file type unknown: {}'.format(transformed_image_filename))
    extension = transformed_image_filename.split('.')[-1]
    if not extension in SUPPORTED_IMAGE_FILETYPES:
        raise ValueError('Inappropriate file type: {}'.format(extension))
    transformed_values_from_image_func = {
        'png': transformed_values_from_png,
    }[extension]
    transformed_values, intervals = transformed_values_from_image_func()


if __name__ == '__main__':
    cli()
