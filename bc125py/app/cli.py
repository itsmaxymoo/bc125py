import cmd
import os
import sys
import argparse
import datetime
import readline
import bc125py
from bc125py.app import core, log
from bc125py import sdo, con as _c


# Manual port override to be used by cli commands
_port: str = None

# Port finding method
_port_detect_legacy = False


# --- CLI Utility functions

# Make sure we are root function
def enforce_root() -> None:
	if not core.is_root():
		print(bc125py.PACKAGE_NAME, "must be ran as superuser (root) to perform this function.")
		sys.exit(126)
	
	log.debug("root permissions found")


# CLI Get Scanner Connection w/ port prompt
def get_scanner_connection(port: str = None) -> _c.ScannerConnection:
	log.debug(
		"cli get_scanner_connection",
		"provided port:", port,
		"legacy mode:", _port_detect_legacy
	)

	# If we have not a user provided port, we must find one
	if not port:
		# Get all ports
		found_ports: list = _c.ScannerConnection.find_ports(_port_detect_legacy)

		# Error and exit if none found
		if not found_ports:
			log.error("No device found")
			sys.exit(1)
		
		# Make user select if more than 1
		if len(found_ports) > 1:
			print("Please select port:\n")

			for i in range(0, len(found_ports)):
				print(
					"   "
					+ str(i + 1) + ") "
					+ found_ports[i]
				)
			
			print()

			selected_port = input("select port: ")

			try:
				selected_port = int(selected_port)
				port = found_ports[selected_port - 1]
			except Exception:
				log.error("Invalid selection:", selected_port)
				sys.exit(1)


		# Else, just make the port the only device
		else:
			port = found_ports[0]
		
	# Now, get scanner connection
	return core.get_scanner_connection(port)


