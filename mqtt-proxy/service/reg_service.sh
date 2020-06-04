echo "Copying service spec."
cd /lib/systemd/system/
BASE_PATH="/home/david/Moqiott"
sudo cp $BASE_PATH/mqtt-proxy/service/mqtt-proxy.service ./mqtt-proxy.service

echo "Stopping service (if existing). Chmod 644 service spec."
sudo systemctl stop mqtt-proxy.service
sudo chmod 644 /lib/systemd/system/mqtt-proxy.service
chmod +x $BASE_PATH/mqtt-proxy/run.py
chmod -R 775 $BASE_PATH/log/

echo "Restarting daemon, enabling/starting service."
sudo systemctl daemon-reload
sudo systemctl enable mqtt-proxy.service
sudo systemctl start mqtt-proxy.service

sudo systemctl status mqtt-proxy.service
