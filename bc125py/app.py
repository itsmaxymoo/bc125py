import argparse
import bc125py


_VERBOSE = False


def main():
	# Create main cli parser
	cli_parser = argparse.ArgumentParser(prog=bc125py.MODULE_NAME, description=bc125py.MODULE_DESCRIPTION)

	# Add universal cli arguments
	cli_parser.add_argument("-v", "--verbose", action="store_true")
	cli_parser.add_argument("--version", action="version", version=bc125py.MODULE_VERSION)

	# Parse arguments
	cli_args = cli_parser.parse_args()
	
	# Set verbosity level
	_VERBOSE = cli_args.verbose

	return 0
