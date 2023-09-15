#!/usr/bin/env sh

echo "running dockerized xampp by guangrei ..";
chown -R daemon $XAMPP_ROOT
lampp start
echo "checking status .."
sleep 3
lampp status
echo "xampp is ready!"
tail -f /opt/lampp/logs/access_log