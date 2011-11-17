
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
GeoTiffs that have been optimized for rendering with [TileMill][].

It requires the commandline utilities `ogr2ogr` and `shapeindex` to be 
available.

[TileMill]: http://tilemill.com

## Goals (TODO):

- don't care about input filetypes
- default output format is Shapefiles for vector and GeoTiff for raster
- optionally output vector sources to SQLite
- clip any data that falls outside the TMS zoom-level 0 tile
- reproject all sources to The One And Only Google Mercator
- index output files in a way that speeds up Mapnik rendering
- if many input files are specified, process them all individually by default
- optionally merge many input files to a single output file

## Examples for a theoretical future working version

The simplest case: reproject & shapeindex a single file. Output file would be
named `someshape_millready.shp`.

    millprep.py someshape.shp

Similar to above, but with a custom output filename:

    millprep.py someshape.shp -o custom_outfile_name.shp

Bulk process a number of files at once. Output filenames will be like
`<original_name>_millready.shp`

    millprep.py *.shp

Bulk process a number of files at once and put the results in a specified 
directory. Files keep their original name and *not* have `_millready` appended.

    millprep.py *.shp -d ./processed/

Merge a number of input files into a single output file.

    millprep.py --merge county_*.shp -o all_counties.shp

Convert a number of shapefiles to individual SQLite files.

    millprep.py --sqlite *.shp

