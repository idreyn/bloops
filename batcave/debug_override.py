class DebugOverride(object):
	def __init__(self, disable_save=False,
			disable_playback=False,
			force_enable_emitters=False,
			save_prefix=""):
		self.disable_save = disable_save
		self.disable_playback = disable_playback
		self.force_enable_emitters = force_enable_emitters
		self.save_prefix= save_prefix

	@staticmethod
	def from_dict(dict):
		return DebugOverride(
			disable_save=dict.get('disableSave'),
			disable_playback=dict.get('disablePlayback'),
			force_enable_emitters=dict.get('forceEnableEmitters'),
			save_prefix=dict.get('savePrefix')
		)