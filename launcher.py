"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import pathlib


def generate_config_files(master_filepath: str, directory_path: str) -> None:
    
    #List of assignable ports
    assignable_ports = list(range(1024,65536))

    #Keep track of current port
    current_port = 1024

    #Extract records from master file
    records = [x[:-1].split(",") for x in open(master_filepath).readlines()]

    #Extract unique tld and auth partial domains
    tlds = set()
    auths = set()

    for domain,port in records[1:]:
        tlds.add(domain.split(".")[-1])
        auths.add(domain.split(".")[-2] + "." + domain.split(".")[-1])

    # print(f"TLD: {tlds}")
    # print(f"AUTH: {auths}")

    #Creat new root file with port
    root_file = open(f"{directory_path}/root.conf", "w")
    root_file.write(f"{current_port}\n")
    #assignable_ports.remove(int(root_port))


    for tld in tlds:

        current_port += 1
    
        #Write all tld partial domains to root file
        root_file.write(f"{tld},{current_port}\n")
        #assignable_ports.remove(int(current_port))
 
        #Create a new file for each tld
        tld_file = open(f"{directory_path}/tld-{tld}.conf", "w")
        tld_file.write(f"{current_port}\n")


        for auth in auths:

            #tld and auth not associated
            if tld not in auth:
                continue
            current_port += 1

            #Write related auths to tld file
            tld_file.write(f"{auth},{current_port}\n")
            #assignable_ports.remove(int(current_port))

            #Create new auth file for each auth
            auth_file = open(f"{directory_path}/auth-{auth}.conf", "w")
            auth_file.write(f"{current_port}\n")

            #Write each full domain associated with auth to file
            for domain, port in records[1:]:
                
                if auth not in domain:
                    continue
                current_port += 1
                
                auth_file.write(f"{domain},{port}\n")
                #assignable_ports.remove(int(current_port))

            auth_file.close()

        tld_file.close()
        
    root_file.close()
        

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
    if len(hostname_parts) < 3:
        return False

    #Check if B and A are alpahnumeric including "-", same check for C but including "."
    return check_alnum(hostname_parts[-1], hostname_parts[-2]) and check_alnum_dot(".".join(hostname_parts[0:-2]))


def valid_port(port: int) -> bool:
    if port < 1024 or port > 66335:
        return False
    
    return True


def valid_directory(directory_path: str) -> bool:
    return pathlib.Path(directory_path).exists()


def valid_master(master_filepath: str) -> bool:
    try:
        #Read records in from file
        records = [x[:-1].split(",") for x in open(master_filepath).readlines()]
    except FileNotFoundError:
        return False
    
    try:
        #Validate first port
        if not valid_port(int(records[0][0])):
            return False
        
        domains = []
        ports = []
        for domain, port in records[1:]:
            #Check that each record has a valid domain and port
            if (not valid_hostname(domain) or not valid_port(int(port))):
                return False
            
            #Check that for repeated domains, thier ports match
            if domain in domains:
                if ports[domains.index(domain)] != port:
                    return False
        
            domains.append(domain)
            ports.append(port)

    except ValueError:
        #Port is not integer
        return False
    
    return True
    

def valid_args(args: list[str]) -> bool:
    if len(args) != 2:
        return False
    return True


def main(args: list[str]) -> None:
    #Validate arguments, master file and that the directory exists
    if not valid_args(args):
        print("INVALID ARGUMENTS")
        return
    
    if not valid_master(args[0]):
        print("INVALID MASTER")
        return
    
    if not valid_directory(args[1]):
        print("NON-WRITABLE SINGLE DIR")
        return
    
    generate_config_files(args[0], args[1])


if __name__ == "__main__":
    main(argv[1:])
