#!/bin/bash
isdirectory() {
  if [ -d "$1" ]
  then
    # 0 = true
    return 0 
  else
    # 1 = false
    return 1
  fi
}
PID=$(cat /tmp/vlc_service.pid);
echo $PID;
if isdirectory "/proc/$PID"; then echo "is directory"; else echo "nopes"; fi