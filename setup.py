from setuptools import setup
import bc125py

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name = bc125py.MODULE_NAME,
	version = bc125py.MODULE_VERSION,
	packages = [bc125py.MODULE_NAME],
	url = bc125py.MODULE_URL,
	license = "MIT License",
	author = bc125py.MODULE_AUTHOR,
	author_email = bc125py.MODULE_AUTHOR_EMAIL,
	description = bc125py.MODULE_DESCRIPTION,
	long_description = long_description,
	long_description_content_type = "text/markdown",
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: POSIX :: Linux",
	],
	install_requires = [
		"pyserial>=3,<4"
	],
	python_requires = ">=3.7"
)
