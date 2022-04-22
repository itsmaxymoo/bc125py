import platform
import sys
import os


def get_system_str() -> str:
	"""Get a summary string of the local machine

	Returns:
		str: Machine information
	"""

	os_info: str

	# Try to get a nice string representing the linux distro
	try:
		import distro
		os_info = distro.name(pretty=True)

	# Otherwise, use a more generic string
	except ImportError:
		os_info = platform.system() + " " + platform.release()

	# Get CPU architecture
	cpu_info: str
	if len(platform.machine()) > 0:
		cpu_info = platform.machine()
	else:
		cpu_info = "no_arch"

	# Return results
	return os_info + " -- " + cpu_info


def is_linux() -> bool:
	"""Determine if the local machine is running linux

	Returns:
		bool: True if the local machine runs linux
	"""

	return sys.platform.startswith("linux")


def is_root() -> bool:
	"""Determine if this instance of the program is being ran as root

	Returns:
		bool: True if root, otherwise False
	"""

	return os.getuid() == 0
