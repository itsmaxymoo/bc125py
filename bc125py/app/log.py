import sys


_DEBUG: bool = False
_FILE = sys.stdout


def __split_print(*args, console_out_file = sys.stdout) -> None:
	"""Print message to stdout and logfile, if applicable
	"""

	print(*args, file=console_out_file)
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

	__split_print("[WARN]", *args, console_out_file=sys.stderr)


def error(*args) -> None:
	"""Log error
	"""

	__split_print("[ERROR]", *args, console_out_file=sys.stderr)
