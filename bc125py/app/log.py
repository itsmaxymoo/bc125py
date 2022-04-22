import sys


_DEBUG: bool = False
_FILE = sys.stdout


def __split_print(*args) -> None:
	"""Print message to stdout and logfile, if applicable
	"""

	print(*args)
	if _FILE != sys.stdout:
		print(*args, file=_FILE)


def debug(*args) -> None:
	"""Log debug message
	"""

	if _DEBUG:
		__split_print("[DEBUG]", *args)


def warn(*args) -> None:
	"""Log warning
	"""

	__split_print("[WARN]", *args)
