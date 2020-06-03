echo "Stopping service."
sudo systemctl stop mqtt-proxy.service
sleep 1
sudo systemctl status mqtt-proxy.service
