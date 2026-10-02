"""
REQUIREMENTS - Vault Corridor — vault_dump.txt
The file contains many candidates resembling:

SAFE{a-b-c}
Spacing can vary, but each candidate is contained on one physical line.

Tasks:

use a compiled regex to extract integer values a, b, and c;
tolerate optional whitespace around braces, numbers, and hyphens;
validate each candidate using a + b == c;
identify the single candidate satisfying the checksum.
The generator guarantees exactly one valid candidate.

Required transcript lines:

TOKEN[SAFE]=a-b-c
EVIDENCE[SAFE].MATCH="<actual matched text>"
EVIDENCE[SAFE].CHECK=a+b=c
EVIDENCE[SAFE].MATCH must preserve the spacing of the text that your regex matched.
"""

# Regex
import re

def main():
    #TODO REMOVE AND ADD TO GAME MENU
    log_file = "data/vault_dump.txt"
    
    # Setup the pattern
    pattern = re.compile(r'SAFE\s*\{\s*(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*\}')
    
    with open(log_file, 'r') as f:
        for line in f:
            # Only scan the lines that match the specified pattern
            match = pattern.search(line)
            if match:
                a = int(match.group(1))
                b = int(match.group(2))
                c = int(match.group(3))
                # Check if the line satisfies the requirements
                if a + b == c:
                    # Dump the result
                    print("TOKEN[SAFE]=" + str(a) + "-" + str(b) + "-" + str(c))
                    print("EVIDENCE[SAFE].MATCH=\"" + match.group(0) + "\"")
                    print("EVIDENCE[SAFE].CHECK=" + str(a) + "+" + str(b) + "=" + str(c))
                    break

if __name__ == "__main__":
    main()

