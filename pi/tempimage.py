# import the necessary packages
import uuid
import os

class TempImage:
	def __init__(self, basePath="./", ext=".jpg"):
		# construct the file path
		self.key = str(uuid.uuid4())+ ext
		self.path = "{base_path}/{name}".format(base_path=basePath,
			name=self.key)
		
		

	def cleanup(self):
		# remove the file
		os.remove(self.path)