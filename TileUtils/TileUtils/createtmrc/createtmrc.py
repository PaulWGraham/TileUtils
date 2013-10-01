#!/usr/bin/env python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.
"""
A GUI utility for creating a TileMap Run Configuration file.
"""

import argparse
import os.path
import sys
import tkinter
import tkinter.filedialog
import tkinter.ttk
import xml.etree.ElementTree

import TileUtils.TranslationTable

class TMRCModel():
	"""
	A data model used for adding tmrc options to a .tmx tilemap file.
	"""
	def __init__(self, pathToTileMapFile, pathToTMRCFile):
		self._changed = set()
		self._observers = set()
		self._reset()

		self._pathToTileMapFile = pathToTileMapFile
		self._pathToTMRCFile = pathToTMRCFile

		if self._pathToTMRCFile is not None:
			self.loadTMRCFromFile(self._pathToTMRCFile)

	def clearCommandLine(self):
		"""
		Clear the TMRC command line and notify observers.
		"""
		self._commandLine = None
		self.setChanged('COMMANDLINE')
		self.notifyObservers()

	def clearEnv(self):
		"""
		Clear the TMRC environment and notify observers.
		"""
		self._env = None
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearLink(self):
		"""
		Clear the TMRC link and notify observers.
		"""
		self._link = False
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearNoDefaults(self):
		"""
		Clear the TMRC nodefaults and notify observers.
		"""
		self._nodefaults = False
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearPathToSaveFile(self):
		"""
		Clear the TMRC path to save and notify observers.
		"""
		self._pathToSaveFile = None
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearPathToTranslationTable(self):
		"""
		Clear the TMRC translation table path and notify observers.
		"""
		self._pathToTranslationTable = None
		self.setChanged('TRANSLATIONTABLE')
		self.notifyObservers()

	def clearRemap(self):
		"""
		Clear the TMRC remap and notify observers.
		"""
		self._remap = []
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearSteps(self):
		"""
		Clear the TMRC steps and notify observers.
		"""
		self._steps = []
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def clearTranslationType(self):
		"""
		Clear the TMRC translation type and notify observers.
		"""
		self._translationType = None
		self.setChanged('OPTIONS')
		self.notifyObservers()

	def getCommandLine(self):
		"""
		Return the the TMRC command line.
		"""
		return self._commandLine

	def getEnv(self):
		"""
		Return the the TMRC environment.
		"""
		return self._env

	def getLink(self):
		"""
		Return the the TMRC link.
		"""
		return self._link

	def getNoDefaults(self):
		"""
		Return a the value of TMRC nodefaults.
		"""
		return self._nodefaults

	def getPathToSaveFile(self):
		"""
		Return the value of the TMRC save path.
		"""

		return self._pathToSaveFile

	def getPathToTileMapFile(self):
		"""
		Return the path to the .tmx tile file the the TMRC option will be added to.
		"""
		return self._pathToTileMapFile

	def getPathToTranslationTable(self):
		"""
		Return the the TMRC translation table.
		"""
		return self._pathToTranslationTable

	def getRemap(self):
		"""
		Return the the TMRC remap.
		"""
		return self._remap

	def getSteps(self):
		"""
		Return a list (in the order [x, y, z]) of the TMRC steps.
		"""
		return self._steps

	def getTileSetsUsedInTranslationTable(self):
		"""
		Return a list of the names of the tile sets used in the TMRC translation table.
		"""
		if self._translationTable:
			return self._translationTable.getTileSetNamesAsList()
		return []

	def getTranslationType(self):
		"""
		Return the the TMRC translation type.
		"""
		return self._translationType

	def getTranslationTypesUsedInTranslationTable(self):
		"""
		Return a list of the types used in the TMRC translation table.
		"""
		if self._translationTable:
			return self._translationTable.getTranslationTypesAsList()
		return []

	def loadTMRCFromFile(self, pathToTMRCFile):
		"""
		Load a TMRC file.
		"""

		try:
			tmrcTree = xml.etree.ElementTree.parse(pathToTMRCFile)

		except FileNotFoundError:
			return False

		pathToTileMapFile = self._pathToTileMapFile
		self._reset()
		self._pathToTileMapFile = pathToTileMapFile
		self._pathToTMRCFile = pathToTMRCFile

		tmrcRoot = tmrcTree.getroot()
		translationTableElement = tmrcRoot.find('./options/option[@name="tmrc_translationtable"]')
		translationTypeElement = tmrcRoot.find('./options/option[@name="tmrc_translationtype"]') 
		envElement = tmrcRoot.find('./options/option[@name="tmrc_env"]')
		linkElement = tmrcRoot.find('./options/option[@name="tmrc_link"]')
		remapElement = tmrcRoot.find('./options/option[@name="tmrc_remap"]')
		stepsElement = tmrcRoot.find('./options/option[@name="tmrc_steps"]')
		noDefaultsElement = tmrcRoot.find('./options/option[@name="tmrc_nodefaults"]')
		saveElement = tmrcRoot.find('./options/option[@name="tmrc_save"]')
		commandLineElement = tmrcRoot.find('./options/option[@name="tmrc_commandline"]')

		if translationTableElement is not None:
			self._pathToTranslationTable = translationTableElement.text
			self._translationTable = TileUtils.TranslationTable.TranslationTable()
			self._translationTable.loadFromXMLFile(self._pathToTranslationTable)

		if translationTypeElement is not None:
			self._translationType = translationTypeElement.attrib['value']

		if envElement is not None:
			self._env = envElement.attrib['value']

		if linkElement is not None:
			self._link = True

		if remapElement is not None:
			self._remap = [remapElement.attrib['from'], remapElement.attrib['to']]

		if stepsElement is not None:
			self._steps = [	stepsElement.attrib["x"], stepsElement.attrib["y"],
							stepsElement.attrib["z"]]

		if noDefaultsElement is not None:
			self._nodefaults = True

		if saveElement is not None:
			self._pathToSaveFile = saveElement.text

		if commandLineElement is not None:
			self._commandLine = commandLineElement.text

		self.setChanged('TMRCFile', True)
		self.notifyObservers()

	def notifyObservers(self):
		"""
		Call the update function of each observer, passing it the type of change that occurred.
		"""
		if len(self._changed):
			for observer in self._observers:
				observer.update(self, list(self._changed))
			self._changed = set()

	def registerObserver(self, observer):
		"""
		Register an observer.
		"""
		self._observers.add(observer)

	def saveChangesTMRCFile(self):
		"""
		Save the TMRC to the currently loaded TMRC file.
		"""
		tmrcTree = None
		try:
			tmrcTree = xml.etree.ElementTree.parse(self._pathToTMRCFile)
		except FileNotFoundError:
			pass

		if tmrcTree is None:
			tmrcTree = xml.etree.ElementTree.ElementTree(xml.etree.ElementTree.Element("tmrc"))

		tmrcRoot = tmrcTree.getroot()
		optionsElement = tmrcRoot.find('./options')
		if optionsElement is None:
			modifiedOptionsElement = xml.etree.ElementTree.Element("options")
			optionsElement = None
			translationTableElement = None
			translationTypeElement = None
			envElement = None
			linkElement = None
			remapElement = None
			stepsElement = None
			noDefaultsElement = None
			saveElement = None
			commandLineElement = None
		else:
			modifiedOptionsElement = optionsElement
			translationTableElement = optionsElement.find('./option[@name="tmrc_translationtable"]')
			translationTypeElement = optionsElement.find('./option[@name="tmrc_translationtype"]')
			envElement = optionsElement.find('./option[@name="tmrc_env"]')
			linkElement = optionsElement.find('./option[@name="tmrc_link"]')
			remapElement = optionsElement.find('./option[@name="tmrc_remap"]')
			stepsElement = optionsElement.find('./option[@name="tmrc_steps"]')
			noDefaultsElement = optionsElement.find('./option[@name="tmrc_nodefaults"]')
			saveElement = optionsElement.find('./option[@name="tmrc_save"]')
			commandLineElement = optionsElement.find('./option[@name="tmrc_commandline"]')

		tmrcOptionsHaveChanged = False

		if self._pathToTranslationTable:
			if translationTableElement is None:
				translationTableElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement, "option",
														{'name' : "tmrc_translationtable"})
			
			translationTableElement.text = self._pathToTranslationTable
			tmrcOptionsHaveChanged = True
		else:
			if translationTableElement is not None:
				modifiedOptionsElement.remove(translationTableElement)
				tmrcOptionsHaveChanged = True


		if self._translationType:
			if translationTypeElement is None:
				translationTypeElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement,
														"option", {'name' : "tmrc_translationtype"})
			translationTypeElement.attrib['value'] = self._translationType
			tmrcOptionsHaveChanged = True
		else:
			if translationTypeElement is not None:
				modifiedOptionsElement.remove(translationTypeElement)
				tmrcOptionsHaveChanged = True

		if self._env:
			if envElement is None:
				envElement = xml.etree.ElementTree.SubElement(	modifiedOptionsElement, 
																"option", {'name' : "tmrc_env"})
			envElement.attrib['value'] = self._env
			tmrcOptionsHaveChanged = True
		else:
			if envElement is not None:
				modifiedOptionsElement.remove(envElement)
				tmrcOptionsHaveChanged = True

		if self._link:
			if linkElement is None:
				linkElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement,
														"option", { 'name' : "tmrc_link" })
			tmrcOptionsHaveChanged = True
		else:
			if linkElement is not None:
				modifiedOptionsElement.remove(linkElement)
				tmrcOptionsHaveChanged = True

		if self._remap:
			if remapElement is None:
				remapElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement, 
														"option", { 'name' : "tmrc_remap" })
			remapElement.attrib['from'] = self._remap[0]
			remapElement.attrib['to'] = self._remap[1]
			tmrcOptionsHaveChanged = True
		else:
			if remapElement is not None:
				modifiedOptionsElement.remove(remapElement)
				tmrcOptionsHaveChanged = True

		if self._steps:
			if stepsElement is None:
				stepsElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement,
														"option", { 'name' : "tmrc_steps" })
			stepsElement.attrib['x'] = self._steps[0]
			stepsElement.attrib['y'] = self._steps[1]
			stepsElement.attrib['z'] = self._steps[2]
			tmrcOptionsHaveChanged = True
		else:
			if stepsElement is not None:
				modifiedOptionsElement.remove(stepsElement)
				tmrcOptionsHaveChanged = True

		if self._nodefaults:
			if noDefaultsElement is None:
				noDefaultsElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement,
														"option", { 'name' : "tmrc_nodefaults" })
			tmrcOptionsHaveChanged = True
		else:
			if noDefaultsElement is not None:
				modifiedOptionsElement.remove(noDefaultsElement)
				tmrcOptionsHaveChanged = True

		if self._pathToSaveFile:
			if saveElement is None:
				saveElement = xml.etree.ElementTree.SubElement(	modifiedOptionsElement,
																"option", {'name' : "tmrc_save"})
			saveElement.text = self._pathToSaveFile
			tmrcOptionsHaveChanged = True
		else:
			if saveElement is not None:
				modifiedOptionsElement.remove(saveElement)
				tmrcOptionsHaveChanged = True

		if self._commandLine:
			if commandLineElement is None:
				commandLineElement = \
					xml.etree.ElementTree.SubElement(	modifiedOptionsElement, "option",
														{'name' : "tmrc_commandline"})

			commandLineElement.text = self._commandLine
			tmrcOptionsHaveChanged = True
		else:
			if commandLineElement is not None:
				modifiedOptionsElement.remove(commandLineElement)
				tmrcOptionsHaveChanged = True

		if tmrcOptionsHaveChanged:
			if optionsElement is not modifiedOptionsElement:
				tmrcRoot.append(modifiedOptionsElement)
			tmrcTree.write(self._pathToTMRCFile, 'UTF-8', True)

	def setChanged(self, typeOfChange, allChanged = False):
		"""
		Declare that a change of type typeOfChange has occurred since the last call to
		self.notifyObservers().
		"""		
		if allChanged:
			self._changed = set(	[	'TMRCFile', 'TRANSLATIONTABLE', 'TRANSLATIONTYPE',
										'COMMANDLINE', 'OPTIONS'])
		else:
			self._changed.add(typeOfChange)

	def setCommandLine(self, commandLine):
		"""
		Set the TMRC command line and notify observers.
		"""
		if self._commandLine != commandLine:
			self._commandLine = commandLine
			self.setChanged('COMMANDLINE')				
			self.notifyObservers()
			return True
		return False

	def setEnv(self, env):
		"""
		Set the TMRC environment and notify observers.
		"""
		if self._env != env:
			self._env = env
			self.setChanged('OPTIONS')				
			self.notifyObservers()

			return True
		return False

	def setLink(self, link):
		"""
		Set the TMRC the translation type and notify observers.
		"""
		if self._link != link:
			self._link = link
			self.setChanged('OPTIONS')				
			self.notifyObservers()

			return True
		return False

	def setNoDefaults(self, noDefaults):
		"""
		Set the TMRC nodefaults and notify observers.
		"""
		if self._nodefaults != noDefaults:
			self._nodefaults = noDefaults
			self.setChanged('OPTIONS')				
			self.notifyObservers()
			return True
		return False

	def setPathToSaveFile(self, path):
		"""
		Set the TMRC path to save and notify observers.
		"""
		if self._pathToSaveFile != path:
			self._pathToSaveFile = path
			self.setChanged('OPTIONS')				
			self.notifyObservers()
			return True
		return False

	def setPathToTranslationTable(self, path):
		"""
		Set the TMRC path to the translation table and notify observers.
		"""
		if self._pathToTranslationTable != path:
			self._pathToTranslationTable = path
			self._translationTable = TileUtils.TranslationTable.TranslationTable()
			self._translationTable.loadFromXMLFile(path)
			tileSetsUsed = self.getTileSetsUsedInTranslationTable()
			for remapValue in self._remap:
				if remapValue not in tileSetsUsed:
					self.clearRemap()
					break

			if self.getTranslationType() not in self.getTranslationTypesUsedInTranslationTable():
				self.clearTranslationType()

			self.setChanged('TRANSLATIONTABLE')				
			self.notifyObservers()
			return True
		return False

	def setRemap(self, fromSet, toSet):
		"""
		Set the TMRC remap and notify observers.
		"""
		if self._remap != [fromSet, toSet]:
			tileSetsUsed = self.getTileSetsUsedInTranslationTable()
			if fromSet not in tileSetsUsed or toSet not in tileSetsUsed:
				return False
			self._remap = [fromSet, toSet]
			self.setChanged('OPTIONS')
			self.notifyObservers()
			return True
		return False

	def setSteps(self, x, y, z):
		"""
		Set the TMRC steps and notify observers.
		"""
		steps = [str(x), str(y), str(z)]
		if self._steps != steps:
			self._steps = steps
			self.setChanged('OPTIONS')
			self.notifyObservers()
			return True
		return False

	def setTranslationType(self, translationType):
		"""
		Set the TMRC translation type and notify observers.
		"""
		if self._translationType != translationType and translationType in \
		self.getTranslationTypesUsedInTranslationTable():

			self._translationType = translationType
			self.setChanged('TRANSLATIONTYPE')				
			self.notifyObservers()

			return True
		return False

	def _reset(self):
		# Initialize/clear private member variables.
		self._pathToTMRCFile = None
		self._pathToTileMapFile = None
		self._translationTable = None
		self._pathToTranslationTable = None
		self._translationType = None
		self._env = None
		self._link = False
		self._remap = []
		self._steps = []
		self._nodefaults = False
		self._pathToSaveFile = None
		self._commandLine = None


