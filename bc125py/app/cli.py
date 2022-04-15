import argparse
import bc125py.app.strings as strings


_VERBOSE = False


def main():

	# --- Command Line Arguments ---
	# Create main cli parser
	main_parser = argparse.ArgumentParser(prog=strings.CLI_PROGRAM_NAME, description=strings.CLI_PROGRAM_DESCRIPTION)

	# Add universal cli arguments
	main_parser.add_argument("-v", "--verbose", action="store_true", help=strings.CLI_COMMAND_VERBOSE_HELP)
	main_parser.add_argument("--version", action="version", version=strings.VERSION)

	# Add subcommands
	sub_parsers = main_parser.add_subparsers(dest="command", required=True, help=strings.CLI_COMMAND_SUBCOMMAND_HELP)

	# Subcommand test
	read_parser = sub_parsers.add_parser("test", help=strings.CLI_COMMAND_SUBCOMMAND_TEST_HELP)

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
	_VERBOSE = cli_args.verbose

	return 0
