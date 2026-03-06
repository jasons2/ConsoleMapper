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

from helpers import getConnectionToTermServ, parseShowLineOutput
from helpers import parseOutput
from helpers import getHostname, getArgs
from constants import APP_DIR

def main():

    # Get Arguments Provided by User
    user_input = getArgs()
    if not user_input.password:
        user_input.password = getpass.getpass(prompt=f"Password for {user_input.username}: ")

    # Define Constants 
    output_rows = ["HostName (show run)", "Port (show run)", "HostName (actual)", "Port (actual)", "TTY"]

    # Establish Connection to Console Router
    net_connect = getConnectionToTermServ(user_input.termserv_ip_address,
                                          user_input.username,
                                          user_input.password)

    # Gather HostNames and Ports from Show Run
    show_run_output = net_connect.send_command("show run | i host")
    
    host_details = parseOutput(show_run_output, "cisco_show_run_hostnames.textfsm")

    #### Temporary Code
    from pprint import pprint
    pprint(show_run_output)
    pprint(host_details)

    net_connect.disconnect()

    import sys
    sys.exit()
    #####################

    # Gather Show Line CLI
    show_line_output = net_connect.send_command("show line")
    
    line_details = parseShowLineOutput(show_line_output)

    for line_detail in line_details:
        if line_detail["TYPE"] in ["CTY", "VTY"] or line_detail["TTY"] in ['0', '1', '*']:
            continue
        else:
            port = int(line_detail["LINE"]) + 2000
            host_name = getHostname(net_connect, 
                                    port, 
                                    user_input.loopback)
            output_rows.append([line_detail["TTY"],
                                str(port),
                                host_name])

    with open(user_input.csv_file_name, "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(output_rows)

    net_connect.disconnect()



if __name__ == "__main__":
    main()