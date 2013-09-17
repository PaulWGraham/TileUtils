#!/usr/bin/python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

import argparse
import os
import sys

import TileUtils.Plugin
import TileUtils.TranslationTable

class ConflictingTileTranslationError(Exception):
	def __init__(self, message, conflictingTranslations):
		super().__init__(message)
		self.conflictingTranslations = conflictingTranslations

class DirectoryToTranslationTableConverter(TileUtils.Plugin.Plugable):
	def __init__(self):
		super().__init__()
		self._environments = []
		self._translationTable = TileUtils.TranslationTable.TranslationTable()

	def createTranslationTableFromDirectory(	self, directory, relativeDirectory, environment,
												ignoreDefaults, tableName, tableVersion):

		translationTableRootDir, tileSetNames, miscFiles = next(os.walk(directory))
		tileSetNames[:] = self._filterOutDotNames(tileSetNames)

		conflictingTileTranslationFound = False
		tileSetsWithConflictingTranslations = {}
		if 'DEFAULTS' in tileSetNames:
			if not ignoreDefaults:
				tileSetDirectory = os.path.join(translationTableRootDir, 'DEFAULTS')
				tileTranslations, conflictingTileTranslations = \
					self._createTileTranslationsFromSetDirectory(	tileSetDirectory, 
																	relativeDirectory, environment)
				if conflictingTileTranslations:
					conflictingTileTranslationFound = True
					tileSetsWithConflictingTranslations['DEFAULTS'] = conflictingTileTranslations
				
				if not conflictingTileTranslationFound:
					for tileTranslation in tileTranslations:
						self._translationTable.addDefaultTileTranslationValue(*tileTranslation[:3])

			tileSetNames.remove('DEFAULTS')

		for tileSetName in tileSetNames:
			tileSetDirectory = os.path.join(translationTableRootDir, tileSetName)
			tileTranslations, conflictingTileTranslations = \
				self._createTileTranslationsFromSetDirectory(	tileSetDirectory, relativeDirectory,
																environment)
			if conflictingTileTranslations:
				conflictingTileTranslationFound = True
				tileSetsWithConflictingTranslations[tileSetName] = conflictingTileTranslations
			
			if not conflictingTileTranslationFound:
				for tileTranslation in tileTranslations:
					self._translationTable.addTileTranslationValue(	tileSetName,
																	*tileTranslation[:3])

		if conflictingTileTranslationFound:
			raise ConflictingTileTranslationError(	"Conflicting tile translations.",
													tileSetsWithConflictingTranslations)

		self._translationTable.setTranslationTableName(tableName)
		self._translationTable.setTranslationTableVersion(tableVersion)


	def getTranslationTableAsXML(self):
		return self._translationTable.getXML()

	def getTranslationTableAsCSV(self):
		return self._translationTable.getCSV()

	def getEnvironments(self):
		return self._environments

	def registerPlugin(self, newPlugin, path):
		if super().registerPlugin(newPlugin, path):
			if path[0] not in self._environments:
				self._environments.append(path[0])
	
	def _createTileTranslationsFromSetDirectory(	self, tileSetDirectory, relativeDirectory,
													environment):
		tileSetDirectoryRootDirectory, translationTypes, miscFiles = next(os.walk(tileSetDirectory))
		
		translationTypes[:] = self._filterOutDotNames(translationTypes)

		tileTranslations = []
		conflictingTileTranslations = []
		for translationType in translationTypes:
			translationTypeDirectory = 	os.path.join(tileSetDirectoryRootDirectory, translationType)
			
			currentTileTranslations = self._createTileTranslationsFromTranslationTypeDirectory(
																		translationTypeDirectory,
																		relativeDirectory,
																		environment,
																		translationType)

			tileTranslations.extend(currentTileTranslations)

			conflictingTileTranslations.extend(
				self._findConflictingTileTranslations(currentTileTranslations))

		return tileTranslations, conflictingTileTranslations



	def _createTileTranslationsFromTranslationTypeDirectory(	self, translationTypeDirectory,
																relativeDirectory,
																environment,
																translationType):
		
		if self.queryPlugin([environment, translationType]):
			tileCreator = self.getPlugin([environment, translationType])[0]
		elif self.queryPlugin([environment]):
			tileCreator = self.getPlugin([environment])[0]
		else:
			tileCreator = self.getPlugin(['default'])[0]

		tileTranslations = []

		for currentDirRoot, dirNames, unfilteredFileNames in os.walk(translationTypeDirectory):
			dirNames[:] = self._filterOutDotNames(dirNames)
			fileNames = self._filterOutDotNames(unfilteredFileNames)
			for fileName in fileNames:
				filePath = os.path.join(currentDirRoot, fileName)
				tileName, translationValue = tileCreator.createTranslation(	filePath,
																			relativeDirectory,
																			environment,
																			translationType)
				if tileName is not None:
					tileTranslations.append((tileName, translationType, translationValue, filePath))

		return tileTranslations


	def _filterOutDotNames(self, names):
		filteredNames = [name for name in names if not name.startswith('.')]

		return filteredNames

	def _findConflictingTileTranslations(self, tileTranslations):
		conflictingTranslations = {}

		conflictingTranslationFound = False
		for tileTranslation in tileTranslations:
			if conflictingTranslations.get(tileTranslation[0]) is None:
				conflictingTranslations[tileTranslation[0]] = [tileTranslation]
			else:
				conflictingTranslations[tileTranslation[0]].append(tileTranslation)
				conflictingTranslationFound = True

		conflictingTranslationsList = []
		if conflictingTranslationFound:
			for tileName, conflictingTiles in conflictingTranslations.items():
				for conflictingTile in conflictingTiles:
					conflictingTranslationsList.append(conflictingTile)

		return conflictingTranslationsList


