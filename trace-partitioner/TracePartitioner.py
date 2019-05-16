import os, json
class TracePartitioner(object):
	"""docstring for TracePartitioner"""
	def __init__(self):
		super(TracePartitioner, self).__init__()
		self.serial = 0
		self.rawTraceDir = './trace-logs/rawtraces'
		self.traceDir = './trace-logs/traces'
		self.traceLimit = 10000
		self.traceNumberMap = {} # map number of traces to the contract
		self.traceMap = {} # map traces to the contract
		
	def readTX(self, path):
		# read txlist.json and tracelist.json in blockN
		# return json data
		with open(os.path.join(path, 'txlist.json'), 'rb') as f:
			txList = json.load(f)
		with open(os.path.join(path, 'tracelist.json'), 'rb') as f:
			traceList = json.load(f)

		return txList, traceList

	def writeTraces(self, tx, traces):
		# write traces of transaction addr into json files
		CTIDict = {}
		for trace in traces:
			output = dict(trace)

			output['tx'] = tx
			output['serial'] = self.serial
			output['children'] = []


			cti =  output['cti']
			if cti:
				CTIDict[tuple(cti)] = output
			else:
				CTIDict[()] = output
		
		for k in CTIDict.keys():	
			output = CTIDict[k]
			cti = output['cti']
			if not cti:
				output['parent'] = None
			else:
				parentCTI = tuple(cti[:-1])
				parent = CTIDict[parentCTI]
				output['parent'] = parent['address']
				parent['children'].append(output['address'])

		self.writeCTIDict(CTIDict)

	def writeCTIDict(self, CTIDict):
		for key in CTIDict.keys():
			output = CTIDict[key]
			contract = output['address']
			output.pop('address', None)

			# if tx dir not exist, create it
			txDir = os.path.join(self.traceDir, contract)
			if not os.path.exists(txDir):
				os.makedirs(txDir)

			if 'code' in output: # creation
				with open(os.path.join(txDir, 'creation.json'), 'w') as f:  
					json.dump(output, f)
			else:
				if contract in self.traceNumberMap:
					self.traceNumberMap[contract] += 1
					self.traceMap[contract].append(output)
				else:
					self.traceNumberMap[contract] = 1
					self.traceMap[contract] = [output]

				if self.traceNumberMap[contract]%self.traceLimit==0: # dump to json file if full
					fileIndex = int(self.traceNumberMap[contract]/self.traceLimit)
					fileName = str(fileIndex) + '.json'
					with open(os.path.join(txDir, fileName), 'w') as f:  
						json.dump(output, f)
					self.traceMap[contract] = []


	def dumpAllTraces(self):
		for k in self.traceMap.keys():
			txDir = os.path.join(self.traceDir, k)
			fileIndex = int(self.traceNumberMap[k]/self.traceLimit)
			fileName = str(fileIndex) + '.json'
			with open(os.path.join(txDir, fileName), 'w') as f:  
				json.dump(self.traceMap[k], f)
			self.traceMap[k] = []		

	def partition(self):
		# 1. get all block numbers
		blockNs = os.listdir(self.rawTraceDir)
		blockNs.sort()

		# 2. for each block, read raw traces
		for block in blockNs:
			txList, traceList = self.readTX(os.path.join(self.rawTraceDir, block))
			
			# 3. for each transcation, write to trace
			for i in range(len(txList)):
				tx = txList[i]
				traces = traceList[i]
				self.writeTraces(tx, traces)
				self.serial += 1

		self.dumpAllTraces()


if __name__ == '__main__':
	TP = TracePartitioner()
	TP.partition()