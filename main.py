import gps
import json
import paramiko


#SSH connection details

#foreign client IP address
hostname = '192.168.1.1'
port = 22
#Enter the username and password for the foreign client
username = ''
password = ''

#Local file of the map on the pi
local_html_file = '/home/pi/Documents/gpstesting/telemetry.txt'

#where you want it to be stored on the foreign client
remote_html_file = '/home/brody/Documents/gpstesting/telemetry.txt'


#create SSH Client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
sftp = None

try:
    # Connect to the remote server
    ssh.connect(hostname, port, username, password)

    # Create an SFTP client from the SSH connection
    sftp = ssh.open_sftp()
    print('ssh connection successfull')
    
except Exception as e:
    print("An error occurred:", str(e))



def get_gps_data():
    # Create a GPSD session
    session = gps.gps(mode=gps.WATCH_ENABLE)
    print('created gps session')

    # Wait for a valid fix
    while True:
        report = session.next()
        if report['class'] == 'TPV' and 'lat' in report and 'lon' in report and 'alt' in report:
            break

    # Retrieve and process GPS data
    latitude = float(report.lat)
    longitude = float(report.lon)
    altitude = float(report.alt)

    return latitude,longitude,altitude

with open('telemetry.txt','a') as file:
    while True:
        latitude, longitude, altitude = get_gps_data()
        telemetry = {
                    'altitude': "{:>07.2f}".format(round(altitude), 2),
                    'latitude': '{:.6f}'.format(latitude),
                    'longitude': '{:.6f}'.format(longitude +360),
                }
            # Convert telemetry data to JSON string and encode as bytes
        json_str = json.dumps(telemetry)
        file.write(json_str)
        print('file updated')
        sftp.put(local_html_file, remote_html_file)
        
