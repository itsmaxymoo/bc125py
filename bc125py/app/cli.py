import os
import sys
import argparse
import datetime
from termios import CRTSCTS
import bc125py
from bc125py.app import core, log
from bc125py import sdo


# Manual port override to be used by cli commands
_port: str = None


# Program entrypoint
def main() -> int:

	# --- Command Line Arguments ---
	# Create main cli parser
	main_parser = argparse.ArgumentParser(prog=bc125py.MODULE_NAME, description=bc125py.MODULE_DESCRIPTION)

	# Add universal cli arguments
	main_parser.add_argument(
		"-v",
		"--verbose",
		action="store_true",
		help="verbose mode"
	)
	main_parser.add_argument(
		"-l",
		"--log",
		help="additionally log debug statements to the specified file. use in conjunction with verbose mode"
	)
	main_parser.add_argument(
		"--version",
		action="version",
		version=bc125py.MODULE_VERSION
	)
	main_parser.add_argument(
		"-p",
		"--port",
		help="force " + bc125py.MODULE_NAME + " to use the specified device port"
	)

	# Add subcommands
	sub_parsers = main_parser.add_subparsers(dest="command", required=True, help="command")

	# Subcommand test
	test_parser = sub_parsers.add_parser("test", help="test scanner connection")

	# Subcommand import/read
	import_parser = sub_parsers.add_parser("import", help="read data from scanner, output to file")
	import_parser.add_argument("file", help="output file")
	import_parser.add_argument(
		"-c",
		"--csv",
		action="store_true",
		help="import channels ONLY, and write as CSV"
	)

	# Subcommand export/write
	export_parser = sub_parsers.add_parser("export", help="write data from file to scanner")
	export_parser.add_argument("file", help="input file")
	export_parser.add_argument(
		"-c",
		"--csv",
		action="store_true",
		help="export and write channels CSV file"
	)
	export_parser.add_argument(
		"-s",
		"--simulate",
		action="store_true",
		help="simulate scanner write operation. MUST specify output file with --port"
	)

	# Subcommand shell
	shell_parser = sub_parsers.add_parser("shell", help="launch interactive scanner shell")
	shell_parser.add_argument("file", help="commands file to execute", nargs="?", default=None)

	# Parse arguments
	cli_args = main_parser.parse_args()

	# --- END Command Line Arguments ---
	
	# Set verbosity level
	log._DEBUG = cli_args.verbose

	# Set up logging
	if cli_args.log:
		log._FILE = open(cli_args.log, "w")
	log.debug(bc125py.MODULE_NAME, "version", bc125py.MODULE_VERSION + ", started on", datetime.datetime.now())
	log.debug("sysinfo:", core.get_system_str())
	if not core.is_linux():
		log.warn("Your system is unsupported!")

	# Set port, if specified
	if cli_args.port:
		global _port
		_port = cli_args.port
	
	# If simulate, make sure there is a port
	if hasattr(cli_args, "simulate"):
		if cli_args.simulate and not cli_args.port:
			log.error("use of --simulate requires --port")
			return 1

	# Dispatch subcommand
	cmd = cli_args.command
	if cmd == "test":
		return test()
	elif cmd == "import":
		return import_read(cli_args.file, cli_args.csv)
	elif cmd == "export":
		return export_write(cli_args.file, cli_args.csv, simulate=cli_args.simulate)
	elif cmd == "shell":
		return shell(cmd_file_path=cli_args.file)

	# If this part of the code was reached, something went wrong with argparse
	log.error("ERRoneous subc:", cli_args.command)

	return 1


# Make sure we are root function
def enforce_root() -> None:
	if not core.is_root():
		print(bc125py.MODULE_NAME, "must be ran as superuser (root) to perform this function.")
		sys.exit(126)
	
	log.debug("root permissions found")


# Test command
def test() -> int:
	log.debug("subc: test")

	enforce_root()

	try:
		# Connect, try to get device model
		con = core.get_scanner_connection(_port)
		print("Scanner model:", con.exec("MDL", return_tuple=False), "(success)")
		con.close()

		return 0

	except (ConnectionError, bc125py.CommandError) as e:
		log.error(str(e))
		return 1


