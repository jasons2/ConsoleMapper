
class Line:

    def __init__(self,
                 evaluated = False,
                 connected = False,
                 answers = False,
                 in_show_run = False,
                 host_name_connected = None,
                 host_name_configured = None,
                 tty = None,
                 line = None,
                 tcp_destination_port = None,
                 noisy_line = False,
                 noise_level = None):
        
        self._evaluated = evaluated
        self._connected = connected
        self._answers = answers
        self._in_show_run = in_show_run
        self._host_name_connected = host_name_connected
        self._host_name_configured = host_name_configured
        self._tty = tty
        self._line = line
        self.tcp_destination_port = tcp_destination_port
        self._noisy_line = noisy_line
        self._noise_level = noise_level
        self._audit = ""

    # Getters
    @property
    def evaluated(self): return self._evaluated
    @property
    def connected(self): return self._connected
    @property
    def answers(self): return self._answers
    @property
    def in_show_run(self): return self._in_show_run
    @property
    def host_name_connected(self): return self._host_name_connected
    @property
    def host_name_configured(self): return self._host_name_configured
    @property
    def tty(self): return self._tty
    @property
    def line(self): return self._line
    @property
    def noisy_line(self): return self._noisy_line
    @property
    def noise_level(self): return self._noise_level
    @property
    def audit(self): return self._audit

    # Setters
    @evaluated.setter
    def evaluated(self, value): self._evaluated = value
    @connected.setter
    def connected(self, value): self._connected = value
    @answers.setter
    def answers(self, value): self._answers = value
    @in_show_run.setter
    def in_show_run(self, value): self._in_show_run = value
    @host_name_connected.setter
    def host_name_connected(self, value): self._host_name_connected = value
    @host_name_configured.setter
    def host_name_configured(self, value): self._host_name_configured = value
    @tty.setter
    def tty(self, value): self._tty = value
    @line.setter
    def line(self, value): self._line = value
    @noisy_line.setter
    def noisy_line(self, value): self._noisy_line = value
    @noise_level.setter
    def noise_level(self, value): self._noise_level = value
    @audit.setter
    def audit(self, value): self._audit = value

    def __str__(self):
        return (f"ConnectedDevice(Host: {self._host_name_connected}, "
                f"Connected: {self._connected}, TTY: {self._tty}, Line: {self._line})")

    def __repr__(self):
        return (
            f"ConnectedDevice("
            f"evaluated={self._evaluated!r}, "
            f"connected={self._connected!r}, "
            f"answers={self._answers!r}, "
            f"in_show_run={self._in_show_run!r}, "
            f"host_name_connected={self._host_name_connected!r}, "
            f"host_name_configured={self._host_name_configured!r}, "
            f"tty={self._tty!r}, "
            f"line={self._line!r}, "
            f"noisy_line={self._noisy_line!r}, "
            f"noise_level={self._noise_level!r}, "
            f"audit={self._audit!r}"
            f")"
        )



    def to_csv_row(self):
        """Returns the device data as a list for CSV writing."""
        return [
            self.host_name_connected,
            self.host_name_configured,
            self.evaluated,
            self.connected,
            self.answers,
            self.in_show_run,
            self.tty,
            self.line,
            self.noisy_line,
            self.noise_level
        ]
