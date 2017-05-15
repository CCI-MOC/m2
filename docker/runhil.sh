nohup gunicorn -w 5 -b 0.0.0.0:7000 wsgi:application >/dev/null 2>&1 &
sleep 1
nohup haas serve_networks >/dev/null 2>&1 &
sleep infinity