#!/usr/bin/python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

from distutils.core import setup

description = 	(	"TileUtils is an experimental proof of concept that explores the idea of "
					"translating individual tiles in a tilemap created with Tiled "
					"(http://www.mapeditor.org) into abstract data using a translation table.")

setup(	name = 'TileUtils',
		version = '0.0.3',
		packages = ['TileUtils'],
		scripts = [	'TileUtils/createtmrc/createtmrc.py', 'TileUtils/csvttt/csvttt.py',
					'TileUtils/dirttt/dirttt.py', 'TileUtils/ertileplacer/ertileplacer.py',
					'TileUtils/tilenames/tilenames.py', 'TileUtils/tileplacer/tileplacer.py',
					'TileUtils/tttcsv/tttcsv.py' ],
		author = 'Paul Graham',
		license = 'MIT',
		description  = description,
		long_description = description
		)