# Import/Read command
def import_read(out_file: str, csv: bool) -> int:
	log.debug(
		"subc: import/read",
		"file:",
		out_file,
		"csv:", csv
	)

	enforce_root()

	try:

		# Connect to scanner
		scanner_con = core.get_scanner_connection(_port)

		# Read from scanner
		print("Reading from scanner...")
		log.debug("Attempting full scanner read")
		scanner: sdo.Scanner = sdo.Scanner()
		scanner.read_from(scanner_con)
		print("done")

		# Open output file
		log.debug("import: creating output file")
		fout = open(out_file, "w")

		if not csv:

			# Import json
			import json

			log.debug("full import: writing to json")

			fout.write(json.dumps(scanner.to_dict(), indent="\t", sort_keys=False))

		else:

			# CSV (channel only) import
			import csv

			log.debug("csv import: writing csv")
			# create CSV writer
			csv_writer = csv.writer(fout, dialect="excel")

			# Create CSV header
			csv_writer.writerow(
				["Index", "Name", "Frequency (MHz)", "Modulation", "CTCSS", "Delay (sec)", "Lockout", "Priority"]
			)

			# Loop through write channel info
			c: sdo.Channel
			for c in scanner.channels:
				c_dict = c.to_dict()

				log.debug("csv cin", c_dict)

				csv_writer.writerow(
					[
						c_dict["index"],
						c_dict["name"],
						c_dict["frequency"],
						c_dict["modulation"],
						c_dict["ctcss"],
						c_dict["delay"],
						c_dict["locked_out"],
						c_dict["priority"]
					]
				)
			del c

			log.debug("wrote csv")
		
		# Close output file
		fout.close()

		# Close scanner connection
		scanner_con.close()

		return 0

	except Exception as e:
		log.error(str(e))
		return 1


# Export/Write command
def export_write(in_file: str, csv: bool, simulate: bool = False) -> int:
	log.debug(
		"subc: export/write",
		"file:",
		in_file,
		"csv:", csv,
		"simulate:", simulate
	)

	if not simulate:
		enforce_root()
	

	return 0


# Shell command
def shell(cmd_file_path: str = None) -> int:
	log.debug("subc: shell")

	enforce_root()

	try:
		# Connect
		con = core.get_scanner_connection(_port)

		# Print header
		print(bc125py.MODULE_NAME, bc125py.MODULE_VERSION, "scanner shell")
		print("try commands \"help\" or \"exit\"", os.linesep)

		# User controllable variables
		shell_echo = True
		shell_allow_error = True

		# Function for processing input/commands
		def process_input(input_str: str) -> None:

			nonlocal shell_echo
			nonlocal shell_allow_error

			# case: help
			if input_str == "help":
				print("help           show this text")
				print("exit           exit the shell")
				print("echo on        show command name in response (default)")
				print("echo off       do not include command name in response")
				print("error on       crash program on command error")
				print("error off      do not crash on command error (default)")
				print("print <text>   print all text after \"print\"")
				print("# <text>       mark line as comment. line will be ignored")
			
			# case: exit, blank line, or comment
			elif not input_str or input_str == "exit" or input_str.startswith("#"):
				pass

			# case: print <text>
			elif input_str.startswith("print ") or input_str == "print":
				print(input_str[6:])
			
			# case: echo on
			elif input_str == "echo on":
				shell_echo = True
			
			# case: echo off
			elif input_str == "echo off":
				shell_echo = False
			
			# case: error on
			elif input_str == "error on":
				shell_allow_error = False
			
			# case: error off
			elif input_str == "error off":
				shell_allow_error = True

			# case: Input is not a special command; send input to scanner
			else:
				# Execute command, print result
				print(con.exec(input_str, echo=shell_echo, return_tuple=False, allow_error=shell_allow_error))

		# Determine method of input (file or interactive)
		
		# If we're reading from a command file
		if cmd_file_path:
			log.debug("subc: shell: commands file mode:", cmd_file_path)

			# Open file and read
			in_file = open(cmd_file_path, "r")
			for line in in_file.readlines():
				# Process each line
				process_input(line.lstrip().rstrip())

			in_file.close()


		# Else, interactive mode
		else:
			log.debug("subc: shell: interactive mode")

			# Input loop, stop if last command was "exit"
			in_line: str = ""
			while in_line != "exit":
				# Get user input
				in_line = input("> ").lstrip().rstrip()
			
				# Process input
				process_input(in_line)
			
		# Close scanner connection
		con.close()

		return 0

	except Exception as e:
		log.error(str(e))
		return 1
