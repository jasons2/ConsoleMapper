# Usage
<pre>
usage: mapit.py [-h] -u USERNAME [-p PASSWORD] -l LOOPBACK -t TERMSERV_IP_ADDRESS -c CSV_FILE_NAME

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        username
  -p PASSWORD, --password PASSWORD
                        password (prompted safely on the CLI if not given)
  -l LOOPBACK, --loopback LOOPBACK
                        Loopback IP Address
  -t TERMSERV_IP_ADDRESS, --termserv_ip_address TERMSERV_IP_ADDRESS
                        IP address of terminal server
  -c CSV_FILE_NAME, --csv_file_name CSV_FILE_NAME
                        Filename for CSV file to be created
</pre>


# Example Output
<pre>
TTY,Port,Hostname
1/0,2066,SomeHostname
1/1,2067,AnotherHostName
1/2,2068,AThirdHostName  
</pre>
