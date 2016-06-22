#!/usr/bin/env python
import datetime, sys
from subprocess import call
if __name__ == '__main__':
	if sys.argv[1:]:
		killtime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
		call(['kill','-9', sys.argv[1]])
		with open('killtime', 'w') as f:f.write(killtime)
	else:
		print('provide PID to kill')