class TMRCView(tkinter.ttk.Frame):
	"""
	A view used for adding tmrc options to a .tmx tilemap file.
	"""
	def __init__(self, master):
		tkinter.ttk.Frame.__init__(self, master)
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=2)
		self.columnconfigure(2, weight=2)
		self.columnconfigure(3, weight=1)

		self.grid(column = 0, row = 0)
		self._createWidgets()

	def _createWidgets(self):
		# Create and place widgets in the view
		self.pathToTileMapLabel = tkinter.ttk.Label(self, text = "Path To TileMap")
		self.pathToTileMapLabel.grid(	column = 0, row = 0, columnspan = 4,
										sticky = (tkinter.E, tkinter.W))
		self.toggleOptionsFrame = tkinter.ttk.Frame(self)
		self.toggleOptionsFrame.grid(column = 0, row = 1, sticky = (tkinter.W, tkinter.E))
		self.useLinkToggleCheckbutton = tkinter.ttk.Checkbutton(self.toggleOptionsFrame,
																text = "--link")
		self.useLinkToggleCheckbutton.grid(column = 0, row = 1, sticky = (tkinter.W))
		self.useNoDefaultsToggleCheckbutton = tkinter.ttk.Checkbutton(	self.toggleOptionsFrame, 
																		text = "--nodefaults")
		self.useNoDefaultsToggleCheckbutton.grid(column = 0, row = 2, sticky = (tkinter.W))
		
		self.remapFrame = tkinter.ttk.Frame(self)
		self.remapFrame.grid(column = 0, row = 2, sticky = (tkinter.W, tkinter.E))
		self.enableRemapCheckbutton = tkinter.ttk.Checkbutton(self.remapFrame, text = "--remap")
		self.enableRemapCheckbutton.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.remapFromLabel = tkinter.ttk.Label(self.remapFrame, text = "from")
		self.remapFromLabel.grid(column = 0, row = 1, sticky = (tkinter.E))
		self.remapFromCombobox = tkinter.ttk.Combobox(self.remapFrame)
		self.remapFromCombobox.grid(column = 1, row = 1, sticky = (tkinter.W))
		self.remapToLabel = tkinter.ttk.Label(self.remapFrame, text = "to")
		self.remapToLabel.grid(column = 0, row = 2, sticky = (tkinter.E))
		self.remapToCombobox = tkinter.ttk.Combobox(self.remapFrame)
		self.remapToCombobox.grid(column = 1, row = 2, sticky = (tkinter.W))

		self.stepsFrame = tkinter.ttk.Frame(self)
		self.stepsFrame.grid(column = 0, row = 3, sticky = (tkinter.W, tkinter.E))
		self.enableStepsCheckbutton = tkinter.ttk.Checkbutton(self.stepsFrame, text = "--steps")
		self.enableStepsCheckbutton.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.stepsXLabel = tkinter.ttk.Label(self.stepsFrame, text = "X")
		self.stepsXLabel.grid(column = 0, row = 1, sticky = (tkinter.E))
		self.stepsXSpinbox = tkinter.Spinbox(self.stepsFrame)
		self.stepsXSpinbox.grid(column = 1, row = 1, sticky = (tkinter.W))
		self.stepsYLabel = tkinter.ttk.Label(self.stepsFrame, text = "Y")
		self.stepsYLabel.grid(column = 0, row = 2, sticky = (tkinter.E))
		self.stepsYSpinbox = tkinter.Spinbox(self.stepsFrame)
		self.stepsYSpinbox.grid(column = 1, row = 2, sticky = (tkinter.W))
		self.stepsZLabel = tkinter.ttk.Label(self.stepsFrame, text = "Z")
		self.stepsZLabel.grid(column = 0, row = 3, sticky = (tkinter.E))
		self.stepsZSpinbox = tkinter.Spinbox(self.stepsFrame)
		self.stepsZSpinbox.grid(column = 1, row = 3, sticky = (tkinter.W))

		self.saveFrame = tkinter.ttk.Frame(self)
		self.saveFrame.grid(column = 0, row = 4, sticky = (tkinter.W, tkinter.E))
		self.enableSaveToggleCheckbutton = tkinter.ttk.Checkbutton(self.saveFrame, text = "--save")
		self.enableSaveToggleCheckbutton.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.pathToSaveFileEntry = tkinter.ttk.Entry(self.saveFrame)
		self.pathToSaveFileEntry.grid(column = 0, row = 1, sticky = (tkinter.E))
		self.launchFileDialogToPickSaveFileButton = tkinter.ttk.Button(	self.saveFrame,
																		text="Browse")
		self.launchFileDialogToPickSaveFileButton.grid(column = 1, row = 1, sticky = (tkinter.W))

		self.translationTableFrame = tkinter.ttk.Frame(self)
		self.translationTableFrame.grid(column = 3, row = 1, sticky = (tkinter.W, tkinter.E))
		self.translationTableLabel = tkinter.ttk.Label(	self.translationTableFrame,
														text = "Translation Table")
		self.translationTableLabel.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.currentTranslationTablePathEntry = tkinter.ttk.Entry(self.translationTableFrame)
		self.currentTranslationTablePathEntry.grid(column = 0, row = 1, sticky = (tkinter.E))
		self.launchFileDialogToPickTranslationTableFileButton = tkinter.ttk.Button(
																		self.translationTableFrame,
																		text="Browse")
		self.launchFileDialogToPickTranslationTableFileButton.grid(	column = 1, row = 1,
																	sticky = (tkinter.W))

		self.translationTypeFrame = tkinter.ttk.Frame(self)
		self.translationTypeFrame.grid(column = 3, row = 2, sticky = (tkinter.W, tkinter.E))
		self.translationTypeLabel = tkinter.ttk.Label(	self.translationTypeFrame,
														text = "Translation Type")
		self.translationTypeLabel.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.pickTranslationTypeCombobox = tkinter.ttk.Combobox(self.translationTypeFrame)
		self.pickTranslationTypeCombobox.grid(column = 0, row = 1)

		self.runCommandFrame = tkinter.ttk.Frame(self)
		self.runCommandFrame.grid(column = 3, row = 3, sticky = (tkinter.W, tkinter.E))
		self.useStandardRunCommandRadiobutton = tkinter.ttk.Radiobutton(self.runCommandFrame, text = 
																		"Use Standard Run Command")
		self.useStandardRunCommandRadiobutton.grid(column = 0, row = 0, sticky = (tkinter.W))
		self.standardRunCommandCombobox = tkinter.ttk.Combobox(self.runCommandFrame)
		self.standardRunCommandCombobox.grid(column = 0, row = 1, sticky = (tkinter.E))
		self.useCustomRunCommandRadiobutton = tkinter.ttk.Radiobutton(self.runCommandFrame, text = 
																		"Use Custom Run Command")
		self.useCustomRunCommandRadiobutton.grid(column = 0, row = 2, sticky = (tkinter.W))

		self.customRunCommandEntry = tkinter.ttk.Entry(self.runCommandFrame)
		self.customRunCommandEntry.grid(column = 0, row = 3, sticky = (tkinter.E))
		self.runCommandLabel = tkinter.ttk.Label(self.runCommandFrame, text = "Run Command")
		self.runCommandLabel.grid(column = 0, row = 4, sticky = (tkinter.W))
		self.currentRunCommandLabel = tkinter.ttk.Label(self.runCommandFrame)
		self.currentRunCommandLabel.grid(column = 0, row = 5, sticky = (tkinter.W, tkinter.E))

		self.buttonFrame = tkinter.ttk.Frame(self)
		self.buttonFrame.grid(column = 3, row = 7, sticky=(tkinter.E))
		self.setButton = tkinter.ttk.Button(self.buttonFrame, text = "Set")
		self.setButton.grid(column = 0, row = 0)
		self.cancelButton = tkinter.ttk.Button(self.buttonFrame, text = "Cancel")
		self.cancelButton.grid(column = 1, row = 0)
		


