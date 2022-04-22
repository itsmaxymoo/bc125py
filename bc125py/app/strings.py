"""Strings file. For use in the CLI and GUI
"""


import bc125py


VERSION = bc125py.MODULE_VERSION

CLI_PROGRAM_NAME = bc125py.MODULE_NAME
CLI_PROGRAM_DESCRIPTION = bc125py.MODULE_DESCRIPTION

CLI_COMMAND_VERBOSE_HELP = "verbose mode"
CLI_COMMAND_LOGFILE_HELP = "additionally log debug statements to the specified file. use in conjunction with verbose mode"

CLI_COMMAND_SUBCOMMAND_HELP = "command"
CLI_COMMAND_SUBCOMMAND_TEST_HELP = "test scanner connection"
CLI_COMMAND_SUBCOMMAND_READ_HELP = "read data from scanner, output to file"
CLI_COMMAND_SUBCOMMAND_READ_FILE_HELP = "output file"
CLI_COMMAND_SUBCOMMAND_WRITE_HELP = "write data from file to scanner"
CLI_COMMAND_SUBCOMMAND_WRITE_FILE_HELP = "input file"
CLI_COMMAND_SUBCOMMAND_SHELL_HELP = "launch interactive scanner shell"

DEBUG_STARTED_ON = CLI_PROGRAM_NAME + " version " + VERSION + ", started on"
DEBUG_STARTED_SYS = "sysinfo:"

DEBUG_CLI_SUBCOMMAND_ERR = "ERRoneous subc:"
DEBUG_CLI_TEST = "subc: test"
DEBUG_CLI_READ = "subc: read - file:"
DEBUG_CLI_WRITE = "subc: write - file:"
DEBUG_CLI_SHELL = "subc: shell"

WARN_UNSUPPORTED_PLATFORM = "Your system is not supported!"
