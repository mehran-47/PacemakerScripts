#!/usr/bin/env python
from pexpect import spawn
from threading import Thread, Event as ThreadEvent
import sys, os, logging as lg, time, json
from multiprocessing import Pipe, Process, Queue, Event as ProcessEvent
from connection import *
from checkpoint_service import *

class vlcRemoteColtroller():
	def __init__(self, multiQ, checkpointHandle ,runThreads, runProcs):		
		self.handle = spawn('bash', timeout=None)
		self.check_new_commands = runThreads
		self.listen_for_commands = runProcs
		self.isFirstCall = True
		self.commandstack = multiQ
		self.interval = 2
		self.last10Lines = []
		self.commands_executer = Thread(target=self.command_executer, args=(multiQ,))
		self.commands_executer.start()
		self.ckpt = checkpointHandle

	def instantiate(self, user, path_to_video, ip, port, play=False):
		if os.path.exists(path_to_video):
			lg.debug('command to play video:')
			self.handle.sendline('su '+ user +' -c "vlc -vvv '+ path_to_video + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + str(port) + '/rtest}\' --loop --ttl 1 -I rc"')
			if not play: self.handle.sendline('stop')
			lg.info('vlc -vvv '+ path_to_video + ' --sout \'#rtp{sdp=rtsp://' + ip + ':' + str(port) + '/rtest}\' --loop --ttl 1 -I rc')
			try:
				for line in self.handle: 
					self.last10Lines.append(line)
					self.last10Lines = self.last10Lines[-10:]
					if not self.check_new_commands.is_set(): break
			except KeyboardInterrupt:
				lg.info('Stopping vlc')
				self.check_new_commands.clear()
				self.handle.sendline('quit')
		else:
			lg.error('Invalid path to video: %s' %(path_to_video))
	
	def command_executer(self, multiQ):
		while self.check_new_commands.is_set():
			if not self.commandstack.empty():
				aCommand = self.commandstack.get()
				lg.debug(aCommand)
				lg.debug(self.last10Lines)
				if aCommand.strip()=='terminate':
					self.handle.sendline('quit')
					self.check_new_commands.clear()
					self.listen_for_commands.clear()
					lg.info('Stopping vlc remote.')
				elif aCommand.strip()=='get_time':
					lg.debug("current time: %s" %(self.get_time()))
				elif aCommand.strip().split(' ')[0]=='seek':
					self.resume_at(aCommand.strip().split(' ')[1])
				elif aCommand.strip().split(' ')[0]=='resume':
					lastCkpt = self.ckpt.getLatestCheckPoint()
					lg.debug('resuming from %s' %(lastCkpt))
					self.resume_at(lastCkpt)
				else:
					self.handle.sendline(aCommand)
				#if aCommand.split(',')[0]=='seek'
			time.sleep(self.interval)
		lg.info('Stopping live command input')

	def is_playing(self):
		self.handle.sendline('is_playing')
		#repeated intentionally as the output tails the input by 1 command
		self.handle.sendline('is_playing')
		return int(self.last10Lines[-1].split('\\')[0].strip())==0

	def get_time(self):
		self.handle.sendline('get_time')
		#repeated intentionally as the output tails the input by 1 command
		self.handle.sendline('get_time')
		return self.last10Lines[-1].split('\\')[0].strip()

	def resume_at(self, resumeTime):
		lg.debug('command to resume at time : %s' %(resumeTime))
		'''
		if not self.is_playing():
			self.handle.sendline('play')
		'''
		self.handle.sendline('play')
		self.handle.sendline('seek '+ str(resumeTime))

	def checkpoint_enqueue(self, checkpointingQ, interval=5):
		while self.check_new_commands.is_set():
			lastTime = self.get_time()
			if lastTime[0:]:
				if lastTime[-1] in str(list(range(10))): 				
					checkpointingQ.put(lastTime)
			time.sleep(interval)


def server_recv_commands (child_pipe, multiQ, serverConn, runProcs):
	try:
		while runProcs.is_set():
			data = child_pipe.recv()
			if data: 
				lg.debug(data)
				if data.get('message'):
					multiQ.put(data.get('message'))
			time.sleep(2)
		lg.info('Stopping network server')
		serverConn.shouldRun.clear()
	except KeyboardInterrupt:
		runProcs.clear()
		lg.info('Stopping checkpoint server')


def start_remote_vlc_service(configfile):
	with open(configfile, 'r') as cf: config = json.loads(cf.read())
	lg.basicConfig(level=lg.DEBUG)
	multiQ = Queue()
	checkpointingQ = Queue()
	runThreads = ThreadEvent()
	runProcs = ProcessEvent()
	runThreads.set()
	runProcs.set()
	server = connection(config['vlc_client']['server']['ip'], config['vlc_client']['server']['port'], runProcs)
	parent_pipe, child_pipe = Pipe()
	#Start server process *before* starting remote control thread
	serverProcess = Process(target=server_recv_commands , args=(child_pipe, multiQ, server, runProcs))
	serverProcess.start()
	lg.info('Listening on %r:%r' %(config['vlc_client']['server']['ip'], config['vlc_client']['server']['port']))
	ckpt = checkpoint(config['checkpoint_config'], runProcs)
	vc = vlcRemoteColtroller(multiQ, ckpt, runThreads, runProcs)
	vcThread = Thread(target=vc.instantiate, args=(config['user'], config['video_config']['path'], config['video_config']['ip'].split('/')[0], config['video_config']['port'], True))
	vcThread.start()
	ckptConsumerProcess = Process(target=ckpt.checkpoint, args=(checkpointingQ,))
	ckptProviderThread = Thread(target=vc.checkpoint_enqueue, args=(checkpointingQ,))
	ckptProviderThread.start()
	ckptConsumerProcess.start()
	server.listen(parent_pipe)
	runProcs.clear()
	runThreads.clear()

if __name__ == '__main__':
	if sys.argv[1:]:
		start_remote_vlc_service(sys.argv[1])
	else:
		lg.error('No config file provided.\nUsage: %s <config_file>.json' %(sys.argv[0]))

