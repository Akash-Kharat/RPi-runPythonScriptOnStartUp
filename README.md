# RPi-runPythonScriptOnStartUp
- Open terminal create service 
```sh
sudo nano /etc/systemd/system/my_script.service
```
- Edit the file
 ```sh
[Unit]
Description=My Script Service

[Service]
ExecStart=/usr/bin/python3 /path/to/your/script.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
-Verify that the ExecStart line specifies the correct path to the Python interpreter and the correct path to your Python script. It should look something like this:
```sh
ExecStart=/usr/bin/python3 /path/to/your/script.py
```
-Reload systemd:
```sh
sudo systemctl daemon-reload
```
-Enable the Service: 
```sh
sudo systemctl enable my_script.service
```
-Reboot: 
```sh
sudo reboot
```
-After the reboot, your Python script should automatically run on startup.
You can check the status of your service and view its logs using the following commands:
To check the status of the service:
```sh
sudo systemctl status my_script.service
```
