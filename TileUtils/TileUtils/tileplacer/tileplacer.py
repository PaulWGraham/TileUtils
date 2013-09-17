#!/usr/bin/env python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

"""
Creates a new tilemap based on a transformation of a .tmx tilemap.
"""

# Available modules vary by running environment.
try:
	import bpy
except ImportError:
	pass

try:
	import maya.standalone
	import maya.cmds
except ImportError:
	pass

import TileUtils.Plugin
import TileUtils.TileTranslator

import argparse
import os
import os.path
import re
import sys

class TilePlacementError(Exception):
	"""Exception used to indicate a problem occurred when a tile was placed."""
	pass

class TileTranslationError(Exception):
	"""Exception used to indicate a problem occurred during when a tile was translated."""
	pass

class UnsupportedEnvironmentTypeError(Exception):
	"""Exception used to indicate an attempt to use an unsupported environment."""
	pass

class UnsupportedTranslationTypeError(Exception):
	"""Exception used to indicate an attempt to use an unsupported translation type."""
	pass


class EnvironmentSetter(TileUtils.Plugin.StandardPlugin):
	"""Base class for all environment setters"""
	def setup(self):
		# raises RuntimeError on error.
		pass

	def save(self, filename, token):
		# raises IOError or ValueError on error.
		pass

	def teardown(self):
		# raises RuntimeError on error.
		pass

class BlenderEnvironment(EnvironmentSetter):
	"""Environment setter for blender environment."""
	def name(self):
		return "BlenderEnvironment"

	def setup(self):
		if 'bpy' not in sys.modules:
			raise RuntimeError("Problem setting up environment. bpy module not imported.")

		bpy.ops.object.select_all(action = 'SELECT')
		bpy.ops.object.delete()

	def save(self, filename, token):
		bpy.ops.wm.save_as_mainfile(filepath = filename)

class MayaEnvironment(EnvironmentSetter):
	"""Environment setter for maya environment."""
	def name(self):
		return "MayaEnvironment"

	def setup(self):
		# Check if all of the needed Maya specific modules are imported.
		if 'maya.standalone' not in sys.modules: 
			raise RuntimeError(	"Problem setting up environment. maya.standalone module "
								"not imported.")
		
		if 'maya.cmds' not in sys.modules:
			raise RuntimeError("Problem setting up environment. maya.cmds module not imported.")

		# Initialize the Maya environment.
		maya.standalone.initialize(name = 'python')

		# Load any needed plugins.
		pass

	def save(self, filename, token):
		# Save open Maya scene to filename.
		maya.cmds.file(filename, save = True)

class TerminalEnvironment(EnvironmentSetter):
	"""Environment setter for terminal environment."""
	def name(self):
		return "TerminalEnvironment"

	def save(self, filename, token):
		with open(filename, "w") as outputTextFile:
			outputTextFile.write(token)

class Placer(TileUtils.Plugin.StandardPlugin):
	"""Base class for all tile placers."""
	def getSteps(self):
		pass

	def getUseLink(self):
		pass

	def getWorkingDirectory(self):
		pass

	def placeData(self, layerNumber, x, y, tileData):
		# raise ValueError or IndexError on error.
		pass

	def placeTile(self, layerNumber, x, y, tileData):
		# raise ValueError or IndexError on error.
		pass

	def setSteps(self, x, y, z):
		pass

	def setup(self, setupToken):
		# raises RuntimeError on error.
		pass

	def setUseLink(self, boolean):
		pass

	def setWorkingDirectory(self, string):
		pass

	def teardown(self):
		# raises RuntimeError on error.
		# returns token
		pass

class StandardPlacer(Placer):
	"""Generic placer class."""
	def __init__(self):
		self._useLink = False
		self._stepX = None
		self._stepY = None
		self._stepZ = None
		self._workingDirectory = None

	def getUseLink(self):
		return self._useLink

	def getWorkingDirectory(self):
		return self._workingDirectory

	def getSteps(self):
		return (self._stepX, self._stepY, self._stepZ)

	def setSteps(self, x, y, z):
		self._stepX = x
		self._stepY = y
		self._stepZ = z

	def setUseLink(self, useLink):
		self._useLink = useLink

	def setWorkingDirectory(self, path):
		self._workingDirectory = path

	def teardown(self):
		return None

