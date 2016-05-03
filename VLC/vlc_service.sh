#!/bin/bash

param=$1

#export DO_TOKEN=$OCF_RESKEY_do_token
#IP=$OCF_RESKEY_floating_ip
#ID=$(curl -s http://169.254.169.254/metadata/v1/id)
#HAS_FLOATING_IP=`curl -s http://169.254.169.254/metadata/v1/floating_ip/ipv4/active`

meta_data() {
  cat <<END
<?xml version="1.0"?>
<!DOCTYPE resource-agent SYSTEM "ra-api-1.dtd">
<resource-agent name="vlcservice" version="0.1">
  <version>0.1</version>
  <longdesc lang="en">
vlc ocf resource agent for streaming a specified video to a specified IP</longdesc>
  <shortdesc lang="en">Stream a video using vlc</shortdesc>
<parameters>
</parameters>
  <actions>
    <action name="start"        timeout="20" />
    <action name="stop"         timeout="20" />
    <action name="monitor"      timeout="20"
                                interval="10" depth="0" />
    <action name="meta-data"    timeout="5" />
  </actions>
</resource-agent>
END
}

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

if [ "start" == "$param" ] ; then
  python /opt/videos/vlc_vidstream start
  exit 0
elif [ "stop" == "$param" ] ; then
  python /opt/videos/vlc_vidstream stop
  exit 0;
elif [ "status" == "$param" ] ; then
  python /opt/videos/vlc_vidstream status
elif [ "monitor" == "$param" ] ; then
  PID=$(cat /tmp/vlc_service.pid);
  if isdirectory "/proc/$PID"; then
    exit 0;
  else
    exit 7;
  fi
elif [ "meta-data" == "$param" ] ; then
  meta_data
  exit 0
else
  echo "no such command $param"
  exit 1;
fi