class TMRCController():
	"""
	A controller used for connecting a TMRCView to a TMRCModel.
	"""
	def __init__ (self, model, defaults = None):
		if defaults is None:
			defaults = {'commandLines':[],
						'steps':[1,1,1],
						'exitSet':False,
						'errorCancel':False}

		self._standardRunCommandNames = []
		self._standardRunCommandLines = []
		for commandLine in defaults['commandLines']:
			self._standardRunCommandNames.append(commandLine[0])
			self._standardRunCommandLines.append(commandLine[1])

		self._defaultXStepValue = defaults['steps'][0]
		self._defaultYStepValue = defaults['steps'][1]
		self._defaultZStepValue = defaults['steps'][2]

		self._exitOnSet = defaults['exitSet']
		self._errorOnCancel = defaults['errorCancel']

		self.model = model
		root = tkinter.Tk()
		root.wm_title("Create TMRC")
		self._tmrcView = TMRCView(root)
		self.model.registerObserver(self)
		
		self._disableAll()

		self._standardRunCommandRadiobuttonValue = 0
		self._customRunCommandRadiobuttonValue = 1
		self._unselectedRunCommandRadiobuttonValue = 100
		self._runCommandRadiobuttonControlVariable = tkinter.IntVar()
		self._tmrcView.useStandardRunCommandRadiobutton['variable'] = \
			self._runCommandRadiobuttonControlVariable

		self._tmrcView.useCustomRunCommandRadiobutton['variable'] = \
			self._runCommandRadiobuttonControlVariable

		self._tmrcView.useStandardRunCommandRadiobutton['value'] = \
			self._standardRunCommandRadiobuttonValue

		self._tmrcView.useCustomRunCommandRadiobutton['value'] = \
			self._customRunCommandRadiobuttonValue
	
		self._tmrcView.useStandardRunCommandRadiobutton['command'] = \
			self._runCommandRadioButtonCallback
		self._tmrcView.useCustomRunCommandRadiobutton['command'] = \
			self._runCommandRadioButtonCallback

		self._runCommandEntryControlVariable = tkinter.StringVar()
		self._runCommandEntryCallbackIdentifier = \
			self._runCommandEntryControlVariable.trace('w', self._runCommandEntryCallback)

		self._tmrcView.customRunCommandEntry['textvariable'] = self._runCommandEntryControlVariable

		self._translationTableEntryVariable = tkinter.StringVar()
		self._translationTableEntryCallbackIdentifier = \
			self._translationTableEntryVariable.trace('w', self._translationTableEntryCallback)

		self._tmrcView.currentTranslationTablePathEntry['textvariable'] = \
			self._translationTableEntryVariable

		self._tmrcView.currentTranslationTablePathEntry['state'] = 'readonly'
		self._tmrcView.launchFileDialogToPickTranslationTableFileButton['command'] = \
			self._translationTableBrowseButtonCallback
		
		self._tmrcView.pickTranslationTypeCombobox.bind('<<ComboboxSelected>>', 
				self._translationTypeCallback)


		self._useLinkToggleCheckbuttonControlVariable = tkinter.IntVar()
		self._tmrcView.useLinkToggleCheckbutton['variable'] = self._useLinkToggleCheckbuttonControlVariable
		self._tmrcView.useLinkToggleCheckbutton['command'] = self._linkCheckbuttonCallback
		self._useLinkToggleCheckbuttonControlVariable.set(0)

		self._useNoDefaultsToggleCheckbuttonControlVariable = tkinter.IntVar()
		self._tmrcView.useNoDefaultsToggleCheckbutton['variable'] = \
			self._useNoDefaultsToggleCheckbuttonControlVariable

		self._tmrcView.useNoDefaultsToggleCheckbutton['command'] = \
			self._noDefaultsCheckbuttonCallback

		self._useNoDefaultsToggleCheckbuttonControlVariable.set(0)

		self._enableRemapCheckbuttonControlVariable = tkinter.IntVar()
		self._tmrcView.enableRemapCheckbutton['variable'] = \
			self._enableRemapCheckbuttonControlVariable

		self._enableRemapCheckbuttonControlVariable.set(0)
		self._tmrcView.enableRemapCheckbutton['command'] = self._remapCheckbuttonCallback

		self._tmrcView.remapFromCombobox.bind('<<ComboboxSelected>>', self._remapCallback)
		self._tmrcView.remapToCombobox.bind('<<ComboboxSelected>>', self._remapCallback)


		self._enableStepsCheckbuttonControlVariable = tkinter.IntVar()
		self._tmrcView.enableStepsCheckbutton['variable'] = \
			self._enableStepsCheckbuttonControlVariable

		self._enableStepsCheckbuttonControlVariable.set(0)

		self._tmrcView.enableStepsCheckbutton['command'] = self._stepsCheckbuttonCallback


		self._stepsXSpinboxControlVariable = tkinter.IntVar()
		self._tmrcView.stepsXSpinbox['textvariable'] = self._stepsXSpinboxControlVariable
		self._stepsYSpinboxControlVariable = tkinter.IntVar()
		self._tmrcView.stepsYSpinbox['textvariable'] = self._stepsYSpinboxControlVariable
		self._stepsZSpinboxControlVariable = tkinter.IntVar()
		self._tmrcView.stepsZSpinbox['textvariable'] = self._stepsZSpinboxControlVariable

		self._tmrcView.stepsXSpinbox['command'] = self._stepsSpinboxCallback
		self._tmrcView.stepsYSpinbox['command'] = self._stepsSpinboxCallback
		self._tmrcView.stepsZSpinbox['command'] = self._stepsSpinboxCallback

		self._tmrcView.stepsXSpinbox['from_'] = 0
		self._tmrcView.stepsYSpinbox['from_'] = 0
		self._tmrcView.stepsZSpinbox['from_'] = 0

		self._tmrcView.stepsXSpinbox['to'] = 100000
		self._tmrcView.stepsYSpinbox['to'] = 100000
		self._tmrcView.stepsZSpinbox['to'] = 100000

		self._enableSaveCheckbuttonControlVariable = tkinter.IntVar()
		self._tmrcView.enableSaveToggleCheckbutton['variable'] = \
			self._enableSaveCheckbuttonControlVariable

		self._tmrcView.enableSaveToggleCheckbutton['onvalue'] = 1
		self._tmrcView.enableSaveToggleCheckbutton['offvalue'] = 0

		self._enableSaveCheckbuttonControlVariable.set(0)
		self._tmrcView.enableSaveToggleCheckbutton['command'] = self._saveCheckbuttonCallback
		self._tmrcView.launchFileDialogToPickSaveFileButton['command'] = \
			self._saveFileBrowseButtonCallback

		self._saveFileEntryControlVariable = tkinter.StringVar()
		self._tmrcView.pathToSaveFileEntry['textvariable'] = self._saveFileEntryControlVariable
		self._saveFileEntryCallbackIdentifier = self._saveFileEntryControlVariable.trace('w',
			self._saveFileEntryCallback)

		self._tmrcView.setButton['command'] = self._setButtonCallback
		self._tmrcView.cancelButton['command'] = self._cancelButtonCallback

		self._updateAll()

		self._tmrcView.mainloop()

	def update(self, model, typesOfUpdates):
		"""
		Update view to display the contents of model.
		"""
		if 'TMRCFile' in typesOfUpdates:
			self._updateAll()
		else:
			if 'TRANSLATIONTABLE' in typesOfUpdates:
				self._updateTranslationTable()
				self._updateTranslationType()
				self._updateRemap()
			elif 'TRANSLATIONTYPE' in typesOfUpdates:
				self._updateTranslationType()
				self._updateRemap()

			if 'COMMANDLINE' in typesOfUpdates:
				self._updateRunCommand()

			if 'OPTIONS' in typesOfUpdates:
				self._updateOptions()

	def _cancelButtonCallback(self):
		# Callback used for self._tmrcView.cancelButton
		if self._errorOnCancel:
			sys.exit(1)
		sys.exit(0)

	def _disableAll(self):
		# Disables all entry widgets in self._tmrcView.
		self._disableRequired()
		self._disableOptions()

	def _disableLink(self):
		# Disables the entry widget in self._tmrcView that represents TMRC link option.
		self._tmrcView.useLinkToggleCheckbutton['state'] = tkinter.DISABLED

	def _disableNoDefaults(self):
		# Disables the entry widget in self._tmrcView that represents TMRC nodefaults option.
		self._tmrcView.useNoDefaultsToggleCheckbutton['state'] = tkinter.DISABLED
		
	def _disableOptions(self):
		# Disables all entry widgets in self._tmrcView that represent optional TMRC options.
		self._disableLink()
		self._disableNoDefaults()
		self._disableSteps()
		self._disableRemap()
		self._disableSave()

	def _disableRemap(self):
		# Disables the entry widgets in self._tmrcView that represent the TMRC remap option.
		self._tmrcView.enableRemapCheckbutton['state'] = tkinter.DISABLED
		self._tmrcView.remapFromLabel['state'] = tkinter.DISABLED
		self._tmrcView.remapFromCombobox['state'] = tkinter.DISABLED
		self._tmrcView.remapToLabel['state'] = tkinter.DISABLED
		self._tmrcView.remapToCombobox['state'] = tkinter.DISABLED

	def _disableRequired(self):
		# Disables all entry widgets in self._tmrcView the represent required TMRC options.
		self._disableTranslationTable()
		self._disableTranslationType()
		self._disableRunCommand()

	def _disableRunCommand(self):
		# Disables the entry widgets associated with TMRC run command.
		self._tmrcView.useStandardRunCommandRadiobutton['state'] = tkinter.DISABLED
		self._tmrcView.standardRunCommandCombobox['state'] = tkinter.DISABLED
		self._tmrcView.useCustomRunCommandRadiobutton['state'] = tkinter.DISABLED
		self._tmrcView.customRunCommandEntry['state'] = tkinter.DISABLED

	def _disableSave(self):
		# Disables the entry widgets in self._tmrcView that represent the TMRC save option.
		self._tmrcView.enableSaveToggleCheckbutton['state'] = tkinter.DISABLED
		self._tmrcView.pathToSaveFileEntry['state'] = tkinter.DISABLED
		self._tmrcView.launchFileDialogToPickSaveFileButton['state'] = tkinter.DISABLED

	def _disableSteps(self):
		# Disables the entry widgets in self._tmrcView that represent the TMRC steps option.
		self._tmrcView.enableStepsCheckbutton['state'] = tkinter.DISABLED
		self._tmrcView.stepsXLabel['state'] = tkinter.DISABLED
		self._tmrcView.stepsXSpinbox ['state'] = tkinter.DISABLED
		self._tmrcView.stepsYLabel['state'] = tkinter.DISABLED
		self._tmrcView.stepsYSpinbox['state'] = tkinter.DISABLED
		self._tmrcView.stepsZLabel['state'] = tkinter.DISABLED
		self._tmrcView.stepsZSpinbox['state'] = tkinter.DISABLED

	def _disableTranslationTable(self):
		# Disables the entry widgets associated with TMRC path to translation table.
		self._tmrcView.currentTranslationTablePathEntry['state'] = tkinter.DISABLED
		self._tmrcView.launchFileDialogToPickTranslationTableFileButton['state'] = tkinter.DISABLED

	def _disableTranslationType(self):
		# Disables the entry widgets associated with TMRC translation type.
		self._tmrcView.pickTranslationTypeCombobox['state'] = tkinter.DISABLED

	def _linkCheckbuttonCallback(self):
		# Callback used for self._tmrcView.useLinkToggleCheckbutton
		if self._useLinkToggleCheckbuttonControlVariable.get() == 1:
			self.model.setLink(True)
		else:
			self.model.clearLink()

	def _noDefaultsCheckbuttonCallback(self):
		# Callback used for self._tmrcView.useNoDefaultsToggleCheckbutton
		if self._useNoDefaultsToggleCheckbuttonControlVariable.get() == 1:
			self.model.setNoDefaults(True)
		else:
			self.model.clearNoDefaults()

	def _remapCallback(self, tkevent):
		# Callback used for self._tmrcView.remapFromCombobox
		if self._enableRemapCheckbuttonControlVariable.get() == 1:
			self.model.setRemap(self._tmrcView.remapFromCombobox.get(),
				self._tmrcView.remapToCombobox.get())
		else:
			self.model.clearRemap()

	def _remapCheckbuttonCallback(self):
		# Callback used for self._tmrcView.enableRemapCheckbutton
		if self._enableRemapCheckbuttonControlVariable.get() == 1:
			self._tmrcView.remapFromCombobox['state'] = 'readonly'
			self._tmrcView.remapToCombobox['state'] = 'readonly'
			self.model.setRemap(self._tmrcView.remapFromCombobox.get(),
				self._tmrcView.remapToCombobox.get())
		else:
			self.model.clearRemap()

	def _runCommandEntryCallback(self, tkVariableName, tkVariableIndex, traceMode):
		# Callback used for self._runCommandEntryControlVariable.
		runCommand = self._runCommandEntryControlVariable.get()
		if runCommand:
			self.model.setCommandLine(runCommand)

	def _runCommandRadioButtonCallback(self):
		# Callback used for self._tmrcView.useStandardRunCommandRadiobutton and
		# self._tmrcView.useCustomRunCommandRadiobutton.
		if self._runCommandRadiobuttonControlVariable.get() == 0:
			self.model.clearCommandLine()
			currentRunCommandName = self._tmrcView.standardRunCommandCombobox.get()
			if currentRunCommandName:
				self.model.setCommandLine(
					self._standardRunCommandLines[self._standardRunCommandNames.index(
						currentRunCommandName)])

			self._tmrcView.standardRunCommandCombobox['state'] = tkinter.NORMAL
			self._tmrcView.customRunCommandEntry['state'] = 'readonly'
		else:
			self._tmrcView.customRunCommandEntry['state'] = tkinter.NORMAL
			self._tmrcView.standardRunCommandCombobox['state'] = tkinter.DISABLED

	def _saveCheckbuttonCallback(self):
		# Callback used for self._tmrcView.enableSaveToggleCheckbutton.
		if self._enableSaveCheckbuttonControlVariable.get() == 1:
			self.model.setPathToSaveFile(self._saveFileEntryControlVariable.get())
			self._tmrcView.pathToSaveFileEntry['state'] = 'readonly'
			self._tmrcView.launchFileDialogToPickSaveFileButton['state'] = tkinter.NORMAL
		else:
			self._tmrcView.pathToSaveFileEntry['state'] = tkinter.DISABLED
			self._tmrcView.launchFileDialogToPickSaveFileButton['state'] = tkinter.DISABLED
			self.model.clearPathToSaveFile()

	def _saveFileBrowseButtonCallback(self):
		# Callback used for self._tmrcView.launchFileDialogToPickSaveFileButton
		pathToSaveFile = tkinter.filedialog.asksaveasfilename(parent = self._tmrcView)
		if pathToSaveFile:
			self.model.setPathToSaveFile(pathToSaveFile)

	def _saveFileEntryCallback(self):
		# Callback used for self._saveFileEntryControlVariable
		self.model.setPathToSaveFile(self._saveFileEntryControlVariable.get())

	def _setButtonCallback(self):
		# Callback used for self._tmrcView.setButton
		self.model.saveChangesTMRCFile()
		if self._exitOnSet:
			sys.exit(0)

	def _stepsCheckbuttonCallback(self):
		# Callback used for self._tmrcView.enableStepsCheckbutton.
		if self._enableStepsCheckbuttonControlVariable.get() == 1:
			self.model.setSteps(	self._stepsXSpinboxControlVariable.get(),
									self._stepsYSpinboxControlVariable.get(),
									self._stepsZSpinboxControlVariable.get())

			self._tmrcView.stepsXSpinbox['state'] = 'readonly'
			self._tmrcView.stepsYSpinbox['state'] = 'readonly'
			self._tmrcView.stepsZSpinbox['state'] = 'readonly'
		else:
			self._tmrcView.stepsXSpinbox['state'] = tkinter.DISABLED
			self._tmrcView.stepsYSpinbox['state'] = tkinter.DISABLED
			self._tmrcView.stepsZSpinbox['state'] = tkinter.DISABLED
			self.model.clearSteps()

	def _stepsSpinboxCallback(self):
		# Callback used for self._tmrcView.stepsXSpinbox, self._tmrcView.stepsYSpinbox, and 
		# self._tmrcView.stepsZSpinbox

		self.model.setSteps(self._stepsXSpinboxControlVariable.get(),
							self._stepsYSpinboxControlVariable.get(),
							self._stepsZSpinboxControlVariable.get())

	def _translationTableBrowseButtonCallback(self):
		# Callback used for self._tmrcView.launchFileDialogToPickTranslationTableFileButton
		pathToTranslationTable = tkinter.filedialog.askopenfilename(parent = self._tmrcView,
			defaultextension=".ttt", multiple = False)
		if pathToTranslationTable:
			pathToTileMapFile = self.model.getPathToTileMapFile()
			if pathToTileMapFile:
				pathToTranslationTable = os.path.relpath(pathToTranslationTable, os.path.dirname(
					pathToTileMapFile))
			self.model.setPathToTranslationTable(pathToTranslationTable)

	def _translationTableEntryCallback(self):
		pass

	def _translationTypeCallback(self, tkevent):
		# Callback used for self._tmrcView.pickTranslationTypeCombobox
		self.model.setTranslationType(self._tmrcView.pickTranslationTypeCombobox.get())

	def _updateAll(self):
		# Update all widgets in self._tmrcView to reflect the contents of self._tmrcModel
		self._updateRequired()
		self._updateOptions()

	def _updateLink(self):
		# Updates the widget in self._tmrvView that represents the link TMRC option.
		self._disableLink()
		if self.model.getLink():
			self._useLinkToggleCheckbuttonControlVariable.set(1)
		else:
			self._useLinkToggleCheckbuttonControlVariable.set(0)
		self._tmrcView.useLinkToggleCheckbutton['state'] = tkinter.NORMAL

	def _updateNoDefaults(self):
		# Updates the widget in self._tmrvView that represents the nodefault TMRC option.
		self._disableNoDefaults()
		if self.model.getNoDefaults():
			self._useNoDefaultsToggleCheckbuttonControlVariable.set(1)
		else:
			self._useNoDefaultsToggleCheckbuttonControlVariable.set(0)
		self._tmrcView.useNoDefaultsToggleCheckbutton['state'] = tkinter.NORMAL

	def _updateOptions(self):
		# Updates the widgets in self._tmrcView that represent run command TMRC option.
		self._updateLink()
		self._updateNoDefaults()
		self._updateSteps()
		self._updateRemap()
		self._updateSave()

	def _updateRemap(self):
		# Updates the widgets in self._tmrcView that represent remap TMRC option.
		self._disableRemap()
		self._availableTileSets = self.model.getTileSetsUsedInTranslationTable()
		self._tmrcView.remapFromCombobox['values'] = self._availableTileSets
		self._tmrcView.remapToCombobox['values'] = self._availableTileSets
		self._tmrcView.remapFromCombobox.set('')
		self._tmrcView.remapToCombobox.set('')

		remap = self.model.getRemap()
		if remap:
			self._tmrcView.remapFromCombobox.current(self._availableTileSets.index(remap[0]))

			self._tmrcView.remapToCombobox.current(self._availableTileSets.index(remap[1]))
			self._enableRemapCheckbuttonControlVariable.set(1)
			self._tmrcView.enableRemapCheckbutton['state'] = tkinter.NORMAL
			self._tmrcView.remapFromCombobox['state'] = 'readonly'
			self._tmrcView.remapToCombobox['state'] = 'readonly'
		else:
			self._enableRemapCheckbuttonControlVariable.set(0)
			if self.model.getPathToTranslationTable():
				self._tmrcView.enableRemapCheckbutton['state'] = tkinter.NORMAL

	def _updateRequired(self):
		# Updates the widgets in self._tmrcView that represent the required TMRC options to reflect
		# the contents of self._tmrcModel.
		self._updateTileMap()
		self._updateTranslationTable()
		self._updateTranslationType()
		self._updateRunCommand()

	def _updateRunCommand(self):
		# Updates the widgets in self._tmrcView that represent run command TMRC option.
		self._disableRunCommand()
		commandLine = self.model.getCommandLine()

		self._runCommandEntryControlVariable.trace_vdelete('w',
			self._runCommandEntryCallbackIdentifier)
		self._runCommandEntryControlVariable.set('')
		self._tmrcView.standardRunCommandCombobox['values'] = self._standardRunCommandNames

		if commandLine is not None:
			self._tmrcView.currentRunCommandLabel['text'] = commandLine
			if commandLine in self._standardRunCommandLines:
				self._runCommandRadiobuttonControlVariable.set(0)
				self._tmrcView.standardRunCommandCombobox.current(
					self._standardRunCommandLines.index(commandLine))
			else:
				self._runCommandRadiobuttonControlVariable.set(1)
				self._runCommandEntryControlVariable.set(commandLine)
				self._tmrcView.customRunCommandEntry['state'] = tkinter.NORMAL

			self._tmrcView.useCustomRunCommandRadiobutton['state'] = tkinter.NORMAL
			self._tmrcView.useStandardRunCommandRadiobutton['state'] = tkinter.NORMAL
		else:
			self._runCommandRadiobuttonControlVariable.set(
				self._unselectedRunCommandRadiobuttonValue)
			self._tmrcView.useCustomRunCommandRadiobutton['state'] = 'tristate'
			self._tmrcView.useStandardRunCommandRadiobutton['state'] = 'tristate'
			self._tmrcView.currentRunCommandLabel['text'] = ''

		self.runCommandEntryCallbackIdentifier = \
			self._runCommandEntryControlVariable.trace('w', self._runCommandEntryCallback)

	def _updateSave(self):
		# Updates the widgets in self._tmrcView that represent save TMRC option.
		self._disableSave()
		pathToSave = self.model.getPathToSaveFile()

		self._saveFileEntryControlVariable.trace_vdelete('w', self._saveFileEntryCallbackIdentifier)
		self._saveFileEntryControlVariable.set('')
		if pathToSave is not None:
			self._enableSaveCheckbuttonControlVariable.set(1)
			self._saveFileEntryControlVariable.set(pathToSave)
			self._tmrcView.enableSaveToggleCheckbutton['state'] = tkinter.NORMAL
			self._tmrcView.pathToSaveFileEntry['state'] = 'readonly'
			self._tmrcView.launchFileDialogToPickSaveFileButton['state'] = tkinter.NORMAL
		else:
			self._enableSaveCheckbuttonControlVariable.set(0)
			self._tmrcView.enableSaveToggleCheckbutton['state'] = tkinter.NORMAL

		self._saveFileEntryCallbackIdentifier = self._saveFileEntryControlVariable.trace('w',
			self._saveFileEntryCallback)

	def _updateSteps(self):
		# Updates the widgets in self._tmrcView that represent steps TMRC option.
		self._disableSteps()

		steps = self.model.getSteps()
		if steps:
			self._enableStepsCheckbuttonControlVariable.set(1)
			self._stepsXSpinboxControlVariable.set(steps[0])
			self._stepsYSpinboxControlVariable.set(steps[1])
			self._stepsZSpinboxControlVariable.set(steps[2])
			self._tmrcView.stepsXSpinbox['state'] = 'readonly'
			self._tmrcView.stepsYSpinbox['state'] = 'readonly'
			self._tmrcView.stepsZSpinbox['state'] = 'readonly' 
		else:
			self._stepsXSpinboxControlVariable.set(self._defaultXStepValue)
			self._stepsYSpinboxControlVariable.set(self._defaultYStepValue)
			self._stepsZSpinboxControlVariable.set(self._defaultZStepValue)
			self._enableStepsCheckbuttonControlVariable.set(0)

		self._tmrcView.enableStepsCheckbutton['state'] = tkinter.NORMAL

	def _updateTileMap(self):
		# Updates the widgets in self._tmrcView that represent the path to tile map that   
		# whose TMRC options are being edited.
		pathToTileMapFile = self.model.getPathToTileMapFile()
		if pathToTileMapFile is not None:
			self._tmrcView.pathToTileMapLabel['text'] = pathToTileMapFile
		else:
			self._tmrcView.pathToTileMapLabel['text'] = ''

	def _updateTranslationTable(self):
		# Updates the widgets in self._tmrcView that represent the path to translation table 
		# TMRC option.
		self._disableTranslationTable()
		
		pathToTranslationTable = self.model.getPathToTranslationTable()

		self._translationTableEntryVariable.trace_vdelete('w',
			self._translationTableEntryCallbackIdentifier)
		self._translationTableEntryVariable.set('')
		
		if pathToTranslationTable:
			pathToTileMapFile = self.model.getPathToTileMapFile()
			if pathToTileMapFile:
				pathToTranslationTable = os.path.relpath(pathToTranslationTable, os.path.dirname(
					pathToTileMapFile))
			
			self.model.setPathToTranslationTable(pathToTranslationTable)
			self._translationTableEntryVariable.set(self.model.getPathToTranslationTable())
		
		self.translationTableEntryCallbackIdentifier = \
			self._translationTableEntryVariable.trace('w', self._translationTableEntryCallback)

		self._tmrcView.currentTranslationTablePathEntry['state'] = 'readonly'
		self._tmrcView.launchFileDialogToPickTranslationTableFileButton['state'] = tkinter.NORMAL

	def _updateTranslationType(self):
		# Updates the widgets in self._tmrcView that represent the path to translation type 
		# TMRC option.
		self._disableTranslationType()
		self._availableTranslationTypes = self.model.getTranslationTypesUsedInTranslationTable()
		self._tmrcView.pickTranslationTypeCombobox['values'] = self._availableTranslationTypes

		translationType = self.model.getTranslationType()
		if translationType:
			self._tmrcView.pickTranslationTypeCombobox.current(
				self._availableTranslationTypes.index(translationType))

		if self.model.getPathToTranslationTable():
			self._tmrcView.pickTranslationTypeCombobox['state'] = 'readonly'


