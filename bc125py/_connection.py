import os
import glob
import time


class CommandError(RuntimeError):
	"""Error resulting from an invalid scanner command

	Args:
		RuntimeError (str): Error message
	"""

	def __init__(self, message: str = "A command error has occurred"):
		super().__init__(message)


class ScannerConnection:
	
	__connected: bool = False
	__device = None


	def __init__(self):
		pass


	def connect(self, device_path: str = None) -> None:
		"""Establish a connection to the scanner

		Args:
			device_path (str, optional): Force connection to specific device. Defaults to None.

		Raises:
			ConnectionError: If the connection is already established, or if any errors occur while connecting
		"""

		if self.__connected:
			raise ConnectionError("Connection already established")

		# First, set up device driver. It doesn't matter if we do this multiple times
		self.__setup_driver()

		# Pause to give the OS time to generate the device file
		time.sleep(0.1)

		# Second, determine device path
		device_path = device_path if device_path else self.__find_device()

		# Third, establish a device connection.
		self.__connect_device(device_path)

		self.__connected = True


	def __setup_driver(self) -> None:
		"""internal use. inject driver string into kernel

		Raises:
			ConnectionError: if no scanner detected
			ConnectionError: if error writing to new_id file
		"""

		try:
			# Path to new acm device file
			driver_path: str = "/sys/bus/usb/drivers/cdc_acm/new_id"

			# Make directories up to this file
			# They likely do not exist
			os.makedirs(os.path.dirname(driver_path), exist_ok=True)

		except IOError as e:
			raise ConnectionError("No scanner found")
		
		try:
			# Open new_id file, write driver string
			driver_file = open(driver_path, "w")
			print("1965 0017 2 076d 0006", file=driver_file) # Thanks to Rikus Goodell's bc125at-perl
			driver_file.close()

		except IOError as e:
			raise ConnectionError("Error setting up driver: " + str(e))


	def __find_device(self) -> str:
		"""internal use. Find likely scanner device file

		Raises:
			ConnectionError: if could not find candidate

		Returns:
			str: path to file found
		"""

		# The code to find possible scanner device files is extensible, but we will only use the first match for now
		found_files = []
		found_files.extend(glob.glob("/dev/serial/by-id/*Uniden*BC125AT*"))
		found_files.extend(glob.glob("/dev/ttyACM*"))

		# We must find a device
		if len(found_files) < 1:
			raise ConnectionError("Could not find scanner")

		return found_files[0]


	def __connect_device(self, device_path: str):
		"""internal use. Open scanner device file for read/writing

		Args:
			device_path (str): open this device

		Raises:
			ConnectionError: if cannot open device file
		"""

		# Now, try to open the device file
		try:
			self.__device = open(device_path, "rb+", buffering=0)
		except IOError:
			raise ConnectionError("Could not open device file (rb+): " + device_path)


	def _exec(self, command: str) -> str:
		"""INTERNAL USE! USE exec() INSTEAD! -- Execute a command

		Args:
			command (str): the command to execute

		Raises:
			ConnectionError: if the command fails to send
			ConnectionError: if the response cannot be read

		Returns:
			str: device response
		"""

		# First, try to send command to device
		try:
			# Don't forget to append a \r. It's the 125AT's line ending
			# Except for writing, in which case the char to end a command is \n
			self.__device.write(bytes(command + "\r", "ascii"))
		except IOError as e:
			raise ConnectionError("Could not communicate (write) with scanner: " + str(e))
		
		# Create response string
		resp: str

		# Now we will try to read the device's response
		try:
			# Create byte string to store scanner response
			bs = b""

			# Loop through file read, stop at \n
			by = self.__device.read(1)
			while by not in (b"\r", b"\n"):
				bs += by
				by = self.__device.read(1)

			# Return result
			return bs.decode("ascii")

		except IOError as e:
			raise ConnectionError("Could not communicate (read) with scanner: " + str(e))


	def exec(self, command, echo: bool = False, return_tuple: bool = True, allow_error = False):
		"""Execute a command on the scanner. Get response.

		Args:
			command (tuple, str): The command to execute, in string or tuple form
			echo (bool, optional): Should the response include the command name? Defaults to False.
			returnTuple (bool, optional): Should the response be in tuple form? Defaults to True.
			returnTuple (bool, optional): Should we allow an invalid command? Defaults to False.

		Raises:
			ConnectionError: if a connection was never established
			ConnectionError: if there is an error communicating with the scanner
			bc125py.CommandError: if the command produces an error

		Returns:
			tuple, str: The command response in tuple or string form
		"""

		if not self.__connected:
			raise ConnectionError("Cannot execute command when scanner isn't connected")

		# Convert tuple command to command string
		if type(command) is tuple:
			command = ",".join(map(str, command))
		elif type(command) is not str:
			raise TypeError("exec() command must be str or tuple")

		# Execute command, store result
		resp = self._exec(command)

		# Make sure command executed properly
		if not allow_error:
			if resp.endswith( (",ERR", ",NG") ):
				raise CommandError("Error in command: " + command)

		# If echo is off (default), remove the command name from the response
		if not echo:
			resp = resp[4:]

		# If we want the result as a tuple (default), create tuple
		if return_tuple:
			resp = tuple(resp.split(","))


		return resp


	def close(self) -> None:
		"""Disconnect scanner. Safely closes connection.

		Raises:
			ConnectionError: if the scanner never was connected.
		"""

		if not self.__connected:
			raise ConnectionError("Can't close closed connection")
		self.__device.close()
		self.__connected = False


	def __del__(self):
		if self.__connected:
			self.close()
