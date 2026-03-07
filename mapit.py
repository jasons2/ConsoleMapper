__author__ = "Jason Smith"
__copyright__ = "Copyright 2026, Cisco Systems Inc."
__credits__ = ["Jason Smith"]
__license__ = "GPL v3."
__version__ = "0.0.1"
__maintainer__ = "Jason Smith"
__email__ = "jasons2@cisco.com"
__status__ = "Development"

import csv
import getpass

from helpers import getConnectionToTermServ
from helpers import parseOutput, cleanLines
from helpers import evaluateDevice, getArgs
from constants import APP_DIR
from LINE import Line

def main():

    # Get Arguments Provided by User
    user_input = getArgs()
    if not user_input.password:
        user_input.password = getpass.getpass(prompt=f"Password for {user_input.username}: ")

    # Define Constants 
    output_rows = ["Evaluated", "Connected", "In Show Run", "Host (Conn)", "Host (Cfg)", "TTY", "Line", "Noisy", "Noise Lvl", "Audit"]

    # Establish Connection to Console Router
    net_connect = getConnectionToTermServ(user_input.termserv_ip_address,
                                          user_input.username,
                                          user_input.password)

    # Gather HostNames and Ports from Show Run
    show_run_output = net_connect.send_command("show run | i host")
    host_details = parseOutput(show_run_output, "cisco_show_run_hostnames.textfsm")
    # from sample_output import hosts
    # host_details = hosts

    # Gather Show Line CLI
    show_line_output = net_connect.send_command("show line")
    line_details = parseOutput(show_line_output, "cisco_ios_show_line.textfsm")
    # from sample_output import lines
    # line_details = lines

    # Create Tracker
    results = {}

    # Identify Interesting Lines Only
    interesting_lines = cleanLines(line_details)

    for line in interesting_lines:
        if line["TTY"] and line["LINE"]:
            # Clean up and calculate some variables
            tcp_destination_port = int(line["LINE"]) + 2000
            noise = line["NOISE"] if line["NOISE"] else '0'

            # Create Object to track the line
            line = Line(
                tcp_destination_port = tcp_destination_port,
                noise_level = noise,
                tty = line['TTY'],
                line = line['LINE']
                )
                        
            if int(noise) > 0:
                line.noisy_line = True
            
            results[tcp_destination_port] = line
            
    # Process Hosts in Console Router's Configuration
    for host in host_details:
        host_port = int(host['PORT'])
        if host_port in results:
            if results[host_port].host_name_configured:
                print(f"{host_port} is defined twice in ConsoleRouter Configuration")
                print(f"Trying to insert {host['HOSTNAME']} but {results[host_port].host_name_configured} already present")
            else:
                results[host_port].host_name_configured = host['HOSTNAME']
                results[host_port].in_show_run = True
        else:
            print(f"Port {host_port} is defined in Configuration, but Line is not Present.")

    for line in interesting_lines.values:
        evaluateDevice(net_connect,
                       line,
                       user_input.loopback)
        output_rows.apped(line.to_csv_row())

    with open(user_input.csv_file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(output_rows)

    net_connect.disconnect()

if __name__ == "__main__":
    main()