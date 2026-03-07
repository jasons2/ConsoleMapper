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


# def getHostname(network_connection: object, port: int, lookback_ip: str) -> str:
#     hostname = ""
#     if network_connection.find_prompt():
#         print(f"Attempting to connect to {port}")
#         redispatch(network_connection, device_type="terminal_server")

#         network_connection.write_channel(f"connect {lookback_ip} {port} \n")
#         time.sleep(1)

#         channel_output = network_connection.read_channel()

#         if "refused by remote host" in channel_output:
#             print(f"Port: {port} -> Connection refused")
#             hostname = "Connection refused"

#         elif "Open" in channel_output:
#             print("Connected...Attempting to retrieve hostname")
#             network_connection.write_channel("\n")
#             time.sleep(1)
#             channel_output = network_connection.read_channel()
            
#             match = re.search(r'^(\S+)(?=\s+login:)', channel_output, re.MULTILINE)

#             if match:
#                 hostname = match.group(1)
#             else:
#                 print(f"Hostname not found for port {port}")
#                 hostname = f"Hostname Not Found"
        
#         # Disconnect from device.
#         # Sending CTRL-SHIFT-6 x
#         print(f"Closing port {port}")
#         network_connection.write_channel(CNTL_SHIFT_6)
#         network_connection.write_channel('x')
#         time.sleep(3.5)
#         channel_output = network_connection.read_channel()
        
#         network_connection.write_channel("disc" + "\n")
#         time.sleep(.5)
#         channel_output = network_connection.read_channel()
#         network_connection.write_channel("\n")
#         time.sleep(.5)
#         channel_output = network_connection.read_channel()
#         print(f"Closed port {port} successfully")

#     else:
#         print("Prompt not found")
#     return hostname

def evaluateDevice(
        net_connect: object,
        line: object,
        loopback_ip: str) -> object:
    
    if net_connect.find_prompt():
        line.evaluated = True
        redispatch(net_connect, device_type="terminal_server")

        # Attempt to Reverse Telnet to tcp_destination_port
        net_connect.write_channel(f"connect {loopback_ip} {line.tcp_destination_port} \n ")
        time.sleep(1)
        o = net_connect.read_channel()
        line.audit += f"===sent connect {loopback_ip} {line.tcp_destination_port} ===\n")

        # CHECK TO ENSURE CONNECTION ACCEPTED
        if "refused by remote host" in o:
            line.connected = False
            line.audit += "=> set Connected, Answers, and Confirmed to False\n"
        else:        
            line.connected = True
            line.audit += "=> set Connected to True\n"

        if line.connected:
            # if 'user' in o:
            if re.search('user', o, re.IGNORECASE):
                net_connect.write_channel(net_connect.username + '\n')
                time.sleep(2)
                o = net_connect.read_channel()
                line.audit += "===sent username===\n"
                line.audit += "|" + o + "|\n"

            # if 'pass' in o:
            if re.search('pass', o, re.IGNORECASE):
                net_connect.write_channel(net_connect.password + '\n')
                time.sleep(1) # originally 2
                net_connect.write_channel('\r\n')
                time.sleep(3)
                o = net_connect.read_channel()
                line.audit += "===sent password <CR> after 1 sec===\n"
                line.audit += "|" + o + "|\n"

            if re.search('login', o, re.IGNORECASE):
                match = re.search(r'^(\S+)(?=\s+login:)', o, re.MULTILINE)

                if match:
                    hostname = match.group(1)
                else:
                    print(f"Hostname not found for port {line.tcp_destination_port}")
                    hostname = f"Hostname Not Found"
                
                line.host_name_connected = hostname
            
                line.audit += "===HostName Found and set === \n"
                
            time.sleep(.5)
            
            # Sending CTRL-SHIFT-6 x
            net_connect.write_channel(CNTL_SHIFT_6)
            net_connect.write_channel('x')
            time.sleep(3.5)
            o = net_connect.read_channel()
            line.audit += "===sent CTRL-SHFT-6 x===\n"
            line.audit += "|" + o + "|\n"
            
            # Make sure to clear the line
            net_connect.write_channel("disc" + "\n")
            time.sleep(.5)
            o = net_connect.read_channel()
            line.audit += "===sent 'disc <cr>'===\n"
            line.audit += "|" + o + "|\n"
            
            if "confirm" in o:
                net_connect.write_channel("\n\n")
            
            time.sleep(.5)
            o = net_connect.read_channel()
            line.audit += "===sent '<cr><cr>' if confirm seen===\n"
            line.audit += "|" + o + "|\n"
        
    else:
        line.audit += "\nPrompt Not Found\n"


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