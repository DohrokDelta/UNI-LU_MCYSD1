import hashlib
import hmac


def read_gate_file(filename):  # reads final_gate.txt: group_id, token_order and hmac_key
    settings = {}
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or "=" not in line:
                continue
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings


def build_message(group_id, token_order, tokens):  # builds the message like group09|token1-token2-token3-token4
    values = []
    for name in token_order:
        if name not in tokens:
            raise ValueError("Missing token: " + name)  # a room hasn't been solved yet
        values.append(tokens[name])
    return group_id + "|" + "-".join(values)


def compute_hmac(key, message):  # signs the message with the key using HMAC-SHA256
    return hmac.new(key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()  # hmac needs bytes so we encode both as utf-8


def solve_final_gate(filename, tokens):  # does the whole gate and returns the 3 transcript lines
    settings = read_gate_file(filename)
    token_order = [name.strip() for name in settings["token_order"].split(",")]  # "DNS,PID,SAFE,KEYPAD" -> ["DNS", "PID", "SAFE", "KEYPAD"]
    message = build_message(settings["group_id"], token_order, tokens)
    digest = compute_hmac(settings["hmac_key"], message)
    return [
        "FINAL_GATE=PENDING",
        f"MSG={message}",
        f"HMAC={digest}",
    ]



