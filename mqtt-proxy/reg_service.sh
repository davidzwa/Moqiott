echo "Copying service spec."
cd /lib/systemd/system/
sudo cp /home/david/Moqiott/mqtt-proxy/mqtt-proxy.service ./mqtt-proxy.service

echo "Stopping service (if existing). Chmod 644 service spec."
sudo systemctl stop mqtt-proxy.service
sudo chmod 644 /lib/systemd/system/mqtt-proxy.service
chmod +x /home/david/Moqiott/mqtt-proxy/run.py

echo "Restarting daemon, enabling/starting service."
sudo systemctl daemon-reload
sudo systemctl enable mqtt-proxy.service
sudo systemctl start mqtt-proxy.service

sudo systemctl status mqtt-proxy.service
