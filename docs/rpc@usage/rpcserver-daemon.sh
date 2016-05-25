#!/bin/sh

### BEGIN INIT INFO
# Provides:          rpcserver daemon
# Required-Start:    networking nameserver-daemon
# Required-Stop:     networking nameserver-daemon
# Default-Start:     2 3 4 5 
# Default-Stop:      0 1 6
# Short-Description: This is the rpc daemon
# Descritption:      This is the rpcserver daemon
#                    which starts and runs the 
#                    rpcserver python script.
### END INIT INFO


#The configuration file that has other details.
CONFIG_FILE=/home/ims/rpc-config.json

#This takes the necessary configuration from the rpc-config.json file present in 
#the directory mentioned above.
#The directory in which the file rpcserver.py is present
DIR=$(cat $CONFIG_FILE|grep RPCSERVER_DIR|awk -F '"' '{print $4 }')
#The name of the python script that is present 
DAEMON=$(cat $CONFIG_FILE|grep RPCSERVER_DAEMON_FILE|awk -F '"' '{print $4 }')
#The name that is printed on the screen when the daemon is started
DAEMON_NAME=$(cat $CONFIG_FILE|grep RPCSERVER_DAEMON_NAME|awk -F '"' '{print $4 }')
#The arguments that are passed to the rpcserver.py script
DAEMON_OPTS=$(cat $CONFIG_FILE|grep RPCSERVER_DAEMON_OPTS|awk -F '"' '{print $4 }')

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

cd $DIR

do_start () {
    log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --chdir $DIR --startas $DAEMON $DAEMON_OPTS
    log_end_msg $?
}
do_stop () {
    log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0