# --- Program entrypoint
def main() -> int:

	# --- Command Line Arguments ---
	# Create main cli parser
	main_parser = argparse.ArgumentParser(
		prog=bc125py.PACKAGE_NAME,
		description=bc125py.PACKAGE_DESCRIPTION + ", version " + bc125py.PACKAGE_VERSION,
		epilog="Please report all issues at {url} or to {email}".format(
			url=bc125py.PACKAGE_URL,
			email=bc125py.PACKAGE_AUTHOR_EMAIL
		)
	)

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
		version=bc125py.PACKAGE_VERSION
	)
	main_parser.add_argument(
		"-p",
		"--port",
		help="force " + bc125py.PACKAGE_NAME + " to use the specified device port"
	)
	main_parser.add_argument(
		"--legacy-detect",
		help="use the legacy method of scanner detection. more likely to find device, but will present duplicates",
		action="store_true"
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

	# Subcommand shell
	shell_parser = sub_parsers.add_parser("shell", help="launch interactive scanner shell")
	shell_parser.add_argument("file", help="commands file to execute", nargs="?", default=None)
	shell_parser.add_argument(
		"-c",
		"--clear-history",
		action="store_true",
		help="clear the shell's history before start"
	)

	# Subcommand wipe
	wipe_parser = sub_parsers.add_parser("wipe", help="factory reset scanner")

	# Parse arguments
	cli_args = main_parser.parse_args()

	# --- END Command Line Arguments ---
	
	# Set verbosity level
	log._DEBUG = cli_args.verbose

	# Set up logging
	if cli_args.log:
		log._FILE = open(cli_args.log, "w")
	log.debug(bc125py.PACKAGE_NAME, "version", bc125py.PACKAGE_VERSION + ", started on", datetime.datetime.now())
	log.debug("sysinfo:", core.get_system_str())
	if not core.is_linux():
		log.warn("Your system is unsupported!")

	# Set port, if specified
	if cli_args.port:
		global _port
		_port = cli_args.port
	
	# Set port detection mode
	if cli_args.legacy_detect:
		global _port_detect_legacy
		_port_detect_legacy = True

	# Dispatch subcommand
	cmd = cli_args.command
	if cmd == "test":
		return test()
	elif cmd == "import":
		return import_read(cli_args.file, cli_args.csv)
	elif cmd == "export":
		return export_write(cli_args.file, cli_args.csv)
	elif cmd == "shell":
		return shell(cmd_file_path=cli_args.file, clear_history=cli_args.clear_history)
	elif cmd == "wipe":
		return wipe()

	# If this part of the code was reached, something went wrong with argparse
	log.error("ERRoneous subc:", cli_args.command)

	return 1


# Test command
def test() -> int:
	log.debug("subc: test")

	enforce_root()

	try:
		# Connect, try to get device model
		con = get_scanner_connection(_port)
		print("Scanner model:", con.exec("MDL", return_tuple=False), "(success)")
		con.close()

		return 0

	except (ConnectionError, _c.CommandError) as e:
		log.error(str(e))
		return 1


# Import/Read command
def import_read(out_file: str, csv: bool) -> int:
	log.debug(
		"subc: import",
		"file:",
		out_file,
		"csv:", csv
	)

	enforce_root()

	try:
		# Determine if we are outputting to stdout
		stdout_mode: bool = out_file == "-"
			

		# Connect to scanner
		scanner_con = get_scanner_connection(_port)

		# Read from scanner
		if not stdout_mode:
			print("Reading from scanner...")
		log.debug("Attempting full scanner read")
		scanner: sdo.Scanner = sdo.Scanner()
		scanner.read_from(scanner_con)
		if not stdout_mode:
			print("done")

		# Open output file
		log.debug("import: creating output file")
		fout = None

		# If the output filename is -, use stdout instead
		if stdout_mode:
			log.debug("import: using stdout")
			fout = sys.stdout
		
		# Else, open output file as usual
		else:
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
def export_write(in_file: str, csv: bool) -> int:
	log.debug(
		"subc: export",
		"file:",
		in_file,
		"csv:", csv,
	)

	enforce_root()

	try:

		# Connect to scanner
		scanner_con = get_scanner_connection(port=_port)

		# Open input file
		log.debug("Attempting full file read")
		fin = None

		# If filename is -, read from stdin
		if in_file == "-":
			log.debug("export: using stdin")
			fin = sys.stdin

		# Else, open file to read as usual
		else:
			fin = open(in_file, "r")

		print("Writing to scanner...")

		if not csv:

			# Normal (JSON) export
			import json

			# Read file data
			in_file_data = fin.read()

			# Create scanner from file data
			scanner: sdo.Scanner = sdo.Scanner()
			log.debug("full export: parsing json")
			scanner.from_dict(
				json.loads(in_file_data)
			)

			# Validate scanner
			try:
				scanner.validate()
			except ValueError as e:
				for line in str(e).splitlines():
					log.error(line)
				return 1

			# Write to scanner
			log.debug("full export: writing to scanner")
			scanner.write_to(scanner_con)

		else:

			# CSV (channel only) export
			import csv

			log.debug("csv export: reading csv")
			# create CSV reader
			csv_reader = csv.reader(fin, dialect="excel")

			# Skip header row
			next(csv_reader)

			# Create list of channels
			channels: list = []

			# Loop through each row
			log.debug("csv export: parsing csv")
			for row in csv_reader:
				# Create channel dict first
				c_dict = {
					"index": int(row[0]),
					"name": row[1],
					"frequency": row[2],
					"modulation": row[3],
					"ctcss": int(row[4]),
					"delay": int(row[5]),
					"locked_out": row[6],
					"priority": row[7]
				}

				# Create channel from dict
				c: sdo.Channel = sdo.Channel()
				c.from_dict(c_dict)

				# Validate channel
				try:
					c.validate()
				except ValueError as e:
					log.error(str(e))
					return 1

				# Append channel, once validated
				channels.append(c)

			# Write channels
			log.debug("csv export: write channels")

			# PRG
			sdo.EnterProgramMode().write_to(scanner_con)

			c: sdo.Channel

			for c in channels:
				log.debug("WRITING CHANNEL", ",".join(map(lambda n : str(n), c.to_write_command())))
				c.write_to(scanner_con)

			del c

			# EPG
			sdo.ExitProgramMode().write_to(scanner_con)

		# Close input file
		fin.close()

		# Close scanner connection
		scanner_con.close()

		print("done")

		return 0

	except Exception as e:
		log.error(str(e))
		return 1


class Shell(cmd.Cmd):
	HISTORY_FILE_PATH = os.path.expanduser('~/.bc125py_history')

	def __init__(self, con):
		super(Shell, self).__init__()
		self.intro = (bc125py.PACKAGE_NAME + " " + bc125py.PACKAGE_VERSION +
					  " scanner shell" + os.linesep +
					  "try commands \"help\" or \"exit\"" + os.linesep)
		self.prompt = "> "
		self.__con = con
		self.__shell_echo = True
		self.__shell_allow_error = True
		self.__shell_history_file = self.HISTORY_FILE_PATH
		self.__shell_history_size = 1000

	def preloop(self):
		if os.path.exists(self.__shell_history_file):
			readline.read_history_file(self.__shell_history_file)

	def postloop(self):
		readline.set_history_length(self.__shell_history_size)
		readline.write_history_file(self.__shell_history_file)

	def help_echo(self):
		print("In response, show command name with \"echo on\" (default) or do not " +
		      "show command name with \"echo off\".")
	def do_echo(self, arg):
		if not arg:
			print("echo is " + ("on" if self.__shell_echo else "off"))
		elif arg == "on":
			self.__shell_echo = True
		elif arg == "off":
			self.__shell_echo = False
		else:
			print("Unexpected argument to \"echo\".")

	def help_error(self):
		print("On command error, crash with \"error on\" or do not crash with " +
		      "\"error off\" (default).")
	def do_error(self, arg):
		if not arg:
			print("error is " + ("off" if self.__shell_allow_error else "on"))
		elif arg == "on":
			self.__shell_allow_error = False
		elif arg == "off":
			self.__shell_allow_error = True
		else:
			print("Unexpected argument to \"error\".")

	def help_exit(self):
		self.help_EOF()
	def do_exit(self, arg):
		return self.do_EOF(arg)

	def help_print(self):
		print("Print all text after \"print\".")
	def do_print(self, arg):
		print(arg)

	def help_EOF(self):
		print("Exit the shell.")
	def do_EOF(self, arg):
		return True

	def default(self, arg):
		if arg[:1] == "#":
			return False
		print(self.__con.exec(arg, echo=self.__shell_echo, return_tuple=False,
							  allow_error=self.__shell_allow_error))

# Shell command
def shell(cmd_file_path: str = None, clear_history: bool = False) -> int:
	log.debug("subc: shell")

	enforce_root()

	# Clear history if the user requested it. Fail silently
	if clear_history:
		log.debug("subc: shell: Clearing shell history file: " + Shell.HISTORY_FILE_PATH)
		try:
			os.unlink(Shell.HISTORY_FILE_PATH)
			log.debug("subc: shell: Shell history file successfully cleared")
		except Exception as e:
			log.debug("subc: shell: error deleting history file: " + str(e))

	try:
		# Connect
		con = get_scanner_connection(_port)

		the_shell = Shell(con)

		# If we're reading from a command file
		if cmd_file_path:
			log.debug("subc: shell: commands file:", cmd_file_path)

			# Open file and read
			fin = None

			# If the filename is -, read from stdin
			if cmd_file_path == "-":
				fin = sys.stdin
				log.debug("shell: using stdin")
		
			# Else, read from file as usual
			else:
				fin = open(cmd_file_path, "r")

			# Skip the intro and exit when done
			the_shell.intro = ""
			the_shell.cmdqueue.extend(fin.read().splitlines() + ["exit"])

			fin.close()

		the_shell.cmdloop()
			
		# Close scanner connection
		con.close()

		return 0

	except Exception as e:
		log.error(str(e))
		return 1


# Wipe command
def wipe():
	log.debug("subc: wipe")

	# User confirmation password
	USER_CONFIRMATION_PASSWORD = "I understand the consequences."

	enforce_root()

	# Inform user about the danger of this command
	print("This command will perform a factory reset on the connected scanner and DELETE ALL CHANNELS!")
	print("It is STRONGLY recommended to back up your scanner first, using:", bc125py.PACKAGE_NAME, "import\n")
	print("To wipe the connected scanner, type:", USER_CONFIRMATION_PASSWORD)

	# Get user confirmation
	user_input = input("> ")

	log.debug("wipe: confirm input == password:", user_input, "==", USER_CONFIRMATION_PASSWORD)

	if user_input != USER_CONFIRMATION_PASSWORD:
		log.debug("**PASSWORD MISMATCH**")
		log.error("Confirmation not obtained!")
		return 1

	else:
		log.debug("continuing with wipe")

	try:

		# Connect
		con = get_scanner_connection(_port)

		# Issue wipe command
		print("Wiping scanner. DO NOT UNPLUG THE DEVICE OR TURN POWER OFF!")
		print("This will take some time...")
		sdo.EnterProgramMode().write_to(con)
		sdo.ClearScannerMemory().write_to(con)
		sdo.ExitProgramMode().write_to(con)

		# Done
		print("done")

		return 0

	except Exception as e:
		log.error(str(e))
		return 1