class BlenderObjectFromScenePlacer(StandardPlacer):
	"""Placer for BlenderObjectFromScene translation data."""
	def __init__(self):
		super().__init__()
		self._layerSelectionMask = {}
		self._BLENDERLAYERMAX = 20

	def name(self):
		return "BlenderObjectFromScenePlacer"
		
	def placeTile(self, layerNumber, x, y, tileData):		
		# Construct path for file specified in translation data relative to working directory.
		blenderPath = os.path.join(self.getWorkingDirectory(), tileData)
		blenderDirectory, blenderObject = os.path.split(blenderPath)
		blenderDirectory = blenderDirectory + os.path.sep

		# Copy or link the blender object to the current scene from a .blend file.
		bpy.ops.object.select_all(action = 'DESELECT')
		try:
			result =	bpy.ops.wm.link_append(	filepath = blenderPath, filename = blenderObject, 
												directory = blenderDirectory,
												link = self.getUseLink(), autoselect = True,
												instance_groups = False)
		except RuntimeError:
			raise ValueError(	"Problem with translated data. "
								"layerNumber: {} x: {} y: {}".format(layerNumber, x, y))

		currentObject = bpy.context.selected_objects[0]
		bpy.context.scene.objects.active = currentObject
		bpy.ops.object.proxy_make()

		# Move the new blender object to a layer in the current scene.
		stepX, stepY, stepZ = self.getSteps()
		bpy.context.object.location = [stepX * x, -(stepY * y), stepZ * layerNumber]

		if layerNumber < self._BLENDERLAYERMAX:
			maskNumber = layerNumber
		else:
			maskNumber = self._BLENDERLAYERMAX - 1

		if maskNumber not in self._layerSelectionMask:
			self._layerSelectionMask[maskNumber] = \
									tuple(x == maskNumber for x in range(self._BLENDERLAYERMAX))

		bpy.ops.object.move_to_layer(layers = self._layerSelectionMask[layerNumber])

	def teardown(self):
		# Make the blender layers that have blender objects in them visible.
		for layerNumber in range(self._BLENDERLAYERMAX):
			bpy.context.scene.layers[layerNumber] = layerNumber in self._layerSelectionMask

		return None

class MayaScenePlacer(StandardPlacer):
	"""Placer for Maya translation data. Unlikely to work."""
	def name(self):
		return "MayaScenePlacer"

	def placeTile(self, layerNumber, x, y, tileData):		
		# Construct path for file specified in translation data relative to working directory.
		mayaScenePath = os.path.join(self.getWorkingDirectory(), tileData)

		# Place the scene specified in mayaScenePath inside of the current scene by importing it or
		# by creating reference. The objects from the imported/referenced scene are stored in a
		# newly created Maya namespace called mayaObjectNamespace.
		if self.getUseLink():
			# Create a reference to the specified scene place it in the current scene.
			maya.cmds.file(	mayaScenePath, reference = True,
							namespace = 'mayaObjectNamespace')
		else:
			# Import the specified scene into the current one.
			maya.cmds.file(mayaScenePath, i = True, namespace = 'mayaObjectNamespace')

		# Check for any errors the occurred in opening the file. If any are found raise ValueError. 
		if maya.cmds.file(mayaScenePath, errorStatus = True):
			raise ValueError(	"Problem with translated data. "
								"layerNumber: {} x: {} y: {}".format(layerNumber, x, y))

		# Get a list of the Maya objects stored in the Maya namespace mayaObjectNamespace.
		mayaObjects = maya.cmds.ls('mayaObjectNamespace:*')

		stepX, stepY, stepZ = self.getSteps()

		# Move the objects from the imported/referenced scene to a location in the current scene. 
		maya.cmds.move(	float(stepX * x), float(stepY * y), float(stepZ * layerNumber),
						*mayaObjects, absolute = True)

		# Merge the mayaObjectNamespace with its parent namespace then remove the
		# mayaObjectNamespace namespace.
		maya.cmds.namespace(	removeNamespace = 'mayaObjectNamespace',
								mergeNamespaceWithParent = True)

class TerminalPlacer(StandardPlacer):
	"""Generic terminal placer."""
	def __init__(self):
		super().__init__()
		self._newtiles = []

	def name(self):
		return "TerminalPlacer"

	def placeTile(self, layerNumber, x, y, tileData):
		newtile = "layerNumber: {} x: {} y: {} data: {}".format(layerNumber, x, y, tileData)
		self._newtiles.append(newtile)
		print(newtile)

	def teardown(self):
		return "\n".join(self._newtiles)

