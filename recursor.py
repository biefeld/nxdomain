"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import socket
import time

#Time when the recursor began resolving the hostname
starttime: float = 0


def resolve_hostname(root_port: int, timeout: float) -> str:
    while True:

        #Get port for the related tld server from the root server, the hostname to resolve (input after connection established) and how long has currently elapsed
        tld_port, hostname, time_elapsed = get_tld_port(root_port, timeout)
        if ("NXDOMAIN" in tld_port):
            print(tld_port.strip("\n"))
            continue

        #Using the hostname, query the tld server for the related auth server. Get the aggregate time this has taken
        auth_port, time_elapsed = get_auth_port(int(tld_port), hostname, timeout-time_elapsed)
        if ("NXDOMAIN" in auth_port):
            print(auth_port.strip("\n"))
            continue

        #Using the hostname, query the auth server for the resolved port
        resolved_port = get_resolved_port(int(auth_port), hostname, timeout-time_elapsed)
        print(resolved_port.strip("\n"))


def get_tld_port(root_port: int, timeout: float) -> (str, str, float):
    #Create new socket using TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            try:
                #Start timer to track in between functions, and set time out for port
                start_time = time.time()
                server_socket.settimeout(timeout)
                server_socket.connect(('127.0.0.1', root_port))
            except ConnectionRefusedError:
                print("FAILED TO CONNECT TO ROOT")
                exit()

            while True:
                #Get hostname to resolve
                try:
                    hostname = input("")
                except EOFError:
                    exit()

                #Validate hostname
                if not valid_hostname(hostname):
                    print("INVALID")
                    continue
                break

            #Query for partial hostname with formatting
            server_socket.sendall(hostname.split(".")[-1].encode() + b'\n')

            #Get and decode response
            tld_port = server_socket.recv(1024).decode()
            return tld_port, hostname, time.time() - start_time
        except TimeoutError:
            #Timer has run out
            return "NXDOMAIN", None, None


def get_auth_port(tld_port: int, hostname: str, timeout: float) -> (str, float):
    #Create new socket using TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        
        try:
            try:
                #Start timer to track in between functions, and set time out for port
                starttime = time.time()
                server_socket.settimeout(timeout)
                server_socket.connect(('127.0.0.1', tld_port))
            except ConnectionRefusedError:
                print("FAILED TO CONNECT TO TLD")
                exit()

            #Query for partial hostname with formatting
            payload = f"{hostname.split('.')[-2]}.{hostname.split('.')[-1]}"
            server_socket.sendall(payload.encode() + b'\n')

            #Get and decode response
            auth_port = server_socket.recv(1024).decode()
            return auth_port, time.time() - starttime
        except TimeoutError:
            #Timer has run out
            return "NXDOMAIN", None


def get_resolved_port(auth_port: int, hostname: str, timeout: float) -> str:
    #Create new socket using TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        
        try:
            try:
                #Set remainder of timer as timeout
                server_socket.settimeout(timeout)
                server_socket.connect(('127.0.0.1', auth_port))
            except ConnectionRefusedError:
                print("FAILED TO CONNECT TO AUTH")
                exit()
            
            #Send all of the hostname
            server_socket.sendall(hostname.encode() + b'\n')

            #Recieve and decode port
            resolved_port = server_socket.recv(1024).decode()
            return resolved_port
        except TimeoutError:
            #Timer has run out
            return "NXDOMAIN"
  

def check_alnum(*strings: str) -> bool:
    #For each string passed in, determine if any characters are not alphanumeric or -
    for string in strings:
        for char in string:
            if not(char.isalnum() or char == "-"):
                return False
    return True
            

def check_alnum_dot(string: str) -> bool:
    #For character
    for i, char in enumerate(string):

        #String cannot start or end with "."
        if (i == 0 or i == len(string)-1):
            if (char == "."):
                return False
        
        #Check if alphanumeric, . or -
        if not(char == "." or char.isalnum() or char == "-"):
            return False
        
    return True


def valid_hostname(hostname: str) -> bool:
    hostname_parts = hostname.split(".")

    #Needs to be full hostname (C.B.A)
    if (len(hostname_parts) < 3):
        return False

    #Check if B and A are alpahnumeric including "-", same check for C but including "."
    return check_alnum(hostname_parts[-1], hostname_parts[-2]) and check_alnum_dot(".".join(hostname_parts[0:-2]))


def valid_port(port: int)  -> bool:
    if port < 1024 or port > 66335:
        return False
    return True


def valid_args(args: list[str]) -> bool:
    #Correct number of arguments
    if (len(args) != 2):
        return False
    
    #Determine if arguments are correct types
    try:
        float(args[1])
        int(args[0])
    except ValueError:
        return False
    
    #Check if argument is a valid port
    if not valid_port(int(args[0])):
        return False
    
    return True


def main(args: list[str]) -> None:
    #Validate arguments
    if not valid_args(args):
        print("INVALID ARGUMENTS")
        return

    #Begin resolving
    resolve_hostname(int(args[0]), float(args[1]))
    

if __name__ == "__main__":
    main(argv[1:])
