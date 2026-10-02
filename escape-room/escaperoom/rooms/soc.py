"""
REQUIREMENTS - SOC Triage Desk — auth.log
The SSH log contains successful and failed authentication records. Identify the /24 subnet responsible for the 
largest number of failed authentication attempts.

A record is valid only if it has all fields in this form:

<TIMESTAMP> <HOST> sshd[<PID>]: <Failed|Accepted> password for <USER> from <IPv4> port <PORT> protocol 2
Requirements:

TIMESTAMP must be a valid ISO-8601 timestamp; X
PID and PORT must be integers; X
the source must be a valid IPv4 address; X
every field shown above is required.
Any line that does not satisfy the complete format is malformed and must be skipped and counted. 

For example, a line with an invalid IPv4 address, a missing sshd[PID], or missing hostname/port/protocol fields is malformed 
even if part of the line looks plausible.

For each valid Failed password record:

extract the source IP;
group failures by /24;
find the /24 with the largest failure count;
inside that /24, find the most frequent source IP;
let L be its last octet and COUNT the total failures in that /24;
form KEYPAD = "{L}{COUNT}".
The generated data guarantees one winning /24 and one most-frequent IP inside it.

Required transcript lines:

TOKEN[KEYPAD]=<code>
EVIDENCE[KEYPAD].TOP24=<cidr>/24
EVIDENCE[KEYPAD].COUNT=<int>
EVIDENCE[KEYPAD].SAMPLE=<one full valid failed-login line from the winning /24>
EVIDENCE[KEYPAD].MALFORMED_SKIPPED=<int>

"""

"""
The source must be a valid IPv4 address

The requirements for a valid IPv4 address are, according to https://blogs.ipv4mall.com/blogs/valid-ipv4-address/

Check the Format: Ensure it has four numbers separated by periods.
Verify Number Ranges: Each number should be between 0 and 255.
Avoid Leading Zeros: Numbers should not start with a zero unless they are zero.
Exclude Reserved Addresses: Be aware of addresses reserved for special uses.
Ensure Network Uniqueness: Make sure the IP address doesnt conflict with others on the same network.

Relevant requirements for this case are the first 3 points:
"""
def is_valid_ipv4(ip):
    parts = ip.split('.')
    # Check the Format: Ensure it has four numbers separated by periods.
    if len(parts) != 4:
        return False
    try:
        for p in parts:
            # Avoid Leading Zeros: Numbers should not start with a zero unless they are zero.
            if len(p) > 1 and p[0] == '0':
                return False
            num = int(p)
            # Verify Number Ranges: Each number should be between 0 and 255.
            if num < 0 or num > 255:
                return False
        return True
    except:
        return False
"""
TIMESTAMP must be a valid ISO-8601 timestamp

A valid ISO-8601 is, according to https://validatethis.org/iso-compliance-checker

The value must follow the standard exactly: YYYY-MM-DD date order, T separator, 
and a valid timezone designator (Z or ±HH:MM). Lenient parsers accept looser input; 
strict systems (APIs, schemas) do not.

"""
def is_valid_iso8601(timestamp):
    try:
        if 'T' in timestamp:
            # Split Date and Time from the timestamp to verify
            date_part, time_part = timestamp.split('T', 1)
        else:
            date_part = timestamp
            time_part = ''
        
        #Split Date into its components
        if '-' in date_part:
            date_parts = date_part.split('-')
            if len(date_parts) == 3:
                year = int(date_parts[0])
                month = int(date_parts[1])
                day = int(date_parts[2])
            else:
                return False
        else:
            return False
        
        #Check if Month is real
        if month < 1 or month > 12:
            return False
        #Check if Day is real
        if day < 1 or day > 31:
            return False
        
        #Split time into its components
        if time_part:
            #Check if the timezone designator is present
            if 'Z' not in time_part:
                return False
            time_part = time_part[:-1]
            
            if ':' in time_part:
                time_parts = time_part.split(':')
                hour = int(time_parts[0])
                minute = int(time_parts[1]) if len(time_parts) > 1 else 0
                second = int(time_parts[2]) if len(time_parts) > 2 else 0
                
                #Check if hour is real
                if hour < 0 or hour > 23:
                    return False
                #Check if minutes are real
                if minute < 0 or minute > 59:
                    return False
                #Check if seconds are real
                if second < 0 or second > 59:
                    return False
        return True
    except:
        return False

"""
PID and PORT must be integers

Simple check to see if both values are valid
"""
def is_integer(check):
    try:
        int(check)
        return True
    except:
        return False

# The big one:
# (Use of AI Disclaimer: I used AI to help debug to find some errors, commented debug lines were generated by AI.)

