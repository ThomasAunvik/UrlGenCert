import json
import io
import os
import os.path
import ssl
import socket
import datetime

configFile = open("config.json", "r") 
configText = configFile.read()
config = json.loads(configText)

configFile.close()

sites = config["urls"]
trustStoreFilePath = config["truststore"]["target"]
trustStorePassword = config["truststore"]["password"]

certpath = config["certpath"]

socket.setdefaulttimeout(10)

timer = datetime.datetime.now().timestamp()
while True:
    if datetime.datetime.now().timestamp() < timer:
        continue

    if os.path.exists(trustStoreFilePath):
        print("Deleting current trust store file")
        os.remove(trustStoreFilePath)

    if not os.path.exists(certpath):
        os.mkdir(certpath)

    for site in sites:
        print("Fetching from site: " + site)
        try:
            cert = ssl.get_server_certificate((site, 443))

            certPath = os.path.join(certpath, site) + ".crt"
            certFile = open(certPath, "w")
            certFile.write(cert)
            certFile.close()

            deleteCert = "keytool -delete -alias " + site + " -keystore " + trustStoreFilePath + " -storepass " + trustStorePassword
            command = "keytool -import -trustcacerts -alias " + site + " -keystore " + trustStoreFilePath + " -file " + certPath + " -storepass " + trustStorePassword + " -noprompt"
            
            if os.path.exists(trustStoreFilePath):
                os.system(deleteCert)
                print("Attempted to remove certificate: " + site)

            os.system(command)
            print("Added certificate: " + site)
        except socket.timeout:
            print("Failed to fetch certificate from '" + site + "', timeout error")

    timer = datetime.datetime.now().timestamp() + config["certrefresh"]
    print("Waiting for next round in " + str(config["certrefresh"]) + " seconds.")

print("Done")