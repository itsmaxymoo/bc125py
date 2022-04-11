class _ScannerDataObject:

	def __init__(self) -> None:
		if type(self) == _ScannerDataObject:
			raise NotImplementedError(type(self).__name__ + " cannot be instantiated directly (abstract)")


	def set(self, *args, **kwargs) -> None:
		raise NotImplementedError(type(self).__name__ + " must implement set()")


	def get(self):
		raise NotImplementedError(type(self).__name__ + " must implement get()")


	def to_get_command(self, *args, **kwargs) -> str:
		raise NotImplementedError(type(self).__name__ + " must implement to_get_command()")


	def to_write_command(self) -> str:
		raise NotImplementedError(type(self).__name__ + " must implement to_write_command()")
	

	def import_from_command_response(self, command_response: tuple) -> None:
		raise NotImplementedError(type(self).__name__ + " must implement import_from_command_response()")


	def to_save_file_format(self) -> str:
		raise NotImplementedError(type(self).__name__ + " must implement to_save_file_format()")


	def import_from_save_file_format(self, in_text: str) -> None:
		raise NotImplementedError(type(self).__name__ + " must implement import_from_save_file_format()")
