import hashlib
import hmac


def read_gate_file(filename):
    settings = {}
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or "=" not in line:
                continue
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings


def build_message(group_id, token_order, tokens):
    values = []
    for name in token_order:
        if name not in tokens:
            raise ValueError("Missing token: " + name)
        values.append(tokens[name])
    return group_id + "|" + "-".join(values)


def compute_hmac(key, message):
    return hmac.new(key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()


def solve_final_gate(filename, tokens):
    settings = read_gate_file(filename)
    token_order = [name.strip() for name in settings["token_order"].split(",")]
    message = build_message(settings["group_id"], token_order, tokens)
    digest = compute_hmac(settings["hmac_key"], message)
    return [
        "FINAL_GATE=PENDING",
        f"MSG={message}",
        f"HMAC={digest}",
    ]



