import platform
import sys
import os
import shutil
import subprocess
from bc125py.con import *
from bc125py.app import log


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


def detect_tlp() -> bool:
	"""Determines if TLP is active. TLP can interfere with scanner communication.
	THIS MAY NOT BE 100% ACCURATE!!!

	Returns:
		bool: True if tlp detected & enabled.
	"""

	if tlp_bin := shutil.which("tlp-stat"):
		log.debug("core: detected TLP")

		try:
			# See if TLP is actually enabled, warn if true
			if "TLP_ENABLE=\"1\"" in subprocess.check_output([tlp_bin, "-c"], stderr=subprocess.DEVNULL).decode():
				log.warn("TLP is enabled. This may block scanner connection")

				return True
		except Exception:
			log.debug("core: could not determine if TLP is active")
	
	return False


def get_scanner_connection(port: str = None) -> ScannerConnection:
	"""Find and connect to the scanner

	Args:
		port (str, optional): The port to connect to
		simulate (bool, optional): Whether this should create a simulated connection.

	Raises:
		ConnectionError: if connecting to the scanner failed

	Returns:
		bc125py.con.ScannerConnection: The active connection
	"""

	log.debug("core: attempting to find scanner & connect")

	# Check to see if TLP (power management tool) is enabled
	# TLP can interfere with the BC125AT connection
	detect_tlp()

	con: ScannerConnection
	con = ScannerConnection()
	con.connect(port)

	return con
