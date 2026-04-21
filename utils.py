import re
import pathlib

# Expected format C.B.A where B,A is alphanumeric + hyphon
# C can have periods
def valid_hostname(hostname: str) -> bool:
    return None != re.search("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", hostname)

def valid_port(port: int)  -> bool:
    return 1024 <= port <= 65535

def valid_directory(directory_path: str) -> bool:
    return pathlib.Path(directory_path).exists()
