#!/usr/bin/env python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.
"""
Displays the tilenames used in a .tsx file.
"""

import argparse
import csv
import io
import os
import sys

import TileUtils.TileSet



if __name__ == "__main__":
	_EMPTYCSVROW = [None, None, None, None, None] 

	parser = argparse.ArgumentParser(	description = 	"Displays the tilenames used in a .tsx"
														"file.")
	parser.add_argument('TILESET', 	help = ".tsx file.",
								type = str)
	parser.add_argument('--csv', help = "Output in .csv format.",
								action = 'store_true', default = False)
	parser.add_argument('--save', help = "file to save output to.")
	args = parser.parse_args()


	# Chance to give a descriptive error message.
	if not os.path.isfile(args.TILESET):
		print("Problem opening {}. No such file.".format(args.TILESET))
		sys.exit(1)

	tileSet = TileUtils.TileSet.TileSet()

	try:
		tileSet.loadFromXMLFile(args.TILESET)
	except OSError: 
		print("Problem opening {}.".format(args.TILESET))
		sys.exit(1)

	tileSetName = tileSet.getTileSetName()
	tileNames = tileSet.getTileNamesAsList()

	# Sorting the tilenames affects the not only the order in which the tilenames are output but
	# also the order in which the duplicate tilenames are output. 
	tileNames.sort()

	# Calculate the number times each tilename is used. 
	tileNameCount = {}
	for tileName in tileNames:
		if tileName in tileNameCount:
			tileNameCount[tileName] = tileNameCount[tileName] + 1
		else:
			tileNameCount[tileName] = 1

	# Find the tilenames that have been used more than once
	duplicateTiles = []
	for tileName, count in tileNameCount.items():
		if count > 1:
			duplicateTiles.append((tileName, count))

	if args.csv:
		# CSV output
		rowsToBeWrittenToCSV = []

		rowsToBeWrittenToCSV.append([tileSetName])
		for tileName in tileNames:
			rowsToBeWrittenToCSV.append([tileName])

		rowsToBeWrittenToCSV.append(_EMPTYCSVROW)

		rowsToBeWrittenToCSV.append(['DUPLICATES'])
		for duplicateTile in duplicateTiles:
			rowsToBeWrittenToCSV.append(list(duplicateTile))

		with io.StringIO() as stringBuffer:
			writer = csv.writer(stringBuffer, quoting = csv.QUOTE_NONE)
			writer.writerows(rowsToBeWrittenToCSV)

			output = stringBuffer.getvalue()
	else:
		# Regular output
		unconstructedString = []
		unconstructedString.append("{}\n".format(tileSetName))
		for tileName in tileNames:
			unconstructedString.append("{}".format(tileName))

		unconstructedString.append("\nDUPLICATES")
		for duplicateTile in duplicateTiles:
			unconstructedString.append("{} {}".format(*duplicateTile))

		output = "\n".join(unconstructedString)

	if args.save:
		try:
			with open(args.save, "w") as saveFile:	
				saveFile.write(output)
		except (IOError):
			sys.exit("Problem saving file.")
	else:
		print(output)
