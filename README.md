# BC125Py

A Python-based interface for the Uniden BC125AT radio scanner.

This project aims to be a Linux replacement for the Windows-only
Uniden software for the BC125AT. Presently, BC125Py only has a
command line interface, but a GUI is planned. Rest assured, the
CLI is not hard to use at all!

# Installation

`pip install bc125py`

# Usage

BC125Py is used via subcommands.
Invoke them with `bc125py <command>`.

## `test`

Verify connection to the scanner.

## `import --csv <file>`

Import all data and settings from the connected scanner.
Output the data to the specified `file`.
The `--csv` flag will import programmed channels only,
and output them to a formatted csv file.
**It is currently recommended to use the csv flag.**

## `export --csv <file>`

Export the scanner data at `file` and write it to the
connected scanner. The `--csv` flag tells BC125Py that
the input file is a channel csv file.
**It is currently recommended to use the csv flag.**

## `shell`

Open a shell with the connected scanner.
**This is for advanced users only!**
Accepts an optional argument for a script file to run.
Example scripts are in the `docs/` directory.

## `wipe`

Performs a factory reset on the connected scanner.
