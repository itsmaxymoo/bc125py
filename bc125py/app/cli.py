import os
import sys
import argparse
import datetime
import bc125py
from bc125py.app import core, log


# Program entrypoint
def main() -> int:

	# --- Command Line Arguments ---
	# Create main cli parser
	main_parser = argparse.ArgumentParser(prog=bc125py.MODULE_NAME, description=bc125py.MODULE_DESCRIPTION)

	# Add universal cli arguments
	main_parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
	main_parser.add_argument("-l", "--log", help="additionally log debug statements to the specified file. use in conjunction with verbose mode")
	main_parser.add_argument("--version", action="version", version=bc125py.MODULE_VERSION)

	# Add subcommands
	sub_parsers = main_parser.add_subparsers(dest="command", required=True, help="command")

	# Subcommand test
	test_parser = sub_parsers.add_parser("test", help="test scanner connection")

	# Subcommand read
	read_parser = sub_parsers.add_parser("read", help="read data from scanner, output to file")
	read_parser.add_argument("file", help="output file")

	# Subcommand write
	write_parser = sub_parsers.add_parser("write", help="write data from file to scanner")
	write_parser.add_argument("file", help="input file")

	# Subcommand shell
	shell_parser = sub_parsers.add_parser("shell", help="launch interactive scanner shell")

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

	# Dispatch subcommand
	cmd = cli_args.command
	if cmd == "test":
		return test()
	elif cmd == "read":
		return read(cli_args.file)
	elif cmd == "write":
		return write(cli_args.file)
	elif cmd == "shell":
		return shell()

	# If this part of the code was reached, something went wrong with argparse
	log.debug("ERRoneous subc:", cli_args.command)
	print("Invalid subcommand")

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
		con = core.get_scanner_connection()
		print("Scanner model:", con.exec("MDL", return_tuple=False), "(success)")
		con.close()

		return 0

	except (ConnectionError, bc125py.CommandError) as e:
		log.error(str(e))
		return 1


# Read command
def read(out_file: str) -> int:
	log.debug("subc: read", out_file)
	return 0


# Write command
def write(in_file: str) -> int:
	log.debug("subc: write", in_file)
	return 0


# Shell command
def shell() -> int:
	log.debug("subc: shell")

	enforce_root()

	try:
		# Connect
		con = core.get_scanner_connection()

		# Print header
		print(bc125py.MODULE_NAME, bc125py.MODULE_VERSION, "scanner shell")
		print("try commands \"help\" or \"exit\"", os.linesep)

		# User controllable variables
		shell_echo = True
		shell_allow_error = True

		# Function for processing input/commands
		def process_input(input: str) -> None:

			nonlocal shell_echo
			nonlocal shell_allow_error

			# case: help
			if input == "help":
				print("help           show this text")
				print("exit           exit the shell")
				print("echo on        show command name in response (default)")
				print("echo off       do not include command name in response")
				print("error on       crash program on command error")
				print("error off      do not crash on command error (default)")
				print("print <text>   print all text after \"print\"")
				print("# <text>       mark line as comment. line will be ignored")
			
			# case: exit, blank line, or comment
			elif not input or input == "exit" or input.startswith("#"):
				pass

			# case: print <text>
			elif input.startswith("print ") or input == "print":
				print(input[6:])
			
			# case: echo on
			elif input == "echo on":
				shell_echo = True
			
			# case: echo off
			elif input == "echo off":
				shell_echo = False
			
			# case: error on
			elif input == "error on":
				shell_allow_error = False
			
			# case: error off
			elif input == "error off":
				shell_allow_error = True

			# case: Input is not a special command; send input to scanner
			else:
				# Execute command, print result
				print(con.exec(input, echo=shell_echo, return_tuple=False, allow_error=shell_allow_error))

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
