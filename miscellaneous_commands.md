##show current configuration
crm configure show 

#configure http service
crm configure primitive HTTP_Service ocf:heartbeat:apache params configfile=/etc/apache2/apache2.conf op monitor interval="30s" op start timeout="40s" op stop timeout="60s"

#show corosync members
corosync-cmapctl | grep members 