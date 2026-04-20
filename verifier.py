"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import pathlib

master = []
root = []
tld = []
auth = []



def remove_duplicates(records: list[list[str]]) -> list[list[str]]:
    ports = [r[1] for r in records]

    #No duplicate ports
    if len(ports) == len(set(ports)):
        return records 
    
    #Extract duplicate ports
    dupes = list({p for p in ports if ports.count(p) > 1})

    #[ [domain1, domain2, ... , domainN] , port ]
    new_records = []

    #Scan through duplicate ports
    for dupe in dupes:
        new_record = []

        for r in records:
            #If we find record with the same port, add to new record
            if r[1] == dupe:
                new_record.append(r[0])

            #Otherwise change nothing
            else:
                new_records.append(r)

        #If we have have made a new record, add to all records
        if len(new_record) != 0:
            new_records.append([new_record, dupe])
        
    return new_records
    

def match_master(domain: str, port: str) -> bool:
    global master
    #print(f"Checking master {domain} @ {port}")

    try:
        domain.split(".")
    except AttributeError:

        #Case where we have multiple domains to one port
        for d in domain:
            #Check that auth domain and port match with master
            for record in master[1:]:
                if (record[0] == d):
                    if (record[1] != port):
                        return False
            return True
                        
    
    #Check that auth domain and port match with master
    for record in master[1:]:
        if (record[0] == domain):
            if (record[1] == port):
                return True
            else:
                return False

    return False    


def check_auth(domain:list[str], port: str) -> bool:
    global auth
    #print(f"Checking auth {domain} @ {port}")

    try:
        #Get index of file which has the port we are looking for
        idx = [records[0][0] for records in auth].index(port)
    except ValueError:    
        return False #If we dont find a matching port
    

    for record in auth[idx][1:]:
            try:
                record[0].split(".")
            except AttributeError:  
                #Case where we have multiple domains to one port
                for r in record[0]:
                    
                    #If entry in auth record does not end with the domain name of main OR does not have associated record in master
                    if ((r.split(".")[-2] + "." +  r.split(".")[-1]) not in domain):
                        return False 
                    
                if (not match_master(record[0], record[1])):
                    return False
                
                return True
            
            #If entry in auth record does not end with the domain name of main OR does not have associated record in master
            if ((record[0].split(".")[-2] + "." +  record[0].split(".")[-1]) not in domain or not match_master(record[0], record[1])):
                return False 
        
    return True


def check_tld(domain, port: str) -> bool:
    global tld
    #print(f"Checking tld {domain} @ {port}")

    try:
        #Get index of file which has the port we are looking for
        idx = [records[0][0] for records in tld].index(port)
    except ValueError:    
        return False #If we dont find a matching port
    
    for record in tld[idx][1:]:
            try:
                record[0].split(".")
            except AttributeError:  
                #Case where we have multiple domains to one port
                for r in record[0]:
                    #If entry in tld file does not end with the domain name of auth OR if it does not have associated auth file
                    if ((r.split(".")[-1]) not in domain):
                        return False 
                
                if (not check_auth(record[0], record[1])):
                    return False
                
                return True
            
            #If entry in tld file does not end with the domain name of auth OR if it does not have associated auth file
            if (record[0].split(".")[-1] not in domain or not check_auth(record[0], record[1])):
                return False 
        
    return True


def check_root() -> bool:
    global root

    #Check each entry in the root file, that it has an associated tld file
    for record in root[1:]:
        if not check_tld(record[0], record[1]):
            return False
    
    return True


def valid_configuration(master_filepath: str, directory_path: str) -> bool:
    global master
    global root
    global tld
    global auth

    #Read in master config file
    master = [x[:-1].split(",") for x in open(master_filepath).readlines()]

    files = pathlib.Path(directory_path).glob('*')

    #Scan through each single file in directory
    for file in files:

        #Extract contents of file
        records = [x[:-1].split(",") for x in open(file).readlines()]

        #Determine if the single file is a root, tld or auth file and load into respective variables
        for record in records[1:]:
            if (len(record[0].split(".")) == 1):
                root = [records[0]] + remove_duplicates(records[1:])
                break
            elif (len(record[0].split(".")) == 2):
                tld.append([records[0]] + remove_duplicates(records[1:]))
                break
            else:
                auth.append([records[0]] + remove_duplicates(records[1:]))
                break

    # print(f"ROOT: {root}")
    # print(f"TLD: {tld}")
    # print(f"AUTH: {auth}")

    #Begin validation
    return check_root()


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


def valid_domain(domain: str) -> bool:
    domain_parts = domain.split(".")

    #Needs to be full hostname (C.B.A)
    if (len(domain_parts) < 3):
        return False

    #Check if B and A are alpahnumeric including "-", same check for C but including "."
    return check_alnum(domain_parts[-1], domain_parts[-2]) and check_alnum_dot(".".join(domain_parts[0:-2]))


def valid_partial_domain(domain: str) -> bool:
    domain_parts = domain.split(".")

    #Divide domain, accounting for partial domains
    if len(domain_parts) == 1:
        return check_alnum(domain_parts[-1])
    if len(domain_parts) == 2:
        return check_alnum(domain_parts[-1], domain_parts[-2])
    if len(domain_parts) >= 3:
        return check_alnum(domain_parts[-1], domain_parts[-2]) and check_alnum_dot(".".join(domain_parts[0:-2]))


def valid_port(port: int) -> bool:
    if port < 1024 or port > 66335:
        return False
    
    return True


def valid_args(args: list[str]) -> bool:
    if (len(args) != 2):
        return False
    return True


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
            if (not valid_domain(domain) or not valid_port(int(port))):
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


def valid_directory(directory_path: str) -> bool:
    return pathlib.Path(directory_path).exists()


def valid_singles(directory_path: str) -> bool:
    files = pathlib.Path(directory_path).glob('*')
    for file in files:
        try:
            #Read records in from file
            records = [x[:-1].split(",") for x in open(file).readlines()]
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
                if (not valid_partial_domain(domain) or not valid_port(int(port))):
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


def main(args: list[str]) -> None:
    #Validate arguments, master file, single files and that directory exists
    if not valid_args(args):
        print("invalid arguments")
        return
    
    if not valid_master(args[0]):
        print("invalid master")
        return
    
    if not valid_directory(args[1]):
        print("singles io error")
        return

    if not valid_singles(args[1]):
        print("invalid single")
        return
    
    #Check if configuration is valid
    if valid_configuration(args[0], args[1]):
        print("eq")
    else:
        print("neq")
    
    return


if __name__ == "__main__":
    main(argv[1:])
