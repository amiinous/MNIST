import numpy as np

class loader:
	def __init__(self):
		self.num_samples = 0;
		self.num_features = 0;

		self.a = None;
		self.b = None;

	def load_libsvm_data(self, path_to_file, num_samples, num_features, one_hot, classes):
		self.num_samples = num_samples
		self.num_features = num_features

		self.a = np.zeros((self.num_samples, self.num_features))
		if one_hot == 0:
			self.b = np.zeros(self.num_samples)
		else:
			self.b = np.zeros(( self.num_samples, len(classes) ))

		f = open(path_to_file, 'r')
		for i in range(0, self.num_samples):
			line = f.readline()
			items = line.split()
			if one_hot == 0:
				self.b[i] = float(items[0])
			else:
				self.b[i, classes.index(items[0])] = 1
			for j in range(1, len(items)):
				item = items[j].split(':')
				self.a[i, int(item[0])] = float(item[1])

	def load_libsvm_data_array(self, array_of_data, num_features, one_hot, classes):
		self.num_samples = len(array_of_data)
		self.num_features = num_features

		self.a = np.zeros((self.num_samples, self.num_features))
		if one_hot == 0:
			self.b = np.zeros(self.num_samples)
		else:
			self.b = np.zeros(( self.num_samples, len(classes) ))

		for i in range(0, self.num_samples):
			line = array_of_data[i]
			items = line.split()
			if one_hot == 0:
				self.b[i] = float(items[0])
			else:
				self.b[i, classes.index(items[0])] = 1
			for j in range(1, len(items)):
				item = items[j].split(':')
				self.a[i, int(item[0])] = float(item[1])
                