def parse_auth_log(log_file):
    
    malformed_count = 0
    subnet_failures = {}
    ip_failures = {}
    sample_lines = {}
    # debug_failures = {}
    
    with open(log_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            #If entry is incomplete:
            if len(parts) < 13:
                malformed_count += 1
                #debug_failures['incomplete'] = debug_failures.get('incomplete', 0) + 1
                continue

            #Split entry into its components:
            timestamp = parts[0]
            host = parts[1]
            sshd_part = parts[2]
            status = parts[3]
            password_word = parts[4]
            for_word = parts[5]
            user = parts[6]
            from_word = parts[7]
            ip = parts[8]
            port_word = parts[9]
            port = parts[10]
            protocol_word = parts[11]
            protocol = parts[12] if len(parts) > 12 else None
            
            #If entry has a valid timestamp:
            if not is_valid_iso8601(timestamp):
                malformed_count += 1
                # debug_failures['timestamp'] = debug_failures.get('timestamp', 0) + 1
                continue
            #If entry specifies sshd at the start:
            if not sshd_part.startswith('sshd[') or not sshd_part.endswith(']:'):
                malformed_count += 1
                # debug_failures['sshd_format'] = debug_failures.get('sshd_format', 0) + 1
                continue
            #If sshd value is not an integer:
            pid_str = sshd_part[5:-2]  # Extract PID from sshd[PID]:
            if not is_integer(pid_str):
                malformed_count += 1
                # debug_failures['pid'] = debug_failures.get('pid', 0) + 1
                continue
            #If entry doesn't have a Failed/Accepted record:
            if status not in ['Failed', 'Accepted']:
                malformed_count += 1
                # debug_failures['status'] = debug_failures.get('status', 0) + 1
                continue
            #If entry doesn't have "password" word:
            if password_word != 'password':
                malformed_count += 1
                # debug_failures['password_word'] = debug_failures.get('password_word', 0) + 1
                continue
            #If entry doesn't have "for" word:
            if for_word != 'for':
                malformed_count += 1
                # debug_failures['for_word'] = debug_failures.get('for_word', 0) + 1
                continue
            #If entry doesn't direct where it came from:
            if from_word != 'from':
                malformed_count += 1
                # debug_failures['from_word'] = debug_failures.get('from_word', 0) + 1
                continue
            #If entry is a valid IPv4 address:
            if not is_valid_ipv4(ip):
                malformed_count += 1
                # debug_failures['ipv4'] = debug_failures.get('ipv4', 0) + 1
                continue
            #If entry doesn't direct the port it comes from:
            if port_word != 'port':
                malformed_count += 1
                # debug_failures['port_word'] = debug_failures.get('port_word', 0) + 1
                continue
            #If entry port is not an integer:
            if not is_integer(port):
                malformed_count += 1
                # debug_failures['port'] = debug_failures.get('port', 0) + 1
                continue
            #If entry has protocol listed:
            if protocol_word != 'protocol':
                malformed_count += 1
                # debug_failures['protocol_word'] = debug_failures.get('protocol_word', 0) + 1
                continue
            #If entry has valid protocol (Specified protocol 2 in the requirements):
            if protocol is None or protocol != '2':
                malformed_count += 1
                # debug_failures['protocol'] = debug_failures.get('protocol', 0) + 1
                continue
            #If entry has status 'Accepted' (We're looking for failed attempts only):
            if status != "Failed":
                continue
            #If we're good, log and process
            # extract the source IP
            # group failures by /24;
            subnet = '.'.join(ip.split('.')[:3]) + '.0/24'
            
            if subnet not in subnet_failures:
                subnet_failures[subnet] = 0
            subnet_failures[subnet] += 1
            
            if ip not in ip_failures:
                ip_failures[ip] = 0
            ip_failures[ip] += 1
            
            if subnet not in sample_lines:
                sample_lines[subnet] = line
    
    return subnet_failures, ip_failures, sample_lines, malformed_count 
    #return subnet_failures, ip_failures, sample_lines, malformed_count , debug_failures

def main():
    #TODO REMOVE AND ADD TO GAME MENU
    log_file = "data/auth.log"
    
    subnet_failures, ip_failures, sample_lines, malformed_count = parse_auth_log(log_file)
    #subnet_failures, ip_failures, sample_lines, malformed_count, debug_failures = parse_auth_log(log_file)
    
    top_subnet = None
    top_count = 0
    for subnet, count in subnet_failures.items():
        if count > top_count:
            top_count = count
            top_subnet = subnet
    
    if top_subnet is None:
        print("No valid failed login records found in the log file.")
        print("All lines may be malformed or there are no failed attempts.")
        # print(f"Debug failures: {debug_failures}")
        return
    
    subnet_base = top_subnet.split('/')[0][:-1]
    """
    inside that /24, find the most frequent source IP
    (all that are the same subnet https://www.digitalcitizen.life/what-is-24-in-ip-address/ )
    let L be its last octet and COUNT the total failures in that /24;
    form KEYPAD = "{L}{COUNT}".
    """
    top_ip = None
    top_ip_count = 0
    for ip, count in ip_failures.items():
        if ip.startswith(subnet_base):
            if count > top_ip_count:
                top_ip_count = count
                top_ip = ip
    
    last_octet = top_ip.split('.')[-1]
    keypad = last_octet + str(top_count)
    
    print("TOKEN[" + keypad + "]=<code>")
    print("EVIDENCE[" + keypad + "].TOP24=" + top_subnet)
    print("EVIDENCE[" + keypad + "].COUNT=" + str(top_count))
    print("EVIDENCE[" + keypad + "].SAMPLE=" + sample_lines[top_subnet])
    print("EVIDENCE[" + keypad + "].MALFORMED_SKIPPED=" + str(malformed_count))

if __name__ == "__main__":
    main()
