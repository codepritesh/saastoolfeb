#!/bin/bash -x

DJANGO_DIR="$(dirname $0)"
ACTION="$1"
PORT=$2

REPO_DIR="$(dirname $DJANGO_DIR)"
TOOL_DIR="$REPO_DIR/tools/"
#LOG_DIR="$DJANGO_DIR/logs/"
UVICORN_PID_FILE="/run/webport_$PORT.pid"
ROTATE_SCRIPT_PID_FILE="/run/logrotate_script_$PORT.pid"
RUNNING_PORT_CHECK_CMD="ps ax -o cmd |grep -q \"\-\-port $PORT$\""
#ROTATE_SCRIPT_CHECK_CMD="ps ax -o cmd |grep -q \"log_rotate.sh $PORT \""

case $ACTION in
start)
    echo "Starting web server on 0:$PORT"
    python3 $TOOL_DIR/monitor_link.py --activate --path $REPO_DIR --port $PORT
    cd $DJANGO_DIR
    (uvicorn d_trading_bots.asgi:application --host 0 --port $PORT) &
    uvicorn_pid=$!
    echo "$uvicorn_pid" > $UVICORN_PID_FILE
    #($TOOL_DIR/log_rotate.sh $PORT $LOG_DIR) &
    #logrotate_pid=$!
    #echo "$logrotate_pid" > $ROTATE_SCRIPT_PID_FILE
    ;;
stop)
    echo "Stopping web server on 0:$PORT"
    if [ -s $UVICORN_PID_FILE ]; then
        if eval $RUNNING_PORT_CHECK_CMD; then
            echo "Killing uvicorn on $PORT"
            kill -KILL $(<$UVICORN_PID_FILE)
        fi
        rm -f $UVICORN_PID_FILE
    fi
    #if [ -s $ROTATE_SCRIPT_PID_FILE ]; then
    #    if eval $ROTATE_SCRIPT_CHECK_CMD; then
    #        echo "Killing logrotate script on $PORT"
    #        kill -KILL $(<$ROTATE_SCRIPT_PID_FILE)
    #    fi
    #    rm -f $ROTATE_SCRIPT_PID_FILE
    #fi
    python3 $TOOL_DIR/monitor_link.py --deactivate --path $REPO_DIR --port $PORT
    ;;
*)
    echo "Not support action $ACTION"
    ;;
esac
