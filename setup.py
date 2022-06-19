import setuptools
from bc125py import *

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name=PACKAGE_NAME,
	version=PACKAGE_VERSION,
	author=PACKAGE_AUTHOR,
	author_email=PACKAGE_AUTHOR_EMAIL,
	license="MIT License",
	description=PACKAGE_DESCRIPTION,
	long_description=long_description,
	long_description_content_type="text/markdown",
	url=PACKAGE_URL,
	project_urls={
		"Bug Tracker": PACKAGE_URL + "/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Topic :: Communications :: Ham Radio",
		"License :: OSI Approved :: MIT License",
		"Development Status :: 4 - Beta",
		"Operating System :: POSIX :: Linux",
	],
	package_dir={PACKAGE_NAME: PACKAGE_NAME},
	packages=setuptools.find_packages(),
	entry_points={
		"console_scripts":[
			PACKAGE_NAME + "=" + PACKAGE_NAME + ".__main__:main"
		]
	},
	python_requires=">=3.7",
	install_requires = [
		"pyserial >= 3.0, < 4.0"
	],
)
