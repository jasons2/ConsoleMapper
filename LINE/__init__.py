from dataclasses import dataclass, field, asdict
from typing import Any, Optional


@dataclass
class Line:
    evaluated: bool = False
    connected: bool = False
    in_show_run: bool = False
    host_name_connected: Optional[str] = None
    host_name_configured: Optional[str] = None
    tty: Any = None
    line: Any = None
    tcp_destination_port: Optional[int] = None
    noisy_line: bool = False
    noise_level: Any = None
    # 'audit' is initialized to "" but not included in the __init__ arguments
    audit: str = field(init=False, default="")

    def __str__(self):
        """Custom string representation."""
        return (f"ConnectedDevice(Host: {self.host_name_connected}, "
                f"Connected: {self.connected}, TTY: {self.tty}, Line: {self.line})")

    def __repr__(self):
        """Custom repr representation (matching your original format)."""
        return (
            f"ConnectedDevice("
            f"evaluated={self.evaluated!r}, "
            f"connected={self.connected!r}, "
            f"in_show_run={self.in_show_run!r}, "
            f"host_name_connected={self.host_name_connected!r}, "
            f"host_name_configured={self.host_name_configured!r}, "
            f"tty={self.tty!r}, "
            f"line={self.line!r}, "
            f"noisy_line={self.noisy_line!r}, "
            f"noise_level={self.noise_level!r}, "
            f")"
        )

    def to_csv_row(self):
        data = asdict(self)
        del data['audit']  # Remove the audit field
        return list(data.values())