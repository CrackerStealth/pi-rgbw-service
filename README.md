[Pi RGBW Service (v0.1)](https://github.com/CrackerStealth/pi-rgbw-service)
=================

A simple framework for controlling SMD5050 style RGBW string lights using a Raspberry PI.

Application Setup:
------

1. **Install Required Python Libraries**
    
    Connect to your Raspberry Pi as the **pi** user and use the following command to install neccissary Python modules.
    
    ```
    sudo apt-get install python-twisted
    ```

2. **Clone Repository**
    
    Clone the contents of the repository to the home directory for the **pi** user on the Raspberry Pi.
    
    ```
    cd ~
    git clone https://github.com/CrackerStealth/pi-rgbw-service.git
    ```

3. **Create Config File**
    
    If this the first time install of the software, create a new config file using the sample JSON file.
    
    ```
    cd ~/pi-rgbw-service
    cp config.json.sample config.json
    ```
    
    Configure one or more RGBW controllers in the config.json file.

4. **Configure SSL Certificates**
    
    In order for secure communication to be allowed, the controller application needs SSL certificates. By default, the service expects the **certificate** and **key** to be at `/home/pi/pi-rgbw-service-cert/localhost.crt` and `/home/pi/pi-rgbw-service-cert/localhost.key` respectively. You can either update the locations in the config file or place these items at these locations.
    
    To quickly generate SSL certificates for testing, do the following:
    
    ```
    mkdir -p /home/pi/pi-rgbw-service-cert
    openssl req -new -x509 -days 3650 -nodes -out /home/pi/pi-rgbw-service-cert/localhost.crt -newkey rsa:4096 -sha256 -keyout /home/pi/pi-rgbw-service-cert/localhost.key -subj "/CN=localhost"
    chmod 700 /home/pi/pi-rgbw-service-cert
    chmod 600 /home/pi/pi-rgbw-service-cert/*
    ```

5. **Configure The Auto-start Service**
    
    This software expects a recent version of Raspian that is using __systemd__.
    
    ```
    sudo cp /home/pi/pi-rgbw-service/extra/pirgbwserviced.service /lib/systemd/system
    sudo chmod 644 /lib/systemd/system/pirgbwserviced.service
    sudo systemctl daemon-reload
    sudo systemctl enable pirgbwserviced.service
    sudo systemctl start pirgbwserviced.service
    ```
