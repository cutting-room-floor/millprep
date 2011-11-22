#!/usr/bin/python2
# vim: set tabwidth=2 shiftwidth=2 softabstop=2:
'''

                  ___    ___    ____                         
     /'\_/`\  __ /\_ \  /\_ \  /\  _`\                       
    /\      \/\_\\//\ \ \//\ \ \ \ \L\ \_ __    __   _____   
    \ \ \__\ \/\ \ \ \ \  \ \ \ \ \ ,__/\`'__\/'__`\/\ '__`\ 
     \ \ \_/\ \ \ \ \_\ \_ \_\ \_\ \ \/\ \ \//\  __/\ \ \L\ \
      \ \_\\ \_\ \_\/\____\/\____\\ \_\ \ \_\\ \____\\ \ ,__/
       \/_/ \/_/\/_/\/____/\/____/ \/_/  \/_/ \/____/ \ \ \/ 
                                                       \ \_\ 
                                                        \/_/ 

MillPrep eats random geodata and poops shapefiles, SQLite databases, or
GeoTiffs that have been optimized for rendering with TileMill. 

See `README.md` for more information.

'''

import sys
import argparse
import subprocess
from os import path

try:
  from osgeo import ogr
except:
  import ogr

gmerc_proj4 = '"+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over"'
gmerc_bounds = "-180.0 -85.05112877980659 180 85.05112877980659"

def EQUAL(a, b):
  ## case-insensitive equality check
  return a.lower() == b.lower()


################################################################################
## REPROJECT

def reproject(src_path, dst_path, output_format='shp', clip=True):
  """
  Reproject a file to Google Mercator. This will also clip the data if any
  part of it falls outside the square extents of the projection unless the
  user has specified otherwise.

  src_path:  the path to the source file

  dst_path:  the path to the destination file

  output_sqlite:  if not, output shapefile

  clip: a boolean indicating whether (True) or not (False) to attempt to clip
  the datasource to the Google Mercator zoom level 0 tile boundary.
  
  """

  ## Set up the command-line options for ogr2ogr
  ogr_cmd = [ 'ogr2ogr' ]
  if (output_format == 'sqlite'):
    ogr_cmd.append('-f "SQLite"')
  else:
    ogr_cmd.append('-f "ESRI Shapefile"')
  ogr_cmd.append('-s_srs EPSG:4326')
  ogr_cmd.append('-t_srs ' + gmerc_proj4)
  if (clip):
    # TODO: Is there much of a performance impact to running this on datasources
    # that don't require it? Run benchmarks and adjust code if necessary.
    ogr_cmd.append('-clipsrc ' + gmerc_bounds)
  ogr_cmd.append('"' + dst_path + '"')
  ogr_cmd.append('"' + src_path + '"')

  # shell=True is potentially unsafe, however the only approach I can get to work
  subprocess.check_call(' '.join(ogr_cmd), shell=True)


################################################################################
## SHAPEFILE INDEXING

def shp_index(src_file):
  """
  Calls the Mapnik `shapeindex` utility to create .index files for any output
  shapefiles.

  """

  subprocess.check_call('shapeindex ' + src_file)

################################################################################
## MAIN

def main():

  # ---- Process command-line arguments ----------------------------------------

  parser = argparse.ArgumentParser(description='''Convert geographic 
    datasources to more TileMill-optimized formats.''')

  parser.add_argument('src_files',
    nargs='+', 
    help="A geographic file to optimize for TileMill")

  parser.add_argument('--sqlite',
    dest='output_format', action='store_const', const='sqlite', default='shp',
    help='''NOT YET IMPLEMENTED. Use SQLite as the output file format instead 
            of the default ESRI Shapefile''')

  parser.add_argument('--noclip',
    dest='clip', action='store_false', default=True,
    help='''By default files will be clipped so they don't expand outside the 
            bounds of the Google Mercator square.''')

  parser.add_argument('-d',
    nargs=1, dest='dst_dir',
    help='''Destination directory to output the processed files. If not
            specified, output files will be kept in the same directory as their 
            respective input files.''')

  parser.add_argument('-m', '--merge',
    dest='output_merged', action='store_true',
    help='NOT YET IMPLEMENTED. Merge all input files into a single output file.')

  args = parser.parse_args()


  # Optimizes files one at a time according to the specified options.
  for src_file in args.src_files:

    # Get the absolute path of the input file
    src_path = path.abspath(src_file)

    # The output filename is based on the input file, with _millready appended
    dst_filename = path.splitext(path.basename(src_file))[0] + \
      '_millready.' + args.output_format

    # Define the the output directory if the user did not specify one
    if not (args.dst_dir):
      dst_dir = path.split(src_path)[0]
    else:
      dst_dir = args.dst_dir[0]
    dst_path = path.join(dst_dir, dst_filename)

    #
    reproject(src_path, dst_path, args.output_format, args.clip)

    # create a Mapnik index for the shapefile
    #shp_index(dst_path)


if __name__ == '__main__':
  if not main():
    sys.exit(1)
  else:
    sys.exit(0)

