GeoJSON2pg
==========

A simple, quick and dirty, hackish script to load a large GeoJSON file into a Postgis db


Usage:
------

python import.py /path/to/dir/with/geojsonfiles

Features:
--------
- does not eat up your memory
- handles errors in GeoJSON by skipping the feature in question
- works in batch mode (several files at once)
- grabs "schema" from geojson file

Drawbacks:
---------
- hardcoded database-name
- stores all attributes as 255 varchar
- depends on shapely, which depends on geos

Tested on
---------
The n50 dataset from Kartverket

Errors, issues, ideas
---------------------
gimmeh code, ktnxbye ;)

