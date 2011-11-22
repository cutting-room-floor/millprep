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


################################################################################
# REPROJECT VECTOR DATASOURCES
#
def vector_reproject(src_file, dst_file, output_format='shp', clip=True):

  ## Set up the command-line options for ogr2ogr
  ogr_cmd = [ 'ogr2ogr' ]
  if (output_format == 'sqlite'):
    ogr_cmd.append('-f "SQLite"')
  else:
    ogr_cmd.append('-f "ESRI Shapefile"')
  ogr_cmd.append('-s_srs EPSG:4326')
  ogr_cmd.append('-t_srs ' + gmerc_proj4)
  if (clip):
    ogr_cmd.append('-clipsrc ' + gmerc_bounds)
  ogr_cmd.append('"' + dst_file + '"')
  ogr_cmd.append('"' + src_file + '"')

  # shell=True is potentially unsafe, but is the only approach I can get to work
  subprocess.call(' '.join(ogr_cmd), shell=True)

  return True


################################################################################
# PROCESS VECTORS INDIVIDUALLY
#
def vector_process(src_files, dst_dir, output_format='shp', clip=True):
  
  for src_file in src_files:

    # process the file in its current directory if no output directory was 
    # specified with -d
    if not (dst_dir):
      dst_dir = path.split(src_file)[0]

    # The output filename is based on the input file, with _millready appended
    dst_filename = path.splitext(path.basename(src_file))[0] + \
      '_millready.' + output_format
    dst_file = path.join(dst_dir, dst_filename)

    # Do the reprojection
    vector_reproject(src_file, dst_file, output_format, clip)

    # create a Mapnik index for the shapefile, if we made a shapefile
    if (output_format == 'shp'):
      subprocess.call(['shapeindex', dst_file])

  return True


################################################################################
# MERGE VECTORS INTO A SINGLE FILE
#
def vector_merge(src_files, dst_merged, output_format='shp', clip=True):
  # TODO
  return True


################################################################################
# MAIN

def main():

  # ---- Process command-line arguments ----------------------------------------
  #
  parser = argparse.ArgumentParser(description='''Convert geographic 
    datasources to more TileMill-optimized formats.''')

  parser.add_argument('src_files',
    nargs='+', metavar='INPUT_FILE',
    help='''A geographic file to optimize for TileMill''')

  parser.add_argument('--sqlite',
    dest='output_format', action='store_const', const='sqlite', default='shp',
    help='''Use SQLite as the output file format instead of the default,
            ESRI Shapefile''')

  parser.add_argument('--noclip',
    dest='clip', action='store_false', default=True,
    help='''By default files will be clipped so they don't expand outside the 
            bounds of the Google Mercator square.''')

  parser.add_argument('-d',
    nargs=1, dest='dst_dir', metavar='OUTPUT_DIR',
    help='''Destination directory to output the processed files. If not
            specified, output files will be kept in the same directory as their 
            respective input files.''')

  parser.add_argument('-m', '--merge',
    nargs=1, dest='dst_merged', metavar='MERGED_FILE',
    help='''Merge all input files into this single output file.''')

  args = parser.parse_args()

  # ---- send files to be merged -----------------------------------------------
  #
  if (args.dst_merged):
    if (args.dst_dir):
      print("WARNING: --merge overrides -d. Output directory ignored.")
    vector_merge(args.src_files, args.dst_merged, args.output_format, args.clip)

  # ---- send files to be processed individually -------------------------------
  #
  else:
    if (args.dst_dir):
      dst_dir = args.dst_dir[0]
    else:
      dst_dir = None
    vector_process(args.src_files, dst_dir, args.output_format, args.clip)


################################################################################

if __name__ == '__main__':
  if not main():
    sys.exit(1)
  else:
    sys.exit(0)

