import platform
import sys


def get_system_str() -> str:

	os_info: str
	try:
		import distro
		os_info = distro.name(pretty=True)
	except ImportError:
		os_info = platform.system() + " " + platform.release()

	cpu_info: str
	if platform.processor():
		cpu_info = platform.processor()
	else:
		cpu_info = "no_cpu"
	cpu_info += ", "
	if platform.machine():
		cpu_info += platform.machine()
	else:
		cpu_info += "no_arch"

	return os_info + " -- " + cpu_info


def is_linux() -> bool:
	return sys.platform.startswith("linux")
