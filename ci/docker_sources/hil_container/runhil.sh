nohup gunicorn -w 5 -b 0.0.0.0:7000 wsgi:application &
sleep 1
nohup hil-admin serve-networks &
sleep infinity