if __name__ == '__main__':
	parser = argparse.ArgumentParser(	description = 	"A GUI utility for creating a TileMap Run "
														"Configuration file.")
	parser.add_argument('TILEMAP', 	help = 	"TILEMAP for which the TMRC file is being "
											"created/edited.",
								type = str)
	
	parser.add_argument('--dir', help = "directory to search for the TMRC options file.",
						type = str)
	parser.add_argument('--cancelerror', help = "return an error value if cancel is selected.",
						action = 'store_true', default = False)

	parser.add_argument('--setexit', help = "when set button is clicked close program after saving "
											"options.", action = 'store_true', default = False)

	args = parser.parse_args()

	defaults = {'commandLines':[('Terminal','tileplacer.py')],
				'steps':[1,1,1],
				'exitSet':args.cancelerror,
				'errorCancel':args.setexit}
	
	if args.dir:
		if not os.path.isdir(args.dir):
			print("Problem searching for TMRC file. Option --dir must specify a directory.")
		
		pathToTMRCFile = os.path.join(args.dir, os.path.basename(args.TILEMAP))
	else:
		pathToTMRCFile = args.TILEMAP

	pathToTMRCFile += '.tmrc'

	model = TMRCModel(args.TILEMAP, pathToTMRCFile)
	controller = TMRCController(model, defaults)
