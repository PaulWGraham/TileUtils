# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

"""
Plugin module.

Together TileUtils.Plugin.Plugable() and TileUtils.Plugin.Plugin() form a lightweight plugin 
framework used extensively by TileUtils.
	As their names suggest Plugable() and Plugin() declare the required interfaces for objects that 
use plugins and objects that are plugins respectively.

The responsibilities of Plugable() are:

1. Manage the registration of Plugin() objects.
2. Store are retrieve Plugin() objects.
3. Raise errors if something goes wrong while handling responsibilities one and/or two.

Plugin() objects are registered with a Plugable() object with a call to the Plugable() objects
registerPlugin() method.
	 The registerPlugin() method takes as it parameters the Plugin() object to be registered and a
plugin path. A plugin path is nothing more than a list of strings. Similar in function to a filepath
used by a filesystem, when taken together the list strings in a plugin path define a unique point in
a namespace.
	If the Plugin() object is successfully registered a reference to it is stored in the Plugable()
object. An immediate call to Plugable() object's queryPlugin() method with the plugin path that was 
used to register the Plugin() object as a parameter will return True.
	If an attempt is made to register a Plugin() object with a plugin path that has already been
used to register a Plugin() object several things can happen: the old plugin remains and the new 
plugin is discarded; the old plugin is discarded (clobbered) and the a reference to the new plugin 
is kept; the old plugin remains, the new plugin is discarded, and an error is raised by the
Plugable() object or; the old plugin is discarded, a reference to the new plugin is kept, and an
error is raised by the Plugable() object. Which of these scenarios occurs depends on how the
Plugin() objects in question were implemented.

Plugin() declares several methods that influence how a Plugable() object behaves when
registering and/or retrieving a Plugin() object. Those Plugin() methods are:


clobber(self) -

This method returns True if the Plugin() object is to, if possible, replace another Plugin() object
if a plugin path collision occurs when being registered with a Plugable() object.


clobberable(self) -

This method returns True if the Plugin() object is capable of being replaced by another Plugin()
object if a plugin path collision occurs when being registered with a Plugable() object.


preRegistrationCheck(self, caller) -

This method is called before any other Plugin() method by the Plugable() object during the plugin
registration process. If this method returns False then the Plugin() object is not registered and it
doesn't clobber another Plugin() object.


The following Plugin() methods determine if and when a Plugable() object raises errors:


errorIfClobber(self) -

The Plugable() object raises an error if this method returns True and the Plugin() object clobbers
another when it is registered.


errorIfClobbered(self) -

The Plugable() object raises an error if this method returns True and the Plugin() object was
clobbered.


errorIfPreRegistrationCheckFails(self)  -

The Plugable() object raises an error if this method returns True and the Plugin() object method
preRegistrationCheck() returned false.


errorIfNotRegistered(self) -

The Plugable() object raises an error if this method returns True and the Plugin() object fails to
be registered for any reason.


requireFullPath(self) -

If this method returns True and the Plugin() object that defines this method is returned from a call
to the Plugable() objects getPlugin() method and there is a subpath of the plugin path used to
register the Plugin() object that doesn't refer to a registered Plugin() object then the Plugable()
object raises an error.
"""


class DebugPlugin():
	def clobber(self):
		return True

	def clobberable(self):
		return True

	def preRegistrationCheck(self):
		return True

	def errorIfClobber(self):
		return False

	def errorIfClobbered(self):
		return False

	def errorIfPreRegistrationCheckFails(self):
		return False

	def errorIfNotRegistered(self):
		return False

	def name(self):
		return "debug"

	def requireFullPath(self):
		return False

