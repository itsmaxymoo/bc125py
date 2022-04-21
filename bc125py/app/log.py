import sys


_DEBUG: bool = False
_FILE = sys.stdout


def debug(*args) -> None:
	if _DEBUG:
		print("[DEBUG]", *args)
		if _FILE != sys.stdout:
			print("[DEBUG]", *args, file=_FILE)


def warn(*args) -> None:
	print("[WARN]", *args)
	if _FILE != sys.stdout:
		print("[WARN]", *args, file=_FILE)
