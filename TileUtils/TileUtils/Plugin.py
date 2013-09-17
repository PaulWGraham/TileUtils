# Copyright (c) 2013 Paul Graham 
# See LICENSE for details.

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
		return self._getPlugin(path)[0] is not None 

	def getPlugin(self, path):
		plugin, completePath = self._getPlugin(path)
		if plugin is not None:
			if plugin.requireFullPath() and not completePath:
				raise RuntimeError("Full path required for plugin {}.".format(plugin.name()))

		return plugin, completePath

class Plugin():
	def clobber(self):
		pass

	def clobberable(self):
		pass

	def preRegistrationCheck(self, caller):
		pass

	def errorIfClobber(self):
		pass

	def errorIfClobbered(self):
		pass

	def errorIfPreRegistrationCheckFails(self):
		pass

	def errorIfNotRegistered(self):
		pass

	def name(self):
		pass

	def requireFullPath(self):
		pass

class PluginPathLevel():
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