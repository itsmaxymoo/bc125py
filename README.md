# BC125Py

A Python-based interface for the Uniden BC125AT radio scanner.

This project aims to be a Linux replacement for the Windows-only
Uniden software for the BC125AT. Presently, BC125Py only has a
command line interface, but a GUI is planned. Rest assured, the
CLI is not hard to use at all! View the [changelog here](CHANGELOG.md).


# Installation

`sudo pip install bc125py`

*It is recommended to install bc125py as root.*


# Quick Start

All commands **must be ran as root**.

Plug the BC125AT into your computer, and power the device on.

### Import scanner channels

`sudo bc125py import --csv channels.csv`

Then, edit the CSV file in a spreadsheet editor!

**Note:** Depending on your CSV editor, the channels may be offset by 1 or 2  
**Note:** All 500 channels are together. Bank 1 starts at 1 or 2, bank 2 starts at 51 or 52, etc...  
**Note:** omitting the `--csv` flag will import all channels  
**and** settings, and use the **json** file format.

### Export channels to scanner

`sudo bc125py export --csv channels.csv`

**Note:** omitting the `--csv` flag will export all channels
**and** settings, and use the **json** file format.

### Launch scanner shell

`sudo bc125py shell`

The shell allows you to send commands directly to the device.
The `shell` subcommand accepts a script filename as an optional parameter.
Specifying `-` as the input script will tell the shell to read from stdin.

The shell remembers its history by default. This can be cleared by deleting
`~/.bc125py_history` (but usually for the root user), or by running the shell
subcommand with the `-c` or `--clear-history` flags.

### Factory reset the scanner

`sudo bc125py wipe`

This will **erase all channels** and reset all settings.


# More Usage

The following are top level flags, to be use after the
`bc125py` but before the subcommand.

| Flag | Usage |
| --- | --- |
| `-v` | Enable debug messages |
| `-l`, `--log` LOG | Additionally print all debug messages to LOG_FILE |
| `-p`, `--port` PORT | Force BC125Py to use port (device file) PORT |
| `--legacy-detect` | Use the legacy automatic port detection method. Try this if BC125Py does not initially detect your scanner. This may produce duplicate results |

### import/export and `--csv`

By default, import and export will process all of the scanner's channels
and settings, and work with json files. The `--csv` flag tells these
command to process channels only, and work with csv files.

### Shell Scripts

The `shell` subcommand accepts an optional parameter for an input file,
to be processed as a script. Run `help` once inside the shell to learn
more. The recommended extension for these scripts is `.125at`; see
the [docs directory](docs/) for examples.

### TLP

TLP, a power management tool on some laptops,
may interfere with the operation of BC125Py.
To use BC125Py on a TLP-enabled laptop, follow
[this guide](https://askubuntu.com/questions/1239176/how-to-disable-tlp)
to disable it. This is easily reversible afterwards.
If you are aware of a better way to work around TLP, please fork and submit a PR!

### stdin/stdout

The import, export, and shell subcommands may accept a single dash
( `-` ) as a filename to use stdin/stdout. In this mode, the `import`
subcommand will write to stdout. `export` and `shell` will read from stdin.


# Contributing

* The module `bc125py`, excluding `app`, should only contain library (non-executable) code.
* `sdo.py` shall be for all scanner-data abstraction classes.
* The `app` module shall be for all executable code.
* `app/cli.py` shall be the CLI portion of the program.
* `app/core.py` shall be all common functions for the executable portion of the program, both CLI and GUI.
* `app/log.py` shall be the logger. **Use the logger wherever possible!**

The 'main' branch shall be the most up-to-date version of the project. Once the main branch reaches
stability, the version number will be incremented, a release will be generated, and a 'release-x.x.x'
branch will be created to preserve the repository at its state.
