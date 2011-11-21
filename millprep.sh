#!/bin/bash
set -e -u

## MILLPREP

if [ "$1" = "--merge" ]; then
  
  shift
  # if merging, output filename must be specified by the user
  dst="$1"
  # since we'll be reprojecting afterwards, do the merging in a temp file
  tmp=$(mktemp).shp
  shift
  for src in "$@"; do 
    if test -e "$tmp"; then
      echo -n "Merging $src ... "
      ogr2ogr -f "ESRI Shapefile" -update -append -progress \
        "$tmp" "$src" -nln `basename $tmp .shp` \
        || exit 1
    else 
      echo -n "Creating new file from $src ... "
      ogr2ogr -f "ESRI Shapefile" -progress "$tmp" "$src" \
        || exit 1
    fi
  done
  # reproject the temporary file to Google Mercator
  ogr2ogr -f "ESRI Shapefile" \
    -t_srs "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" \
    -clipsrc -180.0 -85.05112877980659 180 85.05112877980659 \
    -progress \
    $dst $tmp

else

  for src in "$@"; do
    # output filename based on the input, with '_millready' appended before the extension
    dst="$(dirname $src)"/"$(echo $src | sed 's/\(.*\)\..*/\1/')_millready.$(echo $src | sed 's/.*\.//')"
    echo $dst
    # reproject to Google Mercator
    ogr2ogr -f "ESRI Shapefile" \
      -t_srs "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +wktext +no_defs +over" \
      -clipsrc -180.0 -85.05112877980659 180 85.05112877980659 \
      $dst $src
    # index the shapefile
    shapeindex $dst
  done

fi
