#!/usr/bin/env python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.
"""
A wrapper used to run tileplacer.py using TMRC files.
"""

import argparse
import xml.etree.ElementTree
import os
import os.path
import subprocess
import shlex
import sys

def getTMRCDataFromFile(pathToTMRCFile):
	"""Returns a dictionary populated based on the contents of pathToTMRCFile"""
	try:
		tmrcFileTree = xml.etree.ElementTree.parse(pathToTMRCFile)
	except FileNotFoundError:
		return None

	tmrcRootElement = tmrcFileTree.getroot()
	tmrcData = None

	if tmrcRootElement is not None:
		translationTableElement = \
			tmrcRootElement.find('./options/option[@name="tmrc_translationtable"]')
		translationTypeElement = \
			tmrcRootElement.find('./options/option[@name="tmrc_translationtype"]') 
		envElement = tmrcRootElement.find('./options/option[@name="tmrc_env"]')
		linkElement = tmrcRootElement.find('./options/option[@name="tmrc_link"]')
		remapElement = tmrcRootElement.find('./options/option[@name="tmrc_remap"]')
		stepsElement = tmrcRootElement.find('./options/option[@name="tmrc_steps"]')
		noDefaultsElement = \
			tmrcRootElement.find('./options/option[@name="tmrc_nodefaults"]')
		saveElement = tmrcRootElement.find('./options/option[@name="tmrc_save"]')
		commandLineElement = tmrcRootElement.find('./options/option[@name="tmrc_commandline"]')

		if translationTableElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['translationtable'] = translationTableElement.text

		if translationTypeElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['translationtype'] = translationTypeElement.attrib['value']

		if envElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['env'] = envElement.attrib['value']


		if linkElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['link'] = True

		if remapElement is not None:
			tmrcData = tmrcData or {}
			remap = {}
			remap['from'] = remapElement.attrib['from']
			remap['to'] = remapElement.attrib['to']

			tmrcData['remap'] = remap

		if stepsElement is not None:
			tmrcData = tmrcData or {}
			steps = {}
			steps['x'] = stepsElement.attrib['x']
			steps['y'] = stepsElement.attrib['y']
			steps['z'] = stepsElement.attrib['z']

			tmrcData['steps'] = steps

		if noDefaultsElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['nodefaults'] = True

		if saveElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['save']  = saveElement.text

		if commandLineElement is not None:
			tmrcData = tmrcData or {}
			tmrcData['command'] = commandLineElement.text

	return tmrcData

def hasTMRCDataRequiredToRun(tmrcData):
	"""
	Returns True if tmrcData if 'command' in tmrcData and 'translationtable' in tmrcData and
	'translationtype' in tmrcData.
	"""
	if 'command' not in tmrcData:
		return False

	if 'translationtable' not in tmrcData:
		return False

	if 'translationtype' not in tmrcData:
		return False

	return True


if __name__ == "__main__":
	parser = argparse.ArgumentParser(	description = 	"")
	parser.add_argument('TILEMAP', 	help = 	"TILEMAP to translate using TMRC file.",
								type = str)

	parser.add_argument('--dir', help = "directory to search for the TMRC options file.",
						type = str)
	args = parser.parse_args()

	tmrcFileName = os.path.basename(args.TILEMAP)
	tmrcFileName += ".tmrc"

	if args.dir:
		tmrcDirName = args.dir
	else:
		tmrcDirName = os.path.dirname(args.TILEMAP) 

	tmrcFullPath = os.path.join(tmrcDirName, tmrcFileName)

	tmrcData = getTMRCDataFromFile(tmrcFullPath)

	if tmrcData is None or not hasTMRCDataRequiredToRun(tmrcData):
		if args.dir is not None:
			subprocess.call(	['createtmrc.py', args.TILEMAP, '--dir', args.dir, '--cancelerror',
								'--setexit'], env = os.environ)
		else:
			subprocess.call(	['createtmrc.py', args.TILEMAP, '--cancelerror', '--setexit'], 
								env = os.environ)

		tmrcData = getTMRCDataFromFile(tmrcFullPath)


	if tmrcData and hasTMRCDataRequiredToRun(tmrcData):
		# The command line arguments for tileplacer.py are collected in a list based on the contents
		# of tmrcData. That list is then converted into a string. The TILEPLACER_ARGS environement
		# variable is set to that string before tileplacer.py is called.
	
		unconstructedEnvironmentVariableValue = []
		unconstructedEnvironmentVariableValue.append("{}".format(shlex.quote(args.TILEMAP)))
		pathToTranslationTable = None
		if os.path.isabs(tmrcData['translationtable']):
			pathToTranslationTable = shlex.quote(tmrcData['translationtable'])
		else:
			pathToTranslationTable = tmrcData['translationtable']
			pathToTranslationTable = os.path.join(	os.path.dirname(args.TILEMAP), 
													pathToTranslationTable)
			pathToTranslationTable = os.path.normpath(pathToTranslationTable)
			pathToTranslationTable = shlex.quote(pathToTranslationTable)

			unconstructedEnvironmentVariableValue.append(
				"{}".format(pathToTranslationTable))

		unconstructedEnvironmentVariableValue.append(tmrcData['translationtype'])
		
		if 'env' in tmrcData:
			unconstructedEnvironmentVariableValue.append("--env {}".format(tmrcData['env']))

		if 'link' in tmrcData:
			unconstructedEnvironmentVariableValue.append("--link")

		if 'nodefaults' in tmrcData:
			unconstructedEnvironmentVariableValue.append("--nodefaults")

		if 'remap' in tmrcData:
			unconstructedEnvironmentVariableValue.append(
				"--remap {} {}".format(tmrcData['remap']['from'], tmrcData['remap']['to']))

		if 'save' in tmrcData:
			unconstructedEnvironmentVariableValue.append(
				"--save {}".format(shlex.quote(tmrcData['save'])))

		if 'steps' is tmrcData:
			unconstructedEnvironmentVariableValue.append(
				"--steps {} {} {}".format(	tmrcData['steps']['x'],
											tmrcData['steps']['y'],
											tmrcData['steps']['z']))

		environmentVariableValue = " ".join(unconstructedEnvironmentVariableValue)
		os.environ["TILEPLACER_ARGS"] = environmentVariableValue
		subprocess.call(tmrcData['command'], env = os.environ)
	else:
		sys.exit(1)