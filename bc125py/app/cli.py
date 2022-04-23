import sys
import argparse
import datetime
import bc125py.app.strings as strings
import bc125py.app.log as log
import bc125py.app.core as core
from bc125py.connection import ScannerConnection, CommandError


# Program entrypoint
def main() -> int:

	# --- Command Line Arguments ---
	# Create main cli parser
	main_parser = argparse.ArgumentParser(prog=strings.CLI_PROGRAM_NAME, description=strings.CLI_PROGRAM_DESCRIPTION)

	# Add universal cli arguments
	main_parser.add_argument("-v", "--verbose", action="store_true", help=strings.CLI_COMMAND_VERBOSE_HELP)
	main_parser.add_argument("-l", "--log", help=strings.CLI_COMMAND_LOGFILE_HELP)
	main_parser.add_argument("--version", action="version", version=strings.VERSION)

	# Add subcommands
	sub_parsers = main_parser.add_subparsers(dest="command", required=True, help=strings.CLI_COMMAND_SUBCOMMAND_HELP)

	# Subcommand test
	test_parser = sub_parsers.add_parser("test", help=strings.CLI_COMMAND_SUBCOMMAND_TEST_HELP)

	# Subcommand read
	read_parser = sub_parsers.add_parser("read", help=strings.CLI_COMMAND_SUBCOMMAND_READ_HELP)
	read_parser.add_argument("file", help=strings.CLI_COMMAND_SUBCOMMAND_READ_FILE_HELP)

	# Subcommand write
	write_parser = sub_parsers.add_parser("write", help=strings.CLI_COMMAND_SUBCOMMAND_WRITE_HELP)
	write_parser.add_argument("file", help=strings.CLI_COMMAND_SUBCOMMAND_WRITE_FILE_HELP)

	# Subcommand shell
	shell_parser = sub_parsers.add_parser("shell", help=strings.CLI_COMMAND_SUBCOMMAND_SHELL_HELP)

	# Parse arguments
	cli_args = main_parser.parse_args()

	# --- END Command Line Arguments ---
	
	# Set verbosity level
	log._DEBUG = cli_args.verbose

	# Set up logging
	if cli_args.log:
		log._FILE = open(cli_args.log, "w")
	log.debug(strings.DEBUG_STARTED_ON, datetime.datetime.now())
	log.debug(strings.DEBUG_STARTED_SYS, core.get_system_str())
	if not core.is_linux():
		log.warn(strings.WARN_UNSUPPORTED_PLATFORM)

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
	log.debug(strings.DEBUG_CLI_SUBCOMMAND_ERR, cli_args.command)
	print("Invalid subcommand")

	return 1


# Make sure we are root function
def enforce_root() -> None:
	if not core.is_root():
		print(strings.CLI_ENFORCE_ROOT)
		sys.exit(126)
	
	log.debug(strings.DEBUG_CLI_CHECK_ROOT)


# Test command
def test() -> int:
	log.debug(strings.DEBUG_CLI_TEST)

	enforce_root()

	# Create connection
	con = ScannerConnection()
	try:
		# Connect, try to get device model
		con.connect()
		print("Scanner model:", con.exec("MDL", return_tuple=False), "(success)")

		return 0

	except (ConnectionError, CommandError) as e:
		log.error(str(e))
		return 1


# Read command
def read(out_file: str) -> int:
	log.debug(strings.DEBUG_CLI_READ, out_file)
	return 0


# Write command
def write(in_file: str) -> int:
	log.debug(strings.DEBUG_CLI_WRITE, in_file)
	return 0


# Shell command
def shell() -> int:
	log.debug(strings.DEBUG_CLI_SHELL)
	return 0
