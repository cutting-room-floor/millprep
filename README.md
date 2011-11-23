
                  ___    ___    ____                         
     /'\_/`\  __ /\_ \  /\_ \  /\  _`\                       
    /\      \/\_\\//\ \ \//\ \ \ \ \L\ \_ __    __   _____   
    \ \ \__\ \/\ \ \ \ \  \ \ \ \ \ ,__/\`'__\/'__`\/\ '__`\ 
     \ \ \_/\ \ \ \ \_\ \_ \_\ \_\ \ \/\ \ \//\  __/\ \ \L\ \
      \ \_\\ \_\ \_\/\____\/\____\\ \_\ \ \_\\ \____\\ \ ,__/
       \/_/ \/_/\/_/\/____/\/____/ \/_/  \/_/ \/____/ \ \ \/ 
                                                       \ \_\ 
                                                        \/_/ 

**MillPrep** eats random geodata and poops shapefiles, SQLite databases, or 
GeoTiffs that have been optimized for rendering with [TileMill][]. It is being
actively developed and is **mostly untested**.

It requires the commandline utilities `ogr2ogr` and `shapeindex` to be 
available.

[TileMill]: http://tilemill.com

## TileMill optimization means:

- reproject everything to The One And Only Google Mercator
- clip any data that falls outside the TMS zoom-level 0 tile (this is optional)
- index output files appropriately for Mapnik

In addition to these core optimizations, MillPrep also allows you to merge many
input files into a single output file. This is useful for data with a single
data schema that is distributed as many separate files, such as the U.S. 
Census Bureau's [TIGER][] shapefiles which are split up by state.

[TIGER]: http://www.census.gov/geo/www/tiger/

## Future Goals:

- appropriately handle any input that the OGR/GDAL supports (the current extent
  of this is untested)
- related to above: handle raster input/output
- test everything in something other than ideal situations
- possibly: geometry simplification

## Usage

<pre>
usage: millprep.py [-h] [--sqlite] [--noclip] [-d OUTPUT_DIR] [-m MERGED_FILE]
                   INPUT_FILE [INPUT_FILE ...]

Convert geographic datasources to more TileMill-optimized formats.

positional arguments:
  INPUT_FILE            A geographic file to optimize for TileMill

optional arguments:
  -h, --help            show this help message and exit
  --sqlite              Use SQLite as the output file format instead of the
                        default, ESRI Shapefile
  --noclip              By default files will be clipped so they don't expand
                        outside the bounds of the Google Mercator square.
  -d OUTPUT_DIR         Destination directory to output the processed files.
                        If not specified, output files will be kept in the
                        same directory as their respective input files.
  -m MERGED_FILE, --merge MERGED_FILE
                        Merge all input files into this single output file.
</pre>

## Examples

The simplest case: reproject & shapeindex a single file. Output file would be
named `someshape_millready.shp`:

    millprep.py someshape.shp

Bulk process a number of files at once. Output filenames will be like
`<original_name>_millready.shp`:

    millprep.py *.shp

Bulk process a number of files at once and put the results in a specified 
directory:

    millprep.py *.shp -d ./processed/

Merge a number of input files into a single output file.

    millprep.py --merge all_counties.shp county_*.shp

Convert a number of shapefiles to individual SQLite files.

    millprep.py --sqlite *.shp

Merge a number of shapefiles to a single table of an SQLite file.

    millprep.py --sqlite --merge merged_file.sqlite *.shp

