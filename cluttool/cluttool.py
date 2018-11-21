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
import png
from array import array

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

def uniform_intervals(end, samples, floating_point=False, exclusive_end=True):
    """
    Make `samples` uniformly distributed numbers from 0 to `end`.
    """
    dist = end/float(samples-1)
    values = [dist*i for i in range(samples)]
    if not floating_point:
        values = [int(round(v)) for v in values]
        if exclusive_end:
            values[-1] = values[-1]-1
        for idx in range(1, samples):
            actual_dist = values[idx] - values[idx-1]
            error_frac = abs(float(actual_dist)/dist - 1.0)
            if error_frac > 0.03:
                raise ValueError('input parameters to uniform_intervals would yield a non-uniform distribution.')
    return values

def scale_color_value(color_value, scaling_factor):
    if scaling_factor is not None:
        color_value = array(
            color_value.typecode,
            ch*self.scaling_factor for ch in color_value,
        )
    return color_value

def index_3D(data, size, r_idx, g_idx, b_idx):
    """
    Index a flattened 3-channel 3D cubic matrix.
    """
    idx = r + size * g + size^2 * b
    return data[idx:idx+3]
    

class ColorLUT(object):
    """
    """
    def __init__(self, data, sample_count=None, input_domain=None, red_increments_fastest=True):
        if not isinstance(data, array) or not isinstance(data[0], numbers.Number):
            raise ValueError('data parameter should be a flat list of numbers.')
        if not isinstance(sample_count, int):
            raise ValueError('sample_count parameter should be of type int.')
        if not isinstance(input_domain, numbers.Number):
            raise ValueError('input_domain parameter should be a number.')
        if isinstance(input_domain, numbers.Real):
            if data.typecode not in 'fd':
                raise ValueError('input_domain parameter should have the same type as the data.')
        else:
            if data.typecode not in 'bBhHiIlL':
                raise ValueError('input_domain parameter should have the same type as the data.')
        if not len(data) == 3 * (sample_count**3): 
            raise ValueError('The sample intervals do not appear to match the matrix dimensions.')
        self.data = data
        self.sample_count = sample_count
        self.input_domain = input_domain
        self.red_increments_fastest = red_increments_fastest

    #@property
    #def input_invervals(self):
    #    if hasattr(self, '_input_intervals'):
    #        return self._input_intervals
    #    self._input_intervals = [i*self.input_domain for i in range(self.sample_count)]

    @property
    def sample_distance(self):
        if hasattr(self, '_sample_distance'):
            return self._sample_distance
        self._sample_distance = self.input_domain / float(self.sample_count-1)

    def get_color_value_from_index(self, r_idx, g_idx, b_idx):
        """
        Determine the output color value given 3D matrix indices.
        """
        if not self.red_increments_fastest:
            r_idx, b_idx = b_idx, r_idx
        return index_3D(self.data, self.sample_count, r_idx, g_idx, b_idx)

    def get_interpolated_color_value(self, r_input, g_input, b_input):
        """
        Determine the output color value using trilinear interpolation.
 
        Algorithm copied from https://en.wikipedia.org/wiki/Trilinear_interpolation
        """
        # On wikipedia, the equations for v_d were:
        #
        #   r_d = ( r - r_0 ) / ( r_1 - r_0 )
        #   g_d = ( g - g_0 ) / ( g_1 - g_0 )
        #   b_d = ( b - b_0 ) / ( b_1 - b_0 )
        #
        # but v−v_0 is equivalent to math.remainder(v, self.sample_distance),
        # and v_0−v_1 is equivalent to self.sample_distance.
        r_d = math.remainder(r_input, self.sample_distance) / self.sample_distance
        g_d = math.remainder(g_input, self.sample_distance) / self.sample_distance
        b_d = math.remainder(b_input, self.sample_distance) / self.sample_distance

        r_0_idx = math.trunc(r_input/self.sample_distance)
        g_0_idx = math.trunc(g_input/self.sample_distance)
        b_0_idx = math.trunc(b_input/self.sample_distance)

        r_1_idx = r_0_idx + 1
        g_1_idx = g_0_idx + 1
        b_1_idx = b_0_idx + 1

        c_000 = self.get_color_value_from_index(r_0_idx, g_0_idx, b_0_idx)
        c_001 = self.get_color_value_from_index(r_0_idx, g_0_idx, b_1_idx)
        c_010 = self.get_color_value_from_index(r_0_idx, g_1_idx, b_0_idx)
        c_011 = self.get_color_value_from_index(r_0_idx, g_1_idx, b_1_idx)
        c_100 = self.get_color_value_from_index(r_1_idx, g_0_idx, b_0_idx)
        c_101 = self.get_color_value_from_index(r_1_idx, g_0_idx, b_1_idx)
        c_110 = self.get_color_value_from_index(r_1_idx, g_1_idx, b_0_idx)
        c_111 = self.get_color_value_from_index(r_1_idx, g_1_idx, b_1_idx)

        c_00 = c_000*(1-r_d) + c_100*r_d
        c_01 = c_001*(1-r_d) + c_101*r_d
        c_10 = c_010*(1-r_d) + c_110*r_d
        c_11 = c_011*(1-r_d) + c_111*r_d

        c_0 = c_00*(1-g_d) + c_10*g_d
        c_1 = c_01*(1-g_d) + c_11*g_d

        c = c_0*(1-b_d) + c_1*b_d

        return c

    def get_values_translated(
        self,
        increment_red_fastest=True,
        floating_point_output=False,
        output_sample_count=None,
        output_domain=None,
        ):
        """
        Make a generator of color values in sequence.

        Reorder the data values in order to make the red/blue channels
        increment most/least rapidly, or least/most rapidly, whichever is
        opposite to the previous state.

        Some Color LUT formats may increment the red channel most rapidly,
        others the blue channel.  This function helps to convert between the
        two styles of representing 3D matrices in memory.
        """
        return_flipped = self.red_increments_fastest ^ increment_red_fastest
        if return_flipped:
            for x in range(self.sample_count):
                for y in range(self.sample_count):
                    for z in range(self.sample_count):
                        idx = x + self.sample_count * y + self.sample_count^2 * z
                        color_value = convert_color_value()
                        color_value = scale_color_value(self.data[idx:idx+3], self._domain_scaling_factor)
                        yield color_value
        else:
            for i3 in self.sample_count**3:
                idx = i3*3
                color_value = scale_color_value(self.data[idx:idx+3], self._domain_scaling_factor)
                yield color_value

    @classmethod
    def from_haldclut(cls, src):
        src_png = png.Reader(filename=src)
        width, height, pixels, meta = src_png.read_flat()
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
        input_domain = 2**meta['bitdepth']-1
        return cls(data, sample_count=sample_count, input_domain=input_domain)

    @classmethod
    def from_3dl(cls, src):
        raise NotImplementedError()

    def to_haldclut(self):
        raise NotImplementedError()


    def to_3dl(cls, dest):
        sample_intervals = uniform_intervals(self.input_domain, self.sample_count)
        sample_intervals = ' '.join(str(v) for v in sample_intervals)
        color_value_gen = self.get_values_translated(increment_red_fastest=False)
        with open(dest, 'w') as destfile:
            destfile.write(' '.join(sample_intervals))
            destfile.write('\n')
            for color in color_value_gen:
                line = ' '.join(str(v) for v in color)
                destfile.write(line)
                destfile.write('\n')


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
