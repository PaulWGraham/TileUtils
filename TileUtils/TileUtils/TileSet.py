# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

"""
TileSet module.

Provides limited support for dealing with .tsx tileset files.
"""


import xml.etree.ElementTree

class TileSet():

	def __init__(self, filename = None):
		if filename is not None:
			self.loadFromXMLFile(filename)

	def loadFromXMLFile(self, filename):
		"""Load a tileset from a .tsx file."""
		with open(filename, 'r') as XMLFile:
			XMLString = XMLFile.read()

		self._root = xml.etree.ElementTree.XML(XMLString)

	def getTileNamesAsList(self):
		"""
		Return a list made up of the names of each tile with a property whos name value is name.
		"""
		tileNames = []
		tileNamePropertyElements = self._root.findall('./tile/properties/property[@name="name"]')
		for tileNamePropertyElement in tileNamePropertyElements:
			tileNames.append(tileNamePropertyElement.attrib['value'])

		return tileNames

	def getTileSetName(self):
		"""
		Return the name of the currently loaded tileset.

		The name returned is the name stored in name attribute of the tileset element.
		"""
		return self._root.attrib['name']



