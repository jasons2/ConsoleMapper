from netmiko import Netmiko, redispatch, CNTL_SHIFT_6
import textfsm
import time
import re
import argparse

# constants
from constants import TEMPLATES_DIR

def getConnectionToTermServ(device_name, username, password):
    
    # logger.info("Establishing Connection to Terminal Server")
    # logger.debug("Establishing Connection to Terminal Server %s" % _deviceName)
    
    try:
        ts = {
            'device_type': 'cisco_xe',
            'host': device_name, 
            'username': username,
            'password': password,
            'ssh_config_file': '~/.ssh/config',
            'session_log': 'sshLog.log',
            'session_log_record_writes': True
        }
    except Exception as e:
        print(e)
        # logger.debug(e)
    
    return Netmiko(**ts)


def parseLineDetails(show_line_output: str) -> list:

    # CLEAN INPUT DATA
    # 1. Standardize line endings and remove carriage returns (\r)
    clean_output = show_line_output.replace('\r\n', '\n').replace('\r', '\n')

    # 2. Reconstruct the string: trim each line and remove empty ones
    # This fixes "desync" issues caused by varying indentation (like 1/0 vs 0)
    lines = [line.strip() for line in clean_output.splitlines() if line.strip()]
    final_input = "\n".join(lines)



    template_file = "cisco_ios_show_line.textfsm"
    with open(TEMPLATES_DIR.joinpath(template_file)) as fsm_template:
        textfsm_parser = textfsm.TextFSM(fsm_template)

    results = textfsm_parser.ParseText(final_input)

    return [dict(zip(textfsm_parser.header, row)) for row in results]
    

def getHostname(network_connection: object, port: int, lookback_ip: str) -> str:
    hostname = ""
    if network_connection.find_prompt():
        print(f"Attempting to connect to {port}")
        redispatch(network_connection, device_type="terminal_server")

        network_connection.write_channel(f"connect {lookback_ip} {port} \n")
        time.sleep(1)

        channel_output = network_connection.read_channel()

        if "refused by remote host" in channel_output:
            print(f"Port: {port} -> Connection refused")
            hostname = "Connection refused"

        elif "Open" in channel_output:
            print("Connected...Attempting to retrieve hostname")
            network_connection.write_channel("\n")
            time.sleep(1)
            channel_output = network_connection.read_channel()
            
            match = re.search(r'^(\S+)(?=\s+login:)', channel_output, re.MULTILINE)

            if match:
                hostname = match.group(1)
            else:
                print(f"Hostname not found for port {port}")
                hostname = f"Hostname Not Found"
        
        # Disconnect from device.
        # Sending CTRL-SHIFT-6 x
        print(f"Closing port {port}")
        network_connection.write_channel(CNTL_SHIFT_6)
        network_connection.write_channel('x')
        time.sleep(3.5)
        channel_output = network_connection.read_channel()
        
        network_connection.write_channel("disc" + "\n")
        time.sleep(.5)
        channel_output = network_connection.read_channel()
        network_connection.write_channel("\n")
        time.sleep(.5)
        channel_output = network_connection.read_channel()
        print(f"Closed port {port} successfully")

    else:
        print("Prompt not found")
    return hostname


def getArgs():
    parser = argparse.ArgumentParser()

    parser.add_argument('-u',
                        '--username',
                        required=True,
                        help='username')
    parser.add_argument('-p',
                        '--password',
                        help='password (prompted safely on the CLI if not given)')
    parser.add_argument('-l',
                        '--loopback',
                        required=True,
                        help='Loopback IP Address')
    parser.add_argument('-t',
                        '--termserv_ip_address',
                        required=True,
                        help='IP address of terminal server')
    parser.add_argument('-c',
                        '--csv_file_name',
                        required=True,
                        help='Filename for CSV file to be created')

    output = parser.parse_args()  # assign contents of parser to output.

    return output