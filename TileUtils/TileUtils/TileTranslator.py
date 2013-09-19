# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

import os.path
import xml.etree.ElementTree

class TileTranslator:
	"""
	Class used for translating tiles from .tmx tilemaps into data based on .ttt translation
	tables
	"""
	def __init__(self):
		self._defaultTilesEnabled = False
		self._defaultTranslations = None
		self._layers = []
		self._pathToTranslationTable = None
		self._pathToTileMap = None
		self._remap = {}
		self._tileSets = None
		self._translationType = None

	def clearRemap(self):
		"""Clear all tileset remaps."""
		self._remap = {}

	def getDefaultTilesEnabled(self):
		"""
		Get boolean value indicating whether default tile translations are used in the
		translation of tiles.
		"""
		return self._defaultTilesEnabled

	def getHeightOfLayerInTiles(self, layerNumber):
		"""Get the height of the specified layer in tiles."""
		if layerNumber < 0:
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is "
								"negative. layerNumber: " + str(layerNumber))		
		
		if layerNumber >= len(self._layers):
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is too "
								"large. layerNumber: " + str(layerNumber))

		return int(self._layers[layerNumber]['height'])

	def getNumberOfLayers(self):
		"""Get the number of layers in the tilemap."""
		return len(self._layers)

	def getRemap(self, tileSetToRemapFrom):
		"""Get the tileset (if any) that the specified tilemap is remaped to."""
		return self._remap.get(tileSetToRemapFrom)

	def getTileMapPath(self):
		"""Get the path to the .tmx file used to load the current tilemap."""
		return self._pathToTileMap

	def getTileTranslation(self, layerNumber, x, y, translationType = None):
		"""
		Get the data from the translation table that is associated with the tile.

		Parameters:
		layerNumber - The layer containing the tile.
		x - The x coordinate of the tile.
		y - The y coordinate of the tile.
		translationType - Overrides the translationType set by setTranslationType()
		"""
		if translationType is None:
			translationType = self.getTranslationType()

		if translationType is None:
			raise RuntimeError("Translation type is not set.")

		if layerNumber < 0:
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is "
								"negative. layerNumber: " + str(layerNumber))		
		
		if layerNumber >= len(self._layers):
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is too "
								"large. layerNumber: " + str(layerNumber))

		if x < 0:
			raise IndexError("x contains an invalid index. x is negative. x: " + str(x))
		
		if x >= self.getWidthOfLayerInTiles(layerNumber):
			raise IndexError("x contains an invalid index. x is too large. x: " + str(x))

		if y < 0:
			raise IndexError("y contains an invalid index. y is negative. y: " + str(y))		
		
		if y >= self.getHeightOfLayerInTiles(layerNumber):
			raise IndexError("y contains an invalid index. x is too large. y: " + str(y))

		translationsForTile = None
		# Find the data for the tile.
		# self._layers[layerNumber] is effectively a sparse 2d array.
		if y in self._layers[layerNumber]['tiles'] and x in self._layers[layerNumber]['tiles'][y]:
			tile = self._layers[layerNumber]['tiles'][y][x]

			tileSet = self.getRemap(tile['setName'])
			if tileSet is None:
				tileSet = tile['setName']

			# Get the translation for the tile.
			if tile['name'] in self._tileSets[tileSet]:
				translationsForTile = self._tileSets[tileSet][tile['name']]
			elif self.getDefaultTilesEnabled() and tile['name'] in self._defaultTranslations:
				translationsForTile = self._defaultTranslations[tile['name']]
			else:
				raise RuntimeError(	"Missing tile translation. Tile name: " + str(tile['name']) +
									" Set name: " + str(tile['setName']) +
									" Remap: " + str(self.getRemap(tile['setName'])) +
									" Default tiles enabled: " + str(self.getDefaultTilesEnabled()))
		else:
			return None

		if translationType in translationsForTile:
			return translationsForTile[translationType]

		raise RuntimeError( "Translation not specified for tile. Tile Translation Type: " +
							str(translationType) +
							" Tile name: " + str(tile['name']) +
							" Set name: " + str(tile['setName']) +
							" Remap: " + str(self.getRemap(tile['setName'])) +
							" Default tiles enabled: " + str(self.getDefaultTilesEnabled()))

	def getTranslationTablePath(self):
		"""Get the path to the .ttt file used to load the current tile translation."""
		return self._pathToTranslationTable

	def getTranslationType(self):
		"""Get the currently set translation type."""
		return self._translationType

	def getWidthOfLayerInTiles(self, layerNumber):
		"""Get the height of the specified layer in tiles."""
		if layerNumber < 0:
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is "
								"negative. layerNumber: " + str(layerNumber))		
		
		if layerNumber >= len(self._layers):
			raise IndexError(	"layerNumber contains an invalid index. layerNumber is too "
								"large. layerNumber: " + str(layerNumber))

		return int(self._layers[layerNumber]['width'])

	def setDefaultTilesEnabled(self, enabled):
		"""Enable/disable the use of default tiles in translations."""
		self._defaultTilesEnabled = enabled

	def setRemap(self, tileSetToRemapFrom, tileSetToRemapTo):
		"""
		Remaps a tileset so that the translations of the any of its tiles are pulled from another
		tilesets portion of the translation table.
		"""
		self._remap[tileSetToRemapFrom] = tileSetToRemapTo

	def setTileMapFromPath(self, pathToTileMap):
		"""
		Load a tilemap to be translated from a .tmx file.

		A path used in this funtion generated in an UNSAFE manner. It uses non-sanitized path data
		from the tilemap.
		"""
		tileMap = xml.etree.ElementTree.parse(pathToTileMap)
		directoryName = os.path.dirname(pathToTileMap)
		tileMapRoot = tileMap.getroot()

		tiles = {}
		layers = []

		for tileSetInfo in tileMapRoot.findall("tileset"):
			# If 'source' is defined it means that the tileset is an external .tsx file.
			if 'source' in tileSetInfo.attrib:

				# This path is generated in an UNSAFE manner. It uses non-sanitized path data from
				# the tilemap.
				pathToCurrentTileSet = os.path.join(directoryName, tileSetInfo.attrib['source'])

				# Find and parse the external .tsx file 
				currentTileSet = xml.etree.ElementTree.parse(pathToCurrentTileSet)
				currentTileSetRoot = currentTileSet.getroot()
				currentTileSetName = currentTileSetRoot.attrib['name']

				if not currentTileSetName:
					raise ValueError("Malformed tileset. Missing name property.")

				# For each tile in the tilemap find its name and which tileset it belongs to.
				for tile in currentTileSet.findall('tile'):
					currentTileProperties = tile.findall('properties/property')
					currentTileGID = None
					currentTileName = None
					for currentProperty in currentTileProperties:
						if currentProperty.attrib.get('name') == 'name':
							currentTileGID = str(	int(tile.attrib['id']) +
													int(tileSetInfo.attrib['firstgid']))
							currentTileName = currentProperty.attrib['value']
							break

					if currentTileName:
						tiles[currentTileGID] = {	"name": currentTileName,
													"setName": currentTileSetName } 
					else:
						raise ValueError("Malformed tile. Missing name property.")

		# Store the tile data in layers.
		for currentLayer in tileMapRoot.findall("layer"):
			newLayer = {
						"width": currentLayer.attrib['width'],
						"height": currentLayer.attrib['height'],
						"tiles": {}
					}

			tileCount = 0
			for currentTileInLayer in currentLayer.findall("data/tile"):
				if 'gid' not in currentTileInLayer.attrib:
					raise ValueError("Malformed tilemap. Missing gid property.")
				
				if currentTileInLayer.attrib['gid'] in tiles:
					row = int(tileCount / int(newLayer["width"]))
					column = int(tileCount % int(newLayer["width"]))
					if int(tileCount / int(newLayer["width"])) not in newLayer["tiles"]:
						newLayer["tiles"][row] = {}

					newLayer["tiles"][row][column] = tiles[currentTileInLayer.attrib['gid']]

				tileCount += 1

			layers.append(newLayer)

		self._layers = layers
		self._pathToTileMap = pathToTileMap

	def setTranslationTableFromPath(self, pathToTranslationTable):
		"""
		Load a translation table from a .ttt file to be used in the translation of the tilemap. 
		"""
		translationTable = xml.etree.ElementTree.parse(pathToTranslationTable)
		defaultTranslations = {}
		tileSets = {}

		translationTableRoot = translationTable.getroot()
		translationTableDefaultTranslations = translationTable.findall("defaulttranslations")

		# Store the default tile translation table data.
		for defaultTranslationSet in translationTableDefaultTranslations:
			currentDefaults = \
				self._extractTileTranslationsFromTileSetTranslation(defaultTranslationSet)

			for tileName in currentDefaults:
				if tileName in defaultTranslations:
					raise ValueError("Malformed defaulttranslations. Duplicate default.")

				defaultTranslations[tileName] = currentDefaults[tileName]

		tileSetTranslations = translationTable.findall("tilesettranslations/tilesettranslation")
 
 		# Store the tile translation table data for each tileset.
		for tileSetTranslation in tileSetTranslations:
			currentSet = \
				self._extractTileTranslationsFromTileSetTranslation(tileSetTranslation)

			if not tileSetTranslation.attrib.get("tilesetname"): 
				raise ValueError("Malformed tilesettranslation. Missing tilesetname attribute.")
			else:
				currentTileSetName = tileSetTranslation.attrib["tilesetname"]
				if not currentTileSetName in tileSets: 
					tileSets[currentTileSetName] = {} 

				for tileName, tile in currentSet.items():
					if tileName in tileSets[currentTileSetName]:
						raise ValueError("Malformed tilesettranslations. Duplicate tile.")

					tileSets[currentTileSetName][tileName] = tile

		self._defaultTranslations = defaultTranslations
		self._tileSets = tileSets
		self._pathToTranslationTable = pathToTranslationTable

	def setTranslationType(self, translationType):
		"""Set the translation type to use when translating files."""
		self._translationType = translationType

	def _extractTileTranslationsFromTileSetTranslation(self, tileSetTranslation):
		# Create a dictionary that stores translation data in the manner
		# of tilsetTranslationData[tilename][translationtype].
		translations = {}
		for tileTranslation in tileSetTranslation.findall("tiletranslation"):
			if tileTranslation.attrib.get("tilename"):
				tileTranslationValues = tileTranslation.find("values")
				values = {}
				for value in tileTranslationValues.findall("*"):
					if value.tag in values:
						raise ValueError(	"Malformed tiletranslation. Duplicate translation "
											"of type: " + str(value.tag))

					values[value.tag] = value.text

				if values == {}:
					raise ValueError("Malformed tiletranslation. Missing translations.")

				if tileTranslation.attrib["tilename"] in translations:
					raise ValueError(	"Malformed defaulttranslations or tilesettranslations. "
										"Duplicate tile. tilename: " +
										str(tileTranslation.attrib["tilename"]))

				translations[tileTranslation.attrib["tilename"]] = values
			else:
				raise ValueError("Malformed tiletranslation. Missing tilename attribute.")

		return translations

