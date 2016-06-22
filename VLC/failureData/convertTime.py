#!/usr/bin/env python
import sys, datetime
if __name__ == '__main__':
	if sys.argv[2:]:
		with open(sys.argv[1], 'r') as f: 
			t1 = datetime.datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S.%f')
		with open(sys.argv[2], 'r') as f: 
			t2 = datetime.datetime.strptime(f.read().strip(), '%Y-%m-%d %H:%M:%S.%f')
		print('microseconds %r\nseconds %f' %((t1-t2).microseconds, float((t1-t2).microseconds)/10**6))
