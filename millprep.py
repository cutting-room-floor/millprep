#!/usr/bin/python2
'''

MillPrep
========

It eats random geodata and poops shapefiles, SQLite databases, or GeoTiffs
that have been optimized for rendering with TileMill.

It requires the commandline utilities `ogr2ogr` and `shapeindex` to be 
available.

'''

import argparse
from os import path
from subprocess import call

gmerc_proj4 = '"+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"'
gmerc_bounds = "-180.0 -85.05112877980659 180 85.05112877980659"


def reproject(src_path, dst_path, clip=True):
  """
  Reproject a file to Google Mercator. This will also clip the data if any
  part of it falls outside the square extents of the projection unless the
  user has specified otherwise.

  src_path:  the path to the source file

  dst_path:  the path to the destination file

  clip: a boolean indicating whether (True) or not (False) to attempt to clip
  the datasource to the Google Mercator zoom level 0 tile boundary.
  
  """

  ## Set up the command-line options for ogr2ogr
  ogr_opts = []
  ogr_opts.append('-f "ESRI Shapefile"')
  ogr_opts.append('-s_srs EPSG:4326')
  ogr_opts.append('-t_srs ' + gmerc_proj4)
  if (clip):
    # TODO: Is there much of a performance impact to running this on datasources
    # that don't require it? Run benchmarks and adjust code if necessary.
    ogr_opts.append('-clipsrc ' + gmerc_bounds)
  ogr_opts.append('"' + dst_path + '"')
  ogr_opts.append('"' + src_file + '"')

  print 'ogr2ogr ' + ' '.join(ogr_opts)
  call('ogr2ogr ' + ' '.join(ogr_opts))


def shp_index(src_file):
  """
  Calls the Mapnik `shapeindex` utility to create .index files for any output
  shapefiles.

  """

  call('shapeindex ' + src_file)


def main():

  parser = argparse.ArgumentParser(
    description="Convert geographic datasources to more TileMill-optimized formats")
  parser.add_argument('src_files', nargs='+', 
    help="A geographic file to optimize for TileMill")
  parser.add_argument('--sqlite', dest='output_sqlite', action='store_true',
    help='NOT YET IMPLEMENTED. Use SQLite as the output file format instead of the default ESRI Shapefile')
  parser.add_argument('--noclip', dest='clip', action='store_false', default=True,
    help="By default files will be clipped so they don't expand outside the bounds of the Google Mercator square.")
  parser.add_argument('-d', nargs=1, dest='dst_dir',
    help='Destination directory to output the processed files. If not specified, output files will be kept in the same directory as their respective input files.')
  parser.add_argument('-m', '--merge', dest='output_merged', action='store_true',
    help='NOT YET IMPLEMENTED. Merge all input files into a single output file.')

  args = parser.parse_args()

  for src_file in args.src_files:
    """
    Optimizes files one at a time according to the specified options.

    """

    # Get the absolute path of the input file
    src_path = path.abspath(src_file)

    # The output filename is based on the input file, with _millready appended
    dst_filename = path.splitext(path.basename(src_file))[0] + \
      '_millready' + path.splitext(path.basename(src_file))[1]

    # Define the the output directory if the user did not specify one
    if not (args.dst_dir):
      dst_dir = path.split(src_path)[0]

    dst_path = path.join(dst_dir, dst_filename)

    reproject(src_path, dst_path, args.clip)

    # create a Mapnik index for the shapefile
    shp_index(dst_path)


if __name__ == "__main__":
  main()

