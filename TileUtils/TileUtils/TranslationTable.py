# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

import csv
import io
import xml.etree.ElementTree

class TranslationTable():
	def __init__(self, translationTableName = "default", translationTableVersion = "0.1"):
		self._EMPTYCSVROW = [None, None, None, None, None] 

		self._reset()
		
		self._root.attrib["name"] = translationTableName
		self._root.attrib["version"] = translationTableVersion


	def addDefaultTile(self, tileName):
		existingTileWithTileName = \
			self._defaultTranslations.find("tiletranslation[@tilename='{}']".format(tileName))

		if existingTileWithTileName is not None:
			raise ValueError(	"Default tile already exists in translation table. "
								"tileName: {}".format(tileName))

		tileTranslationElement = self._createTileTranslationElementWithTileName(tileName)
		self._defaultTranslations.append(tileTranslationElement)

	def addDefaultTileTranslationValue(	self, tileName, translationType, translationValue):
		existingTileTranslation = 	self._defaultTranslations.find("./tiletranslation"
									"[@tilename='{}']/values/{}".format(tileName, translationType))

		if existingTileTranslation is not None:
			raise ValueError(	"Default tile translation for translation type already exists in "
								"translation table. tileName: "
								"{}, translationType: {}".format(tileName,translationType))

		tileTranslationElement = self._defaultTranslations.find("./tiletranslation"
																"[@tilename='{}']".format(tileName))

		if tileTranslationElement is None:
			self.addDefaultTile(tileName)

		translationValues = self._defaultTranslations.find(	"./tiletranslation" +
															"[@tilename" +
															"='{}']/values".format(tileName))

		newTranslation = xml.etree.ElementTree.SubElement(translationValues,translationType)
		newTranslation.text = translationValue

	def addTile(self, tileSetName, tileName):
		existingTileWithTileName = self._tileSetTranslations.find(	
												"./tilesettranslation"
												"[@tilesetname='{}']".format(tileSetName) +
												"/tiletranslation[@tilename='{}']".format(tileName))

		if existingTileWithTileName is not None:
			raise ValueError(	"Tile already exists in tileset in translation table. "
								"tileset: {} tilename: {}".format(tileSetName, tileName))

		tileSet = self._tileSetTranslations.find(	"./tilesettranslation" 
													"[@tilesetname='{}']".format(tileSetName))
		if tileSet is None:
			self.addTileSet(tileSetName)

		tileSet = self._tileSetTranslations.find(	"./tilesettranslation" 
													"[@tilesetname='{}']".format(tileSetName))

		newTile = self._createTileTranslationElementWithTileName(tileName)
		tileSet.append(newTile)
		
	def addTileSet(self, tileSetName):
		existingTileSet = self._tileSetTranslations.find(	"./tilesettranslation[@tilesetname="
															"'{}']".format(tileSetName))
		if existingTileSet is not None:
			raise ValueError(	"Tileset already exists in translation table. "
								"tileset: {}".format(tileSetName))

		tileSet = xml.etree.ElementTree.Element(	"tilesettranslation",
													{"tilesetname" : tileSetName})
		self._tileSetTranslations.append(tileSet)

	def addTileTranslationValue(self, tileSetName, tileName, translationType, translationValue):
		
		pathToTranslationValue = \
		"./tilesettranslation[@tilesetname='{}']/tiletranslation[@tilename='{}']/values/{}".format(
		tileSetName, tileName, translationValue)

		existingTranslationValue = self._tileSetTranslations.find(pathToTranslationValue)

		if existingTranslationValue is not None:
			raise ValueError(	"Tile already has translation for translation type. "
								"tilename: {} translationType: {}".format(	tileName,
																			translationType))


		tileValuesElement = self._tileSetTranslations.find(
								"./tilesettranslation[@tilesetname='{}']/".format(tileSetName) +
								"tiletranslation[@tilename='{}']/values".format(tileName))
		
		if tileValuesElement is None:
			self.addTile(tileSetName, tileName)
			tileValuesElement = self._tileSetTranslations.find(
									"./tilesettranslation[@tilesetname='{}']/".format(tileSetName) +
									"tiletranslation[@tilename='{}']/values".format(tileName))

		translationValueElement = \
		xml.etree.ElementTree.SubElement(tileValuesElement,translationType)
		translationValueElement.text = translationValue



	# def getDefaultTileTranslationValue(self, tileName, translationType):
	# 	tileTranslation =	self._defaultTranslations.find(	"./tiletranslation" + 
	# 														"[@tilename='{}']".format(tileName) +
	# 														"/values/{}".format(translationType))
	# 	if tileTranslation is not None:
	# 		return translationType.text

	# 	return None

	
	def getCSV(self):
		rowsToBeWrittenToCSV = []
		translationTypesUsed = \
						self._getTranslationTypesUsedInTileSetTranslation(self._defaultTranslations)

		defaultTranslationsHeaderRow = self._createTilesetHeaderRow(	"DEFAULTS",
																		translationTypesUsed)
		rowsToBeWrittenToCSV.append(defaultTranslationsHeaderRow)
		defaultTileTranslationElements = self._defaultTranslations.findall("tiletranslation")
		defaultTileTranslationElements.sort(key = lambda element: element.attrib["tilename"])

		for defaultTileTranslationElement in defaultTileTranslationElements:
			rowsToBeWrittenToCSV.append(self._getTileTranslationRow(defaultTileTranslationElement,
																	translationTypesUsed))

		for tileSetTranslationElement in \
			self._root.findall("./tilesettranslations/tilesettranslation"):

			translationTypesUsed = \
					self._getTranslationTypesUsedInTileSetTranslation(tileSetTranslationElement)

			tileSetTranslationHeaderRow = \
					self._createTilesetHeaderRow(	tileSetTranslationElement.attrib["tilesetname"],
													translationTypesUsed)

			
			tileTranslationElements = tileSetTranslationElement.findall("tiletranslation")
			tileTranslationElements.sort(key = lambda element: element.attrib["tilename"])
			

			rowsToBeWrittenToCSV.append(self._EMPTYCSVROW)
			rowsToBeWrittenToCSV.append(tileSetTranslationHeaderRow)

			for tileTranslationElement in tileTranslationElements:
				rowsToBeWrittenToCSV.append(self._getTileTranslationRow(	tileTranslationElement,
																			translationTypesUsed))

		with io.StringIO() as stringBuffer:
			writer = csv.writer(stringBuffer, quoting = csv.QUOTE_NONE)
			writer.writerows(rowsToBeWrittenToCSV)

			return stringBuffer.getvalue()

	def getTileSetNamesAsList(self):
		tileSetNames = set()
		for tileSetTranslation in self._tileSetTranslations:
			tileSetNames.add(tileSetTranslation.attrib['tilesetname'])

		return list(tileSetNames)

	def getTranslationTypesAsList(self):
		translationTypes = set()
		translationTypeElements = \
			self._defaultTranslations.findall('./tiletranslation/values/*')

		for translationTypeElement in translationTypeElements:
			translationTypes.add(translationTypeElement.tag)

		translationTypeElements = \
			self._tileSetTranslations.findall('./tilesettranslation/tiletranslation/values/*')

		for translationTypeElement in translationTypeElements:
			translationTypes.add(translationTypeElement.tag)

		return list(translationTypes)

	def getTranslationTypesForTileSetTranslationAsList(self, tileSetTranslationName):
		tileSetTranslationElement = \
			self._tileSetTranslations.find(
			'./tilesettranslation[@tilesetname="{}"]'.format(tileSetTranslationName))

		if tileSetTranslationElement is None:
			raise IndexError(
				"No tilesettranslation element found for {}".format(tileSetTranslationName))

		translationTypes = set()
		translationTypeElements = \
			tileSetTranslationElement.findall('./tiletranslation/values/*')

		for translationTypeElement in translationTypeElements:
			translationTypes.add(translationTypeElement.tag)

		return list(translationTypes)

	def getXML(self):
		tree = xml.etree.ElementTree.ElementTree()
		tree._setroot(self._root)
		with io.BytesIO() as byteBuffer:
			tree.write(byteBuffer, encoding = "UTF-8", xml_declaration = True)
			return byteBuffer.getvalue().decode(encoding='UTF-8')

	def loadFromXMLFile(self, fileName):
		with open(fileName, 'r') as XMLFile:
			XMLString = XMLFile.read()

		self._root = xml.etree.ElementTree.XML(XMLString)
		self._defaultTranslations = self._root.find("./defaulttranslations")
		if self._defaultTranslations is None:
			self._defaultTranslations = xml.etree.ElementTree.SubElement(	self._root, 
																		'defaulttranslations')
		self._tileSetTranslations = self._root.find("./tilesettranslations")

	def loadFromCSVFile(self, fileName):
		self._reset()
		with open(fileName, "r", newline = '') as CSVFile:
			translationTableReader = csv.reader(CSVFile)

			state = 1
			for row in translationTableReader:
				if self._checkForEmptyCSVRow(row):
					state = 1
				elif state == 1:
					currentTileSetHeader = row[:]
					state = 2
				else:
					if currentTileSetHeader[0] == "DEFAULTS":
						for column in range(1, len(row)):
							if row[column] != '':
								self.addDefaultTileTranslationValue(row[0],
																	currentTileSetHeader[column],
																	row[column])
					else:
						for column in range(1, len(row)):
							if row[column] != '':
								self.addTileTranslationValue(	currentTileSetHeader[0], row[0],
																currentTileSetHeader[column],
																row[column])

	def setTranslationTableName(self, translationTableName):
		self._root.attrib["name"] = translationTableName
	
	def setTranslationTableVersion(self, translationTableVersion):
		self._root.attrib["version"] = translationTableVersion

	def _checkForEmptyCSVRow(self, row):
		for cell in row:
			if cell != '':
				return False
		return True

	def _createTilesetHeaderRow(self, setName, translationTypesUsedInSet):
		headerRow = [setName]
		headerRow.extend(translationTypesUsedInSet)

		return headerRow

	def _createTileTranslationElementWithTileName(self, tileName):
		tileTranslation = xml.etree.ElementTree.Element("tiletranslation", {"tilename" : tileName})
		xml.etree.ElementTree.SubElement(tileTranslation, 'values')

		return tileTranslation

	def _getTileTranslationRow(self, tileTranslationElement, translationTypesUsedInSet):
		tileTranslationRow = [None for x in range(len(translationTypesUsedInSet))]
		for translationType in tileTranslationElement.findall("./values/*"):
			
			tileTranslationRow[translationTypesUsedInSet.index(translationType.tag)] = \
				translationType.text

		tileTranslationRow.insert(0, tileTranslationElement.attrib["tilename"])

		return tileTranslationRow

	def _getTranslationTypesUsedInTileSetTranslation(self, tileSetTranslationElement):
		translationTypeElements = tileSetTranslationElement.iterfind("./tiletranslation/values/*")
		translationTypesUsedInSet = list(set([element.tag for element in translationTypeElements]))
		translationTypesUsedInSet.sort()

		return translationTypesUsedInSet

	def _reset(self):
		self._root = xml.etree.ElementTree.Element("tiletranslationtable", {"name":"default",
																			"version":"0.1"})
		self._defaultTranslations = xml.etree.ElementTree.SubElement(	self._root, 
																		'defaulttranslations')
		self._tileSetTranslations = \
			xml.etree.ElementTree.SubElement(self._root, 'tilesettranslations')