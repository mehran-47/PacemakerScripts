#!/usr/bin/env python
import logging as lg, time, os, json, sys
from multiprocessing import Event as ProcessEvent
from subprocess import Popen, PIPE, call
from shlex import split

class pacemakerGlue():
	def __init__(self, procShouldRun, currentDir, interval=3):
		self.procShouldRun = procShouldRun
		self.interval = interval
		self.hostname = Popen(split('hostname -s'), stdout=PIPE).communicate()[0].strip()
		lg.debug(self.hostname)
		self.dir = currentDir

	def __send_terminate(self):
		lg.debug('pacemakerGlue: terminating')
		call([self.dir+'/VLCcommandDispatcher.py', self.dir+'/config.json','terminate'])
		self.procShouldRun.clear()

	def check_status(self):
		timeout = 60
		if not os.path.isfile('/tmp/vlc.state'): 
			with open('/tmp/vlc.state','w') as f: f.write('standby')
		while self.procShouldRun.is_set():
			x = Popen(split('crm status'), stdout=PIPE)
			output = [aLine for aLine in x.communicate()[0].split('\n') if 'VLC_vidstream' in aLine]
			if not output[0:]:
				#allowing the resources up to 60 seconds to come up
				timeout -= 1
				lg.debug('pacemakerGlue: timeout: %d' %(timeout))
				if timeout<0: 
					lg.debug('pacemakerGlue: VLC resource load failed in pacemaker, terminating')
					self.__send_terminate()					
			else:
				timeout = 60 
				with open('/tmp/vlc.state','r') as f: state = f.read().strip()
				if output[-1].rsplit(' ')[-1].strip() == self.hostname:					
					if state!='active':	
						lg.debug('pacemakerGlue: setting active')
						call([self.dir+'/VLCcommandDispatcher.py', self.dir+'/config.json','set_active'])
				else:					
					if state!='standby':
						lg.debug('pacemakerGlue: stating standby')
						call([self.dir+'/VLCcommandDispatcher.py', self.dir+'/config.json','set_standby'])
			time.sleep(self.interval)
			#for controlling glue from pacemaker
			if not os.path.isfile('/tmp/pcmk.glue'):
				self.__send_terminate()

if __name__ == '__main__':
	lg.basicConfig(level=lg.DEBUG)
	if sys.argv[1:]:
		with open(sys.argv[1], 'r') as f: currentDir=json.loads(f.read())['scripts_dir']
		pge = ProcessEvent()
		pge.set()
		pg = pacemakerGlue(pge, currentDir)
		try:
			pg.check_status()
		except KeyboardInterrupt:
			lg.info('clearing pacemaker status checking')
			pge.clear()
	else:
		lg.error('Usage: %s <config_file>')