import re
import pathlib
from random import randint

# Expected format C.B.A where B,A is alphanumeric + hyphon
# C can have periods
def valid_hostname(hostname: str) -> bool:
    return None != re.search("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.){2,}[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", hostname)

# Expected C.B.A, B.A or A
def valid_partial_hostname(hostname: str) -> bool:
     return None != re.search("(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.){0,}[a-z0-9][a-z0-9-]{0,61}[a-z0-9]", hostname)

def valid_port(port: int)  -> bool:
    return 1024 <= port <= 65535

def get_valid_port(taken_ports: set) -> int:
    candidate = randint(1024, 65535)
    while candidate in taken_ports:
        candidate = randint(1024, 65535)
    taken_ports.add(candidate)
    return candidate

def valid_directory(directory_path: str) -> bool:
    return pathlib.Path(directory_path).exists()

# C.B.A -> A, B.A, C.B.A
def split_hostname(hostname: str) -> tuple[str, str, str]:
        hostname_parts = hostname.split(".")
        root_query = hostname_parts[-1]
        tld_query = f"{hostname_parts[-2]}.{root_query}"
        auth_query = hostname

        return root_query, tld_query, auth_query