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
import numbers
from array import array
from decimal import Decimal
import math
import png
import click


def fatal_error(message):
    """
    Display an error message and exit.
    """
    click.echo(message)
    sys.exit(1)

def is_perfect_six_root(n):
    c = int(n**(1/6.))
    return (c**6 == n) or ((c+1)**6 == n)

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


def uniform_intervals(end, samples, floating_point=False):
    """
    Make `samples` uniformly distributed numbers from 0 to `end`.
    """
    dist = end/float(samples-1)
    values = [dist*i for i in range(samples)]
    if not floating_point:
        values = [int(round(v)) for v in values]
        for idx in range(1, samples):
            actual_dist = values[idx] - values[idx-1]
            error_frac = abs(float(actual_dist)/dist - 1.0)
            if error_frac > 0.07:
                raise ValueError('input parameters to uniform_intervals would yield a non-uniform distribution.')
    return values


class Value3D(object):

    def __init__(self, components):
        self.components = tuple(components)

    def __str__(self):
        return 'Value3D({},{},{})'.format(*self.components)

    def __bytes__(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return iter(self.components)

    def __add__(self, y):
        return Value3D(
            (
                self.components[0] + y.components[0],
                self.components[1] + y.components[1],
                self.components[2] + y.components[2],
            )
        )

    def __mul__(self, y):
        return Value3D(
            (
                self.components[0] * y,
                self.components[1] * y,
                self.components[2] * y,
            )
        )

    def __rmul__(self, x):
        return self.__mul__(x)


def index_3d(data, size, r_idx, g_idx, b_idx):
    """
    Index a flattened 3-channel 3D cubic matrix.
    """
    idx = (r_idx) + (size * g_idx) + (size**2 * b_idx)
    idx *= 3
    click.echo('index_3d(): size, r_idx, g_idx, b_idx = {},{},{},{}'.format(size, r_idx, g_idx, b_idx))
    click.echo('index_3d(): idx = {}'.format(idx))
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
        if isinstance(input_domain, numbers.Integral):
            if data.typecode not in 'bBhHiIlL':
                raise ValueError('input_domain parameter should have the same type as the data.')
        else:
            if data.typecode not in 'fd':
                raise ValueError('input_domain parameter should have the same type as the data.')
        if not len(data) == 3 * (sample_count**3):
            raise ValueError('The sample intervals do not appear to match the matrix dimensions.')
        self.data = data
        self.sample_count = sample_count
        self.input_domain = input_domain
        self.red_increments_fastest = red_increments_fastest
        if data.typecode in 'fd':
            self.datatype = numbers.Real
        elif data.typecode in 'bBhHiIlL':
            self.datatype = numbers.Integral
        self.sample_distance = self.input_domain / float(self.sample_count-1)

    def get_color_value_from_index(self, r_idx, g_idx, b_idx):
        """
        Determine the output color value given 3D matrix indices.
        """
        if not self.red_increments_fastest:
            r_idx, b_idx = b_idx, r_idx
        color_value = Value3D(index_3d(self.data, self.sample_count, r_idx, g_idx, b_idx))
        click.echo('get_color_value_from_index(): r_idx,g_idx,b_idx = {},{},{}'.format(r_idx,g_idx,b_idx))
        click.echo('get_color_value_from_index(): color_value = {}'.format(str(color_value)))
        return color_value

    def get_interpolated_color_value(self, r_input, g_input, b_input):
        """
        Determine the output color value using trilinear interpolation.

        Algorithm adapted from https://en.wikipedia.org/wiki/Trilinear_interpolation
        """
        # On wikipedia, the equations for v_d were:
        #
        #   r_d = ( r - r_0 ) / ( r_1 - r_0 )
        #   g_d = ( g - g_0 ) / ( g_1 - g_0 )
        #   b_d = ( b - b_0 ) / ( b_1 - b_0 )
        #
        # but v-v_0 is equivalent to math.remainder(v, self.sample_distance),
        # and v_1-v_0 is equivalent to self.sample_distance,
        # therefore, v_d = float(Decimal(v_input) % Decimal(self.sample_distance)) / self.sample_distance.
        #
        # Furthermore, we need to handle the border case where v_input == the
        # maximum possible value (i.e. self.input_domain).
        if r_input == self.input_domain:
            r_0_idx = self.sample_count - 2
            r_d = 1
        else:
            r_0_idx = math.trunc(r_input/self.sample_distance)
            r_d = float(Decimal(r_input) % Decimal(self.sample_distance)) / self.sample_distance

        if g_input == self.input_domain:
            g_0_idx = self.sample_count - 2
            g_d = 1
        else:
            g_0_idx = math.trunc(g_input/self.sample_distance)
            g_d = float(Decimal(g_input) % Decimal(self.sample_distance)) / self.sample_distance

        if b_input == self.input_domain:
            b_0_idx = self.sample_count - 2
            b_d = 1
        else:
            b_0_idx = math.trunc(b_input/self.sample_distance)
            b_d = float(Decimal(b_input) % Decimal(self.sample_distance)) / self.sample_distance

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

        c_00 = c_000*(1.0-r_d) + c_100*r_d
        c_01 = c_001*(1.0-r_d) + c_101*r_d
        c_10 = c_010*(1.0-r_d) + c_110*r_d
        c_11 = c_011*(1.0-r_d) + c_111*r_d

        c_0 = c_00*(1.0-g_d) + c_10*g_d
        c_1 = c_01*(1.0-g_d) + c_11*g_d

        c = c_0*(1.0-b_d) + c_1*b_d

        return c

    def get_values_translated(
            self,
            increment_red_fastest=True,
            output_sample_count=None,
            output_domain=None,
        ):
        """
        Make an iterable of output color values in sequence.

        If necessary, reorder the output data values in order to make them
        correspond to red/blue input channels incrementing most/least rapidly
        by default.  Switch increment_red_fastest=False for the opposite
        behavior
        """
        interpolate_output = output_sample_count != self.sample_count
        scale_output = output_domain != self.input_domain

        scaling_factor = output_domain / float(self.input_domain)

        if increment_red_fastest:
            indexes = (
                (r, g, b)
                for b in range(output_sample_count)
                for g in range(output_sample_count)
                for r in range(output_sample_count)
            )
        else:
            indexes = (
                (r, g, b)
                for r in range(output_sample_count)
                for g in range(output_sample_count)
                for b in range(output_sample_count)
            )

        if interpolate_output:
            input_values = (
                Value3D(idx)*(self.input_domain/float(output_sample_count-1))
                for idx in indexes
            )
            output_values = (
                self.get_interpolated_color_value(*input_value)
                for input_value in input_values
            )
        else:
            output_values = (
                self.get_color_value_from_index(*idx)
                for idx in indexes
            )

        if scale_output:
            output_values = (
                output_value*scaling_factor
                for output_value in output_values
            )

        return output_values

    @classmethod
    def from_haldclut(cls, src):
        src_png = png.Reader(filename=src)
        width, height, data, meta = src_png.read_flat()
        if 'palette' in meta:
            raise ValueError('Then given PNG file uses a color palette. Refusing.')
        if 'gamma' in meta:
            raise ValueError('Then given PNG file contains a gamma value. Refusing.')
        if 'transparent' in meta:
            raise ValueError('Then given PNG file specifies a transparent color. Refusing.')
        if meta['alpha']:
            raise ValueError('Then given PNG file contains an alpha channel. Refusing.')
        if meta['greyscale']:
            def triple_generator(d):
                for val in d:
                    yield val
                    yield val
                    yield val
            data = array(data.typecode, triple_generator(data))
        if meta['bitdepth'] not in (8, 16):
            raise ValueError('Then given PNG file specifies an unsupported bit depth. Refusing.')
        width_is_square_root_of_perfect_six_root = is_perfect_six_root(width**2)
        if width != height or not width_is_square_root_of_perfect_six_root:
            raise ValueError('The given PNG file does not have appropriate Hald CLUT dimensions. Refusing.')
        sample_count = int(round((width**2)**(1./3)))
        input_domain = 2**meta['bitdepth']-1
        click.echo('from_haldclut(): PNG dimensions = {}x{}'.format(width, height))
        click.echo('from_haldclut(): PNG bit depth = {}'.format(meta['bitdepth']))
        click.echo('from_haldclut(): PNG array typecode = {}'.format(data.typecode))
        click.echo('from_haldclut(): Inferred input domain = {}'.format(input_domain))
        click.echo('from_haldclut(): Inferred 3D matrix dimensions = {0}x{0}x{0}'.format(sample_count))
        return cls(data, sample_count=sample_count, input_domain=input_domain)

    @classmethod
    def from_3dl(cls, src):
        raise NotImplementedError()

    def write_haldclut(self):
        raise NotImplementedError()

    def write_3dl(self, dest):
        output_domain = 1023
        sample_intervals = uniform_intervals(output_domain, self.sample_count)
        color_value_gen = self.get_values_translated(
            increment_red_fastest=False,
            output_sample_count=self.sample_count,
            output_domain=output_domain,
        )
        with open(dest, 'w') as destfile:
            destfile.write('   '.join(str(v) for v in sample_intervals))
            destfile.write('\n')
            for color in color_value_gen:
                line = ' '.join('{:.0f}'.format(v) for v in color)
                destfile.write(line)
                destfile.write('\n')

    def write_cube(self, dest):
        output_domain = 1.0
        output_sample_count = self.sample_count
        color_value_gen = self.get_values_translated(
            output_sample_count=output_sample_count,
            output_domain=output_domain,
        )
        with open(dest, 'w') as destfile:
            destfile.write('LUT_3D_SIZE {}'.format(output_sample_count))
            destfile.write('\n')
            for color in color_value_gen:
                line = ' '.join('{:.7g}'.format(v) for v in color)
                destfile.write(line)
                destfile.write('\n')


@click.command()
@click.argument(
    'src',
    type=click.Path(exists=True, dir_okay=False),
)
@click.argument(
    'dest',
    type=click.Path(exists=False),
)
@click.option(
    '--dest-type',
    help='Type of color LUT.  If this argument is not provided, the output type is inferred from the destination filename extension.',
    type=click.Choice(['3dl', 'haldclut', 'cube']),
)
def cli(src, dest, dest_type):
    if not src:
        raise ValueError('Please specify a source LUT file.')
    if not dest:
        raise ValueError('Please specify a destination LUT file.')
    if not dest_type:
        dest_type = dest.lower().split('.')[-1]
        if dest_type == 'png':
            dest_type = 'haldclut'
    dest_type = dest_type.lower()
    src_ext = src.lower().split('.')[-1]
    if src_ext == 'png':
        clut = ColorLUT.from_haldclut(src)
    elif src_ext == '3dl':
        clut = ColorLUT.from_3dl(src)
    elif src_ext == 'cube':
        clut = ColorLUT.from_haldclut(src)
    else:
        raise ValueError('Not an appropriate Color LUT file type: {}'.format(src_ext))
    if dest_type == 'haldclut':
        clut.write_haldclut(dest)
    elif dest_type == '3dl':
        clut.write_3dl(dest)
    elif dest_type == 'cube':
        clut.write_cube(dest)
    else:
        raise ValueError('Not an appropriate Color LUT file type: {}'.format(dest_type))


if __name__ == '__main__':
    cli()
