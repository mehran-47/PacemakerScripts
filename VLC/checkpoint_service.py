#!/usr/bin/env python
import logging as lg, sys, json, time, mysql.connector
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
		self.dbuser = config['db']['user']
		self.dbpw = config['db']['password']
		self.dbname = config['db']['db']
	
	def checkpoint(self, checkpointingQ):
		'''
		cnx = mysql.connector.connect(user='root', password='password', database='vlc_checkpoint')
		cr = cnx.cursor()
		cr.execute('update seek set pos=%s where id="0_0"' %(pp))
		cnx.commit()
		----------------
		cr.close()
		cnx.close()
		'''
		cnx = mysql.connector.connect(user=self.dbuser, password=self.dbpw, database=self.dbname)
		cr = cnx.cursor()
		while self.shouldRun.is_set():
			if not checkpointingQ.empty():
				self.seek = checkpointingQ.get()
				lg.debug('from inside checkpointing service %r' %(self.seek))
				with open(self.path+'/checkpoint', 'w') as cf: cf.write(self.seek)
				lg.debug('############ update seek set pos=%r where id="0_0"' %(self.seek))
				cr.execute('update seek set pos=%s where id="0_0"' %(self.seek))
				cnx.commit()
			time.sleep(self.interval)
		cr.close()
		cnx.close()

	def getLatestCheckPoint(self):
		cnx = mysql.connector.connect(user=self.dbuser, password=self.dbpw, database=self.dbname)
		cr = cnx.cursor()
		cr.execute("select pos from seek where id='0_0'")
		lastCheckpoint = cr.fetchone()
		lg.debug('getLatestCheckPoint: latest checkpoint fetched %s' %(lastCheckpoint))
		cr.close()
		cnx.close()
		return lastCheckpoint[0]