class TileTranslationCreator(TileUtils.Plugin.StandardPlugin):
	def createTranslation(self, filePath, relativeDirectory, environment, translationType):
		raise NotImplementedError("This method is required.")		

class DefaultTileTranslationCreator(TileTranslationCreator):
	def createTranslation(self, filePath, relativeDirectory, environment, translationType):
		tileName = os.path.basename(filePath).partition('.')[0]
		translationValue = os.path.relpath(filePath, relativeDirectory)

		return tileName, translationValue

	def name(self):
		return "DefaultTileTranslationCreator"

class BlenderObjectFromSceneTileTranlationCreator(TileTranslationCreator):
	def createTranslation(self, filePath, relativeDirectory, environment, translationType):

		fileExtension = os.path.splitext(filePath)[1]
		if fileExtension != ".blend":
			return None, None

		tileName = os.path.basename(filePath).partition('.')[0]
		translationValue = 	os.path.relpath(filePath, relativeDirectory) + \
							"/Object/{}".format(tileName)

		return tileName, translationValue

	def name(self):
		return "BlenderObjectFromSceneTileTranlationCreator"

if __name__ == "__main__":
	directoryConverter = DirectoryToTranslationTableConverter()
	directoryConverter.registerPlugin(DefaultTileTranslationCreator(),["default"])
	directoryConverter.registerPlugin(DefaultTileTranslationCreator(),["blender"])	
	directoryConverter.registerPlugin(	BlenderObjectFromSceneTileTranlationCreator(),
										["blender", "blenderObjectFromScene"])


	parser = argparse.ArgumentParser(	description = 	"DIRectory To Translation Table. Creates a "
														"new translation table based on the "
														"contents of a directory.",
										epilog = 	"With DIR considered as the root, the first "
													"three levels of the directory structure "
													"represent parts of the translation table: "
													"The name of DIR represents the name of " 
													"the translation table; Each directory under "
													"DIR represents the name of a tileset with the "
													"directory DEFAULTS representing the "
													"default tile translations; Each directly "
													"directory under a tileset directory represents"
													"a translation type. The subdirectories of the "
													"translation type directories are recursively "
													"searched and for each non-directory file "
													"found the name of that file before the first "
													"period '.' is considered the name of a tile. "
													"A translation value is created in the " 
													"translation table for that tile based on the "
													"file found. The translation value created "
													"depends on the current translation type and "
													"the type of the file.")
	parser.add_argument('DIR', 	help = "directory that the translation table is created from.",
								type = str)
	parser.add_argument('--csv', help = "Output translation table in .csv format instead of .ttt",
								action = 'store_true', default = False)
	parser.add_argument('--env', help = 	"the environment the translation table is targeted " 
											"at. The environment affects how the translation "
											"values are created.",
						choices = directoryConverter.getEnvironments(), type = str,
						default = "default")
	parser.add_argument('--errors', help = 	"show detailed error messages.", action = 'store_true',
						default = False)
	parser.add_argument('--nodefaults', help = 	"don't create default translations for tiles. "
												"Ignore the DEFAULTS tileset directory.",
						action = 'store_true', default = False)
	parser.add_argument('--save', help = "file to save generated translated table to.")
	args = parser.parse_args()

	if not os.path.isdir(args.DIR):
		print("Problem opening directory. Directory: {}".format(args.DIR))
		sys.exit(1)

	if args.save:
		relativeDirectory = os.path.dirname(args.save)
	else:
		relativeDirectory = args.DIR

	tableName = os.path.basename(os.path.normpath(args.DIR))
	try:
		directoryConverter.createTranslationTableFromDirectory( args.DIR, relativeDirectory,
																args.env, args.nodefaults,
																tableName, "0.1")
	except ConflictingTileTranslationError as error:
		print(	"Problem creating translation table.")

		if args.errors:
			print("The following conflicting tile translations were found:")

			for tileSet, conflicts in error.conflictingTranslations.items():
				print("Tile set: {}".format(tileSet))
				for tile in conflicts:
					print("Tile name: {}, Translation Type: {}, File name: {}".format(	tile[0],
																						tile[1],
																						tile[3]))
		sys.exit(1)

	if args.csv:
		output = directoryConverter.getTranslationTableAsCSV()
	else:
		output = directoryConverter.getTranslationTableAsXML()


	if args.save:
		try:
			with open(args.save, "w") as saveFile:	
				saveFile.write(output)
		except (IOError):
			sys.exit("Problem saving file.")
	else:
		print(output)