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

from helpers import getConnectionToTermServ, parseLineDetails
from helpers import getHostname, getArgs
from constants import APP_DIR

def main():

    user_input = getArgs()
    if not user_input.password:
        user_input.password = getpass.getpass(prompt=f"Password for {user_input.username}: ")


    output_rows = [["TTY", "Port", "Hostname"]]
    net_connect = getConnectionToTermServ(user_input.termserv_ip_address,
                                          user_input.username,
                                          user_input.password)

    # Gather Show Line CLI
    show_line_output = net_connect.send_command("sh line")
    
    line_details = parseLineDetails(show_line_output)

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