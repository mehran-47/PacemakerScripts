#!/usr/bin/env python
from pexpect import spawn
from threading import Thread
import sys, os, logging as lg, time, json
from multiprocessing import Pipe, Process, Queue
from connection import *

class vlcRemoteColtroller():
	def __init__(self, multiQ):		
		self.handle = spawn('bash', timeout=None)
		self.check_new_commands = True
		self.commandstack = multiQ
		self.interval = 2
		self.commands_executer = Thread(target=self.command_executer, args=(multiQ,))
		self.commands_executer.start()

	def instantiate(self, path_to_video, ip, port, play=False):
		if os.path.exists(path_to_video):
			lg.debug('command to play video:')
			self.handle.sendline('vlc -vvv '+ path_to_video + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + str(port) + '/rtest}\' --loop --ttl 1 -I rc')
			if not play: self.handle.sendline('stop')
			lg.info('vlc -vvv '+ path_to_video + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + str(port) + '/rtest}\' --loop --ttl 1 -I rc')
			try:
				for line in self.handle: 
					#lg.debug(line)
					pass
					if not self.check_new_commands: break
			except KeyboardInterrupt:
				lg.info('Stopping vlc')
				self.check_new_commands = False
				self.handle.sendline('quit')
		else:
			lg.error('Invalid path to video: %s' %(path_to_video))
	
	def command_executer(self, multiQ):
		while self.check_new_commands:
			if not self.commandstack.empty():
				aCommand = self.commandstack.get()
				lg.debug(aCommand)
				self.handle.sendline(aCommand)
				#if aCommand.split(',')[0]=='seek'
			time.sleep(self.interval)
		lg.info('Stopping live command input')
		self.handle.sendline('quit')

	def serverRecv(self, child_pipe, multiQ):
		try:
			while self.check_new_commands:
				data = child_pipe.recv()
				if data: 
					lg.debug(data)
					if data.get('message'):
						multiQ.put(data.get('message'))
				time.sleep(2)
		except KeyboardInterrupt:
			lg.info('Stopping checkpoint server')

def start_remote_vlc(configfile):
	with open(configfile, 'r') as cf: config = json.loads(cf.read())
	lg.basicConfig(level=lg.DEBUG)
	multiQ = Queue()
	vc = vlcRemoteColtroller(multiQ)
	vcThread = Thread(target=vc.instantiate, args=(config['video_config']['path'], config['video_config']['ip'].split('/')[0], config['video_config']['port'], True))
	server = connection(config['checkpoint_config']['server']['ip'], config['checkpoint_config']['server']['port'])
	parent_pipe, child_pipe = Pipe()
	serverProcess = Process(target=vc.serverRecv, args=(child_pipe, multiQ))
	lg.info('Listening on %r:%r' %(config['checkpoint_config']['server']['ip'], config['checkpoint_config']['server']['port']))
	vcThread.start()
	serverProcess.start()
	server.listen(parent_pipe)
	vc.check_new_commands=False

if __name__ == '__main__':
	if sys.argv[1:]:
		start_remote_vlc(sys.argv[1])
	else:
		lg.error('No config file provided.\nUsage: %s <config_file>.json' %(sys.argv[0]))

