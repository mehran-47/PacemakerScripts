#!/usr/bin/env python
import logging as lg, sys, json, time
from multiprocessing import Event, Queue
from connection import *

class checkpoint():
	def __init__(self, config, shouldRun):
		lg.basicConfig(level=lg.DEBUG)
		self.shouldRun = shouldRun
		self.serverIP = config['server']['ip']	
		self.serverPort = config['server']['port']
		self.interval = config['interval']
		self.path = config['dir']
		self.seek = 0
	
	def checkpoint(self, checkpointingQ):
		while self.shouldRun.is_set():
			if not checkpointingQ.empty():
				self.seek = checkpointingQ.get()
				lg.debug('from inside checkpointing service %r' %(self.seek))
				with open(self.path+'/checkpoint', 'w') as cf: cf.write(self.seek)
			time.sleep(self.interval)