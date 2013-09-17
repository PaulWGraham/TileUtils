#!/usr/bin/env python3
# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.
"""
A wrapper used to run tileplacer.py.
"""

import argparse
import os
import subprocess
import shlex

if __name__ == "__main__":
	parser = argparse.ArgumentParser(	description = 	"Export then Run tileplacer.py. "
														"Sets the TILEPLACER_ARGS environment "
														"variable then runs tileplacer.py using "
														"the command specified.")
	parser.add_argument('commandwithargs', help = 	"the command line used to run tileplacer.py "
													"after after the environment variable is set.",
													type = str)
	parser.add_argument('tilemap', help = "location of .tmx tilemap.", type = str)
	parser.add_argument('translationtable', help = "location of .ttt translation table.",
						 type = str)
	parser.add_argument('translationtype', help = "type of translation to use.", type = str)
	parser.add_argument('--env', help = "the environment tileplacer.py is running in.", type = str)
	parser.add_argument('--link', help =	"link translations into new tilemap instead of copying,"
											" if possible.", action = 'store_true')
	parser.add_argument('--nodefaults', help = "don't use default translations for tiles.", 
						action = 'store_true')
	parser.add_argument('--remap', help = "remap tileset translation.", nargs = 2,
						default = [None, None], type = str)
	parser.add_argument('--save', help = "file to save generated tilemap to.")
	parser.add_argument('--steps', help = "values that affect placement of generated tiles.",
						nargs = 3, type = int)
	args = parser.parse_args()

	unconstructedEnvironmentVariableValue = []
	unconstructedEnvironmentVariableValue.append("{}".format(shlex.quote(args.tilemap)))
	unconstructedEnvironmentVariableValue.append("{}".format(shlex.quote(args.translationtable)))
	unconstructedEnvironmentVariableValue.append(args.translationtype)
	
	if args.env is not None:
		unconstructedEnvironmentVariableValue.append("--env {}".format(args.env))

	if args.link is not None:
		unconstructedEnvironmentVariableValue.append("--link")

	if args.nodefaults is not None:
		unconstructedEnvironmentVariableValue.append("--nodefaults")

	if args.remap != [None, None]:
		unconstructedEnvironmentVariableValue.append("--remap {} {}".format(*args.remap))

	if args.save is not None:
		unconstructedEnvironmentVariableValue.append("--save {}".format(shlex.quote(args.save)))

	if args.steps is not None:
		unconstructedEnvironmentVariableValue.append("--steps {} {} {}".format(*args.steps))

	environmentVariableValue = " ".join(unconstructedEnvironmentVariableValue)
	os.environ["TILEPLACER_ARGS"] = environmentVariableValue

	subprocess.call(args.commandwithargs, shell = True, env = os.environ)