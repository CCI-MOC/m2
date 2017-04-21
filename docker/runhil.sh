nohup httpd >/dev/null 2>&1 &
sleep 1
nohup haas serve_networks >/dev/null 2>&1 &
sleep infinity
