#!/usr/bin/python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

import argparse
import os.path
import sys

import TileUtils.TranslationTable

if __name__ == "__main__":
	parser = argparse.ArgumentParser(	description = 	"CSV To Translation Table.")
	parser.add_argument(	'CSV', help = 	"the CSV that the translation table is created from.",
							type = str)
	parser.add_argument('--save', help = "file to save XML to.")
	args = parser.parse_args()

	if not os.path.isfile(args.CSV):
		print("Problem opening file. File: {}".format(args.CSV))
		sys.exit(1)

	translationTable = TileUtils.TranslationTable.TranslationTable()
	translationTable.loadFromCSVFile(args.CSV)
	output = translationTable.getXML()


	if args.save:
		try:
			with open(args.save, "w") as saveFile:	
				saveFile.write(output)
		except (IOError):
			sys.exit("Problem saving file.")
	else:
		print(output)