class TilePlacer(TileUtils.Plugin.Plugable):
	"""Places tiles using plugins."""
	def __init__(self):
		super().__init__()
		self._environments = []

	def getEnvironments(self):
		return self._environments

	def placeTiles(	self, tileMap, translationTable, environmentType, translationType, useDefaults,
					useLink, workingDirectory, stepX, stepY, stepZ, saveFile = None, 
					remapFrom = None, remapTo = None):

		if self.queryPlugin([environmentType]):
			environment = self.getPlugin([environmentType])[0]
		else:
			raise UnsupportedEnvironmentTypeError(	"Unsupported environment. "
													"Environment: {}".format(environmentType))

		if self.queryPlugin([environmentType, translationType]):
			placer = self.getPlugin([environmentType, translationType])[0]
		elif self.queryPlugin([environmentType, "DEFAULT"]):
			placer = self.getPlugin([environmentType, "DEFAULT"])[0]
		else:
			raise UnsupportedTranslationTypeError(	"Unsupported translation type for environment. "
													"Environment: {} TranslationType: {}".format(
													environmentType, translationType))

		environmentSetup = environment.setup()
		placer.setup(environmentSetup)
		placer.setSteps(stepX, stepY, stepZ)
		placer.setUseLink(useLink)
		placer.setWorkingDirectory(workingDirectory)

		translator = TileUtils.TileTranslator.TileTranslator()
		translator.setDefaultTilesEnabled(useDefaults)
		translator.setTranslationType(translationType)

		if remapFrom is not None and remapTo is not None:
			translator.setRemap(remapFrom, remapTo)

		try:
			translator.setTileMapFromPath(tileMap)
		except ValueError:
			raise ValueError("Problem using tilemap: " + str(tileMap))

		try:
			translator.setTranslationTableFromPath(translationTable)
		except ValueError:
			raise ValueError("Problem using translation table: " + str(translationTable))

		# Create new tile map.
		for currentLayer in range(translator.getNumberOfLayers()):
			for currentY in range(translator.getHeightOfLayerInTiles(currentLayer)):
				for currentX in range(translator.getWidthOfLayerInTiles(currentLayer)):
					try:
						translation = translator.getTileTranslation(	currentLayer, currentX,
																		currentY)
					except(IndexError, RuntimeError):
						raise TileTranslationError(
									"Problem translating tile. layer: "
									"{}, x: {}, y: {}".format(	currentLayer, currentX, currentY))

					if translation is not None:
						try:
							placer.placeTile(currentLayer, currentX, currentY, translation)
							placer.placeData(currentLayer, currentX, currentY, translation)				
						except(IndexError, ValueError):
							raise TilePlacementError(
										"Problem placing tile. layer: "
										"{}, x: {}, y: {}".format(currentLayer, currentX, currentY))
		
		teardownToken = placer.teardown()

		if saveFile is not None:
			environment.save(args.save, teardownToken)

		environment.teardown

	def registerPlugin(self, newPlugin, path):
		if super().registerPlugin(newPlugin, path):
			if path[0] not in self._environments:
				self._environments.append(path[0])


if __name__ == "__main__":
	tilePlacer = TilePlacer()
	tilePlacer.registerPlugin(BlenderEnvironment(),["blender"])
	tilePlacer.registerPlugin(MayaEnvironment(),["maya"])
	tilePlacer.registerPlugin(TerminalEnvironment(),["terminal"])


	tilePlacer.registerPlugin(BlenderObjectFromScenePlacer(),["blender", "blenderObjectFromScene"])
	tilePlacer.registerPlugin(MayaScenePlacer(),["maya", "mayaScene"])
	tilePlacer.registerPlugin(TerminalPlacer(),["terminal","DEFAULT"] )

	parser = argparse.ArgumentParser(	description = 	"Creates a new tilemap based on a "
														"transformation of a .tmx tilemap.", 
										epilog = 	"To run in blender set the environment "
													"variable TILEPLACER_ARGS to a string " 
													"containing the command line arguments. Then "
													"call blender with the script from the command "
													"line e.g. "
													"export TILEPLACER_ARGS=\"a.tmx y.ttt test "
													"--env blender\"; blender -P tileplacer.py;"
													"unset TILEPLACER_ARGS")
	parser.add_argument('tilemap', help = "location of .tmx tilemap.", type = str)
	parser.add_argument('translationtable', help = "location of .ttt translation table.",
						 type = str)
	parser.add_argument('translationtype', help = "type of translation to use.", type = str)
	parser.add_argument('--env', help = "the environment the script is running in.",
						default = "terminal", type = str, choices = tilePlacer.getEnvironments())
	parser.add_argument('--link', help =	"link translations into new tilemap instead of copying,"
											" if possible.", action = 'store_true', default = False)
	parser.add_argument('--nodefaults', help = "don't use default translations for tiles.", 
						action = 'store_true', default = False)
	parser.add_argument('--remap', help = "remap tileset translation.", nargs = 2,
						default = [None, None], type = str)
	parser.add_argument('--save', help = "file to save generated tilemap to.")
	parser.add_argument('--steps', help = "values that affect placement of generated tiles.",
						nargs = 3, default = [1, 1, 1], type = int)

	# Parse command line arguments. If the environment variable TILEPLACER_ARGS is set its
	# contents are used as the source of arguments instead of sys.argv.
	if 'TILEPLACER_ARGS' in os.environ:
		# Split argument string in such a way that allows spaces in quoted paths.
		commandLineSplitter = re.compile("\".*?\"|'.*?'|\S+")
		arguments = re.findall(commandLineSplitter,os.environ['TILEPLACER_ARGS'])
		arguments = [argument.strip("\'").strip("\"") for argument in arguments]
		args = parser.parse_args(arguments)
	else:
		args = parser.parse_args()

	try:
		tilePlacer.placeTiles(	args.tilemap, args.translationtable, args.env, args.translationtype,
								not args.nodefaults, args.link,
								os.path.dirname(args.translationtable), *args.steps, 
								saveFile = args.save, remapFrom = args.remap[0],
								remapTo = args.remap[1])
	except (TilePlacementError, TileTranslationError, UnsupportedEnvironmentTypeError,
			UnsupportedTranslationTypeError, IndexError, RuntimeError, ValueError,
			FileNotFoundError) as e:
		print(e)
		sys.exit(1)