class _ScannerObject:

	def __init__(self) -> None:
		if type(self) == _ScannerObject:
			raise NotImplementedError(type(self).__name__ + " cannot be instantiated")


	def to_scanner(self) -> str:
		raise NotImplementedError(type(self).__name__ + " must implement to_scanner()")


	def from_scanner(self, in_data: str) -> None:
		raise NotImplementedError(type(self).__name__ + " must implement from_scanner()")


	def to_string(self) -> str:
		raise NotImplementedError(type(self).__name__ + " must implement to_string()")


	def from_string(self, in_string: str) -> None:
		raise NotImplementedError(type(self).__name__ + " must implement from_string()")
