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

import numbers

SUPPORTED_3DL_BIT_DEPTHS = [8, 10]
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


def generate_3dl_identity_data(bit_depth_3dl):
    if bit_depth_3dl not in HEADER_3DL_INTERVALS
        raise NotImplementedError('{}-bit color depth is not supported'.format(bit_depth))
    intervals = HEADER_3DL_INTERVALS[bit_depth] 
    interval_values = intervals.split()
    interval_count = len(interval_values)
    width = interval_count * IDENTITY_IMAGE_COLUMN_MULTIPLIER
    height = math.ceil(interval_count**3/width)
    bit_depth_image = None
    if bit_depth_3dl
    data = []
    for r in interval_values:
        for g in interval_values:
            for b in interval_values:
                data.extend([r, g, b])
    return data, width, height


def write_png(path, data, width, height, bit_depth):
    """
    Create an "identity" PNG file.
    """
    writer = png.writer(
        width=width,
        height=height,
        bitdepth=bit_depth,
    )
    writer.write_array(path, data)


########################################

class ColorLUT(object):
    """
    """
    def __init__(self, data, sample_count=None, input_domain=None, flip_r_b=False):
        if not isinstance(data, list) or not isinstance(data[0], numbers.Number):
            raise ValueError('data parameter should be a flat list of numbers.')
        if not isinstance(sample_count, int):
            raise ValueError('sample_count parameter should be of type int.')
        if not isinstance(input_domain, tuple) or not isinstance(input_domain[0], numbers.Number) or len(input_domain) != 3:
            raise ValueError('input_domain parameter should be a tuple of input domains for all 3 channels.')
        if not len(data) == 3 * (sample_count**3): 
            raise ValueError('The sample invervals do not appear to match the matrix dimensions.')
        self.data = data
        self.sample_count = sample_count
        self.input_domain = input_domain
        if flip_r_b:
            _flip_r_b()

    def _flip_r_b(self):
        """
        Reorder the data values in order to make the red/blue channels
        increment most/least rapidly, or least/most rapidly, whichever is
        opposite to the previous state..

        Some Color LUT formats may increment the red channel most rapidly,
        others the blue channel.  This function helps to convert between the
        two styles of representing 3D matricies in memory.
        """
        data_flipped = array(self.data.typecode)
        for x in range(self.sample_count):
            for y in range(self.sample_count):
                for z in range(self.sample_count):
                    idx = x + self.sample_count * y + self.sample_count^2 * z
                    value3D = self.data[idx:idx+3]
                    data_flipped.extend(value3D)
        del self.data
        self.data = data_flipped

    @classmethod
    def from_haldclut(cls, src):
        png.Reader(filename=src)
        width, height, pixels, meta = png.read_flat()
        if 'palette' in meta:
            raise ValueError('Then given PNG file uses a color palette. Refusing.')
        if 'gamma' in meta:
            raise ValueError('Then given PNG file contains a gamma value. Refusing.')
        if 'transparent' in meta:
            raise ValueError('Then given PNG file specifies a transparent color. Refusing.')
        if meta['alpha']:
            raise ValueError('Then given PNG file contains an alpha channel. Refusing.')
        if meta['greyscale']:
            raise ValueError('Then given PNG file is greyscale. Refusing.')
        if meta['bitdepth'] not in (8, 16):
            raise ValueError('Then given PNG file specifies an unsupported bit depth. Refusing.')
	width_is_power_of_two = (width & (width - 1)) == 0
        if width != height or not width_is_power_of_two:
            raise ValueError('The given PNG file does not have appropriate Hald CLUT dimensions. Refusing.')
        sample_count = int(round((width**2)**(1./3)))
        input_domain = 2**meta['bitdepth']
        return cls(data, sample_count, input_domain)


@click.command()
@cli.argument(
    'src',
    type=click.Path(exists=True, dir_okay=False)
)
@click.option(
    'type', '--dest-type',
    help='Type of color LUT.',
    type=click.Choice(['3dl', 'haldclut']),
    required=True,
)
def cli(src, dest_type):
    if not src:
        raise ValueError('Please specify a source LUT')
    ext = src.lower().split('.')[-1]
    if ext == 'png':
        clut = ColorLUT.from_haldclut(src)
    elif ext == '3dl':
        clut = ColorLUT.from_3dl(src)
    elif ext == 'cube':
        clut = ColorLUT.from_haldclut(src)
    else:
        raise ValueError('Not an appropriate Color LUT file type: {}'.format(ext))
    if dest_type == 'haldclut':
        clut.write_haldclut()
    elif dest_type == '3dl':
        clut.write_3dl()
    elif dest_type == 'cube':
        clut.write_cube()
    else:
        raise ValueError('Not an appropriate Color LUT file type: {}'.format(ext))


if __name__ == '__main__':
    cli()
