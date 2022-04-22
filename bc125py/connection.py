import os


class ScannerConnection:
	
	__connected: bool = False
	__device = None


	def __init__(self):
		pass


	def connect(self, device_path=None) -> None:
		if self.__connected:
			raise ConnectionError("Connection already established")

		self.__setup_driver()
		device_path = device_path if device_path else self.__setup_driver()

		self.__connected = True


	def __setup_driver(self) -> None:
		try:
			driver_path: str = "/sys/bus/usb/drivers/cdc_acm/new_id"
			os.makedirs(os.path.dirname(driver_path), exist_ok=True)

			driver_file = open(driver_path, "w")
			print("1965 0017 2 076d 0006", file=driver_file) # Thanks to Rikus Goodell's bc125at-perl
			driver_file.close()

		except IOError as e:
			raise ConnectionError("Error setting up driver: " + e.strerror)


	def __find_device(self) -> str:
		pass


	def disconnect(self) -> None:
		if not self.__connected:
			raise ConnectionError("Can't close closed connection")
		self.__device.close()
		self.__connected = False


	def __del__(self):
		if self.__connected:
			self.disconnect()
