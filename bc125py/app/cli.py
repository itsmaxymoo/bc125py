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
	return 0
