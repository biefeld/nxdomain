from sys import argv
import socket

#[hostname, port]
records: list[list[str, int]] = []
buffer: str = ""


def add_records(new_records: list[list[str, int]]) -> None:
    global records

    #If accessing through !ADD
    if len(new_records) == 1:
        for i,r in enumerate(records):
            if r[0] == new_records[0][0]:
                #Override old port if hostname doubled up
                old = [x for x in records]
                old.pop(i)
                records.clear()
                records += old
            if r[1] == new_records[0][1]:
                #Do nothing if port double up
                return

    records += new_records


def delete_records(hostname_to_delete: str) -> None:
    index = 0

    global records

    #Find and delete hostname
    for hostname, port in records:
        if hostname == hostname_to_delete:
            records.pop(index)
            return
        index += 1


def resolve_hostname(hostname_to_resolve: str) -> int:
    global records
    

    #Find and return port for associated hostname
    for hostname, port in records:
        if hostname == hostname_to_resolve:
            return port
    return "NXDOMAIN"


def process_command(command: list[str, int]) -> None:
    match command[0]:
        case "EXIT":
            exit()

        case "ADD":
            try:

                #Validate arguments and add to records
                if valid_domain(command[1]) and valid_port(int(command[2])):
                    add_records([[command[1], command[2]]])
                else:
                    print("INVALID\n",flush=True)

            except IndexError:
                #Invalid number of arguments
                print("INVALID\n",flush=True)
            except ValueError:
                #Arguments not correct typing
                print("INVALID\n",flush=True)

        case "DEL":
            try:

                #Validate arguments and delete records
                if valid_domain(command[1]):
                    delete_records(command[1])
                else:
                    print("INVALID\n",flush=True)

            except IndexError:
                #Invalid number of arguments
                print("INVALID\n",flush=True)

        case _:
            print("INVALID\n",flush=True)


def handle_request(server_socket: socket.socket) -> None:
    client_socket, addr = server_socket.accept()
    global buffer

    while True:

        #Get data
        data = client_socket.recv(1024)

        #Nothing to respond with if there is no data
        if len(data) == 0:
            break

        #Split into individual commands
        requests = data.decode().split("\n")

        #If we have a buffer from last request, add to first command
        if buffer != "":
            requests[0] = buffer + requests[0]
            buffer = ""

        #If request did not end with a new line, add to buffer
        if requests[-1] != "":
            buffer = requests[-1]

        for request in requests[:-1]:
            if request[0] == "!":
                #Handle user commands
                process_command(request[1:].split(" "))
                continue
            else:
                #Resolve hostname and send response
                port = resolve_hostname(request)
                print(f"resolve {request} to {port}", flush=True)
                client_socket.sendall((f"{port}\n").encode()) 


def establish_connection(server_port: int) -> None:
    #Create new socket using TCP (SOCK_STREAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', server_port))
        server_socket.listen()

        while True:
            handle_request(server_socket)


def read_config(filepath: str) -> int:
    try:
        #Read lines of file into array, removing the last element (\n) of each line
        lines = [x[:-1] for x in open(filepath).readlines()]
        
        #Extract port for server to listen on
        server_port = int(lines[0])

        #Read records into array
        pre_file_records = [x.split(",") for x in lines[1:]]

        #Format records
        file_records = [[domain, int(port)] for [domain, port] in pre_file_records]
    except FileNotFoundError:
        return -1 #Cannot find or open file
    except ValueError:
        return -1 #Cannot convert ports to integer
    if not valid_config(file_records):
        return -1 #Check that records are valid

    #Add records to global array
    add_records(file_records)

    return server_port


def valid_port(port: int) -> bool:
    if port < 1024 or port > 65535:
        return False
    
    return True


def valid_args(args: list[str]) -> bool:
    #Must have 1 argument
    if len(args) != 1:
        print("INVALID ARGUMENTS", flush=True)
        return False
    
    return True


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
            if char == ".":
                return False
        
        #Check if alphanumeric, . or -
        if not(char == "." or char.isalnum() or char == "-"):
            return False
        
    return True


def valid_domain(domain: str) -> bool:
    domain_parts = domain.split(".")

    #Divide domain, accounting for partial domains
    if len(domain_parts) == 1:
        return check_alnum(domain_parts[-1])
    if len(domain_parts) == 2:
        return check_alnum(domain_parts[-1], domain_parts[-2])
    if len(domain_parts) >= 3:
        return check_alnum(domain_parts[-1], domain_parts[-2]) and check_alnum_dot(".".join(domain_parts[0:-2]))


def valid_config(records: list[list[str, int]]) -> bool:
    checked_domains = []
    checked_ports = []

    for domain, port in records:
        #Each entry must have valid domain and port
        if (not valid_domain(domain) or not valid_port(port)):
            return False
        
        #If there is a duplicate domain, it must have the same port
        if (domain in checked_domains):
            if (checked_ports[checked_domains.index(domain)] != port):
                return False
        
        checked_domains.append(domain)
        checked_ports.append(port)
    return True


def main(args: list[str]) -> None:
    if (not valid_args(args)):
        return
    
    #Get server port from config
    server_port = read_config(args[0])

    if (server_port == -1 or not valid_port(server_port)):
        print("INVALID CONFIGURATION", flush=True)
        return
    
    #Begin listening for connections
    establish_connection(server_port)


if __name__ == "__main__":
    main(argv[1:])
