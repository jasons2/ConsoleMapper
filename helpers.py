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


# def parseShowLineOutput(show_line_output: str) -> list:

#     # CLEAN INPUT DATA
#     # 1. Standardize line endings and remove carriage returns (\r)
#     clean_output = show_line_output.replace('\r\n', '\n').replace('\r', '\n')

#     # 2. Reconstruct the string: trim each line and remove empty ones
#     # This fixes "desync" issues caused by varying indentation (like 1/0 vs 0)
#     lines = [line.strip() for line in clean_output.splitlines() if line.strip()]
#     final_input = "\n".join(lines)

#     template_file = "cisco_ios_show_line.textfsm"
#     with open(TEMPLATES_DIR.joinpath(template_file)) as fsm_template:
#         textfsm_parser = textfsm.TextFSM(fsm_template)

#     results = textfsm_parser.ParseText(final_input)

#     return [dict(zip(textfsm_parser.header, row)) for row in results]

def parseOutput(device_output: str, template_file) -> list:
    # CLEAN INPUT DATA
    # 1. Standardize line endings and remove carriage returns (\r)
    clean_output = device_output.replace('\r\n', '\n').replace('\r', '\n')

    # 2. Reconstruct the string: trim each line and remove empty ones
    # This fixes "desync" issues caused by varying indentation (like 1/0 vs 0)
    lines = [line.strip() for line in clean_output.splitlines() if line.strip()]
    final_input = "\n".join(lines)

    with open(TEMPLATES_DIR.joinpath(template_file)) as fsm_template:
        textfsm_parser = textfsm.TextFSM(fsm_template)

    results = textfsm_parser.ParseText(final_input)

    return [dict(zip(textfsm_parser.header, row)) for row in results]

def cleanLines(lines: list) -> list:

    output = []

    for line in lines:
        if line["TYPE"] in ["CTY", "VTY"] or line["TTY"] in ['0', '1', '*']:
            continue
        else:
            output.append(line)
    
    return output



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

def evaluateDevice(_net_connect, device_details, tcp_port, loopback_ip):
    
    if _net_connect.find_prompt():
        device_details['evaluated'] = True
        redispatch(_net_connect, device_type="terminal_server")

        _net_connect.write_channel(f"connect {loopback_ip} {tcp_port} \n ")
        time.sleep(1)
        o = _net_connect.read_channel()
        print (f"===sent connect {loopback_ip} {tcp_port} ===\n")

        # CHECK TO ENSURE CONNECTION ACCEPTED
        if "refused by remote host" in o:
            _connectedDevice.setConnected(False)
            _connectedDevice.setAnswers(False)
            _connectedDevice.setConfirmed(False)
            _connectedDevice.audit += "=> set Connected, Answers, and Confirmed to False\n"

            return None
        
        _connectedDevice.setConnected(True)
        _connectedDevice.audit += "=> set Connected to True\n"

        count = 0
        continueToEvaluate = True

        while continueToEvaluate and count <= 1:

            # if 'user' in o:
            if re.search('user', o, re.IGNORECASE):
                count += 1
                _net_connect.write_channel(_net_connect.username + '\n')
                time.sleep(2)
                o = _net_connect.read_channel()
                _connectedDevice.audit += "===sent username===\n"
                _connectedDevice.audit += "|" + o + "|\n"

            # if 'pass' in o:
            if re.search('pass', o, re.IGNORECASE):
                _net_connect.write_channel(_net_connect.password + '\n')
                time.sleep(1) # originally 2
                _net_connect.write_channel('\r\n')
                time.sleep(3)
                o = _net_connect.read_channel()
                _connectedDevice.audit += "===sent password <CR> after 10 secs===\n"
                _connectedDevice.audit += "|" + o + "|\n"

            if matchDevice(_connectedDevice.deviceName, o):
                continueToEvaluate = False
                _connectedDevice.setConfirmed(True)
                _connectedDevice.audit += "=>setConfirmed set to True\n"
            
            if re.search(r'\w',o):
                _connectedDevice.setAnswers(True)
                _connectedDevice.audit += "=>setAnswers set to True Length %s\n" % len(o)
            else:
                _connectedDevice.setAnswers(False)
                continueToEvaluate = False
                _connectedDevice.audit += "=>setAnswers set to False\n"
            
            if not re.search("user", o, re.IGNORECASE):
                continueToEvaluate = False
                _connectedDevice.audit += "=>Exception"
                _connectedDevice.audit += "|" + o + "|\n"

        time.sleep(.5)
        
        # Send Exit in case logged into Device
        _net_connect.write_channel("exit\n")
        time.sleep(.5)

        # Sending CTRL-SHIFT-6 x
        _net_connect.write_channel(CNTL_SHIFT_6)
        _net_connect.write_channel('x')
        time.sleep(3.5)
        o = _net_connect.read_channel()
        _connectedDevice.audit += "===sent CTRL-SHFT-6 x===\n"
        _connectedDevice.audit += "|" + o + "|\n"
        
        _net_connect.write_channel("disc" + "\n")
        time.sleep(.5)
        o = _net_connect.read_channel()
        _connectedDevice.audit += "===sent 'disc <cr>'===\n"
        _connectedDevice.audit += "|" + o + "|\n"
        
        if "confirm" in o:
            _net_connect.write_channel("\n\n")
        
        time.sleep(.5)
        o = _net_connect.read_channel()
        _connectedDevice.audit += "===sent '<cr><cr>' if confirm seen===\n"
        _connectedDevice.audit += "|" + o + "|\n"
        
    else:
        _connectedDevice.audit += "\nPrompt Not Found\n"
        logger.debug("Prompt not found")


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