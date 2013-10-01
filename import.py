#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ijson
import json
from shapely.geometry import shape
from shapely.wkt import dumps
import psycopg2
import sys
import os
import re

"""
Simple tool to load (large) GeoJSON files to a PostGIS db without eating up all my memory
(yes ogr, I'm looking at you!)
"""

def create_table_sql(tablename, fields, geom_type, geom_srid):
    """
    Create a SQL statement for creating a table. Based on a geoJSON
    representation. For simplicity all fields are declared VARCHAR 255
    (not good, I know, patches welcome)
    """
    cols = []
    for field in fields:
        cols.append("%s VARCHAR(255)" % field)

    statement = """CREATE TABLE %s (
                id SERIAL,
                %s,
                geom GEOMETRY(%s, %s),
                PRIMARY KEY (id)
                )
                """ %(tablename, ",\n".join(cols), geom_type, geom_srid)
    return statement

def get_geom(feature):
    """
    Get the shapely geom from a geoJSON geometry
    """
    return shape(feature["geometry"])

def create_table(connection, feature, tablename, srid):
    """
    Actually create a table
    """
    geom =  get_geom(feature)
    sql = create_table_sql(
        tablename,
        [field for field in feature["properties"].keys()],
        geom.type,
        srid
    )
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS %s" % tablename)
    cursor.execute(sql)
    connection.commit()

def insert(cursor, feature, tablename, srid):
    """
    Insert a "feature" as a row in PostGIS
    """
    fields = ", ".join([field for field in feature["properties"].keys()])
    values = ", ".join(["'%s'" % unicode(field) for field in feature["properties"].values()])
    sql = """
    INSERT INTO %s (%s, geom)
    VALUES (%s, ST_GeomFromText('%s', %s))
    """ % (tablename, fields, values, dumps(get_geom(feature)), srid)
    cursor.execute(sql)


def load_geojson(file, tablename, srid):
    """
    Load (read) a geoJSON file and stuff it into a PostGIS table
    """
    f = open(file)
    features = ijson.items(f, "features.item")
    connection = psycopg2.connect("dbname=n50")
    cursor = connection.cursor()

    counter = 0
    first = True
    for feature in features:
        if first:
            create_table(connection, feature, tablename, srid)
        try:
            insert(cursor, feature, tablename, srid)
        except Exception, e:
            print e
        first = False
        counter += 1
        if counter%1000==0:
            print "commit %s" %counter
            connection.commit()
    connection.commit()

def check_geojson(file):
    """
    Figure out what can't be read from file
    """

    f = open(file)
    features = ijson.items(f, "features.item")

    for feature in features:
        try:
            geom = dumps(get_geom(feature))
        except Exception, e:
            print e, feature

try:
    directory = sys.argv[1]
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.geojson'):
                print "load %s" % file
                name = file.split(".")[0].lower().replace("Å", "aa").replace("å", "aa").replace("ø", "o").replace("æ", "ae")
                load_geojson(root  + file, name, 4326)
    print "DONE!"
except IndexError:
    print "specify path"
