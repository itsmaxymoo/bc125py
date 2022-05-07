# bc125py Contributor Documentation

This documentation is intended for those who are contributing
to bc125py's source, **not** those who are using the api, cli, or gui.

This document will set forth guidelines and design methodologies
for most source files.

Tabs will be used, as opposed to spaces, for all files.


## sdo.py

This module shall contain all class definitions for the virtual scanner model.
SDO is short for *Scanner Data Object*; as such, all SDO's should inherit the
abstract class `_ScannerDataObject`, and implement at least one of its functions.
A scanner data object represents a unique piece of data associated with one
bc125at command.

SDO's should only implement the functions in `_ScannerDataObject`, and not define any
new **public** ones. The overall behavior from one SDO to another should not change.
Cloning the `_E` class (example SDO) is a good starting point.

For style's sake, all SDO's should adapt the docstring in `_E`, and maintain the
order of functions seen in `_E` and `_ScannerDataObject`.

An SDO implementing a function may not modify the function's signature.
Any public attribute of an SDO must be an attribute of that scanner setting.

If an SDO implements `to_fetch_command`, it should also implement
`from_command_response`. Likewise, `to_dict` and `from_dict` come in pairs.
SDO's which represent a write-only command, with no data associated with it
(e.g: CLR, DCH, etc...), should only implement `to_write_command`.
SDO's which represent a read-only command (e.g: MDL, VER) should only implement
`to_fetch_command`, `from_command_response`, `to_dict`, and `from_dict`.
