#!/usr/bin/python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

import argparse
import os.path
import sys

import TileUtils.TranslationTable

if __name__ == "__main__":

	parser = argparse.ArgumentParser(	description = 	"Translation Table To CSV.")
	parser.add_argument('TRANSLATIONTABLE', help = 	"translation table that the CSV is created "
													"from.", type = str)
	parser.add_argument('--save', help = "file to save CSV to.")
	args = parser.parse_args()

	if not os.path.isfile(args.TRANSLATIONTABLE):
		print("Problem opening file. File: {}".format(args.TRANSLATIONTABLE))
	sys.exit(1)

	translationTable = TileUtils.TranslationTable.TranslationTable()
	translationTable.loadFromXMLFile(args.TRANSLATIONTABLE)
	output = translationTable.getCSV()

	if args.save:
		try:
			with open(args.save, "w") as saveFile:	
				saveFile.write(output)
		except (IOError):
			sys.exit("Problem saving file.")
	else:
		print(output)