class Plugable():
	"""Declares the required interfaces for objects that use plugins."""
	def __init__(self):
		self._plugins = {}

	def _getPlugin(self, path):
		if path[0] in self._plugins:
			return self._plugins[path[0]].getPlugin(path[1:])

		return None, False

	def _setPlugin(self, plugin, path):
		if path[0] not in self._plugins:
			self._plugins[path[0]] = PluginPathLevel()

		self._plugins[path[0]].setPlugin(plugin, path[1:])


	def registerPlugin(self, newPlugin, path):
		"""Register and store a plugin. Raising RuntimeError as needed."""
		registered = True
		if newPlugin.preRegistrationCheck(self):
			existingPlugin = self._getPlugin(path)[0]
			if existingPlugin:
				if newPlugin.clobber():
					if existingPlugin.clobberable():
						self._setPlugin(newPlugin, path)
						if newPlugin.errorIfClobber():
							raise RuntimeError("Plugin {} clobbered plugin {}.".format(
																				newPlugin.name,
																				existingPlugin.name
																				))

						if existingPlugin.errorIfClobbered():
							raise RuntimeError("Plugin {} was clobbered.".format(existingPlugin))
					else:
						registered = False
			else:
				self._setPlugin(newPlugin, path)
		else:
			if newPlugin.errorIfPreRegistrationCheckFails():
				raise RuntimeError(
							"Preregistration check failed for plugin: {}".format(newPlugin.name()))
			registered = False

		if newPlugin.errorIfNotRegistered() and not registered:
			raise RuntimeError("Plugin {} not registered.".format(newPlugin.name()))

		return registered

	def queryPlugin(self, path):
		"""Return True if a plugin can be accessed at the specified path."""
		return self._getPlugin(path)[0] is not None 

	def getPlugin(self, path):
		"""Return plugin, if any, stored at specified path. RuntimeError as needed."""
		plugin, completePath = self._getPlugin(path)
		if plugin is not None:
			if plugin.requireFullPath() and not completePath:
				raise RuntimeError("Full path required for plugin {}.".format(plugin.name()))

		return plugin, completePath

class Plugin():
	"""Declares the required interfaces for objects that are plugins."""
	def clobber(self):
		"""
		This method returns True if the Plugin() object is to, if possible, replace another Plugin()
		object if a plugin path collision occurs when being registered with a Plugable() object.
		"""
		pass

	def clobberable(self):
		"""
		This method returns True if the Plugin() object is capable of being replaced by another
		Plugin() object if a plugin path collision occurs when being registered with a Plugable()
		object.
		"""
		pass

	def preRegistrationCheck(self, caller):
		"""
		If this method returns False then the Plugin() object is not registered and it doesn't
		clobber another Plugin() object.
		"""
		pass

	def errorIfClobber(self):
		"""
		The Plugable() object raises an error if this method returns True and the Plugin() object
		was clobbered.
		"""
		pass

	def errorIfClobbered(self):
		"""
		The Plugable() object raises an error if this method returns True and the Plugin() object
		was clobbered.
		"""
		pass

	def errorIfPreRegistrationCheckFails(self):
		"""
		The Plugable() object raises an error if this method returns True and the Plugin() object
		method preRegistrationCheck() returned false.
		"""
		pass

	def errorIfNotRegistered(self):
		"""
		The Plugable() object raises an error if this method returns True and the Plugin() object
		fails to be registered for any reason.
		"""
		pass

	def name(self):
		pass

	def requireFullPath(self):
		"""
		If this method returns True and the Plugin() object that defines this method is returned
		from a call to the Plugable() objects getPlugin() method and there is a subpath of the
		plugin path used to register the Plugin() object that doesn't refer to a registered Plugin()
		object then the Plugable() object raises an error.
		"""
		pass

class PluginPathLevel():
	"""Class for storing plugins using a path."""
	def __init__(self):
		self._plugin = None
		self._plugins = {}

	def setPlugin(self, plugin, path):
		if path == []:
			self._plugin = plugin
		else:
			if path[0] not in self._plugins:
				self._plugins[path[0]] = PluginPathLevel()

			self._plugins[path[0]].setPlugin(plugin, path[1:])

	def getPlugin(self, path, completePath = True):
		if path == []:
			return self._plugin, completePath

		if self._plugin is None:
			completePath = False

		if path[0] not in self._plugins:
			completePath = False
			return None, completePath

		return self._plugins[path[0]].getPlugin(path[1:], completePath)

class StandardPlugin(Plugin):
	def clobber(self):
		return True

	def clobberable(self):
		return True

	def preRegistrationCheck(self, caller):
		return True

	def errorIfClobber(self):
		return True

	def errorIfClobbered(self):
		return True

	def errorIfPreRegistrationCheckFails(self):
		return True

	def errorIfNotRegistered(self):
		return True

	def name(self):
		raise NotImplementedError("This method is required.")

	def requireFullPath(self):
		return True