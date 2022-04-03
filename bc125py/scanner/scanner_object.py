class _ScannerObject:

	def __init__(self) -> None:
		if type(self) == _ScannerObject:
			raise NotImplementedError(type(self).__name__ + " cannot be instantiated!")
