# Release History

## 0.10.1

* Deprecate `bc125py.sdo.is_valid_ctcss(int)`
* Implement human readable CTCSS/DCS tones (thanks to [Bradley A. Thornton](https://github.com/cidrblock))
	* Please note that the old index-based tones still work
* Added the `--help-tones` flag which lists all valid CTCSS/DCS/Special tones
* Updated examples
* Added the new `unlock` command to free scanner stuck in program mode after a connection error
* Add "validate" command line option for save files
* Various small bugfixes
* Add pytest support

## 0.9.10

* The shell now remembers command history (thanks to [Brad Town](https://github.com/townba)).
* You can clear the shell's command history with the `-c` or `--clear-history` flags.

## 0.9.9

* Fixed a bug where an empty channel name did not reset the channel name on the device (thanks to [Brad Town](https://github.com/townba))
* Help page displays program version by default

## 0.9.8

* Improved shell documentation

## 0.9.7

* Improved documentation
* stdout support for import subcommand
* stdin support for export and shell subcommand
* Fixed AttributeError when CommandError is raised
* Fixed cdc_acm driver not being setup when searching for ports

## 0.9.6

* First public release