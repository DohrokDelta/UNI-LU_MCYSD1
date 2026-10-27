import base64
import codecs
# reads dns.cfg into a dictionary, skipping comments and empty lines
def read_config(filename):
    config = {}
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # remove spaces and the newline at both ends
            if line == "" or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)  # split only at the FIRST =, base64 ends with = so we keep those
            config[key.strip()] = value.strip()
    return config

# undoes the encoding of one value, e.g. "b64:NQ==" -> ("b64", "5")
def decode_value(value):
    encoding, payload = value.split(":", 1)  # split at the first :
    if encoding == "b64":
        raw_bytes = base64.b64decode(payload)
    elif encoding == "rot13+b64":
        unrotated = codecs.decode(payload, "rot13")  # it was made text -> base64 -> rot13, so we undo rot13 first
        raw_bytes = base64.b64decode(unrotated)
    else:
        raise ValueError("Unknown encoding: " + encoding)
    return encoding, raw_bytes.decode("utf-8")  # bytes -> text, this also fails if it's not valid utf-8

# finds the real hint and returns the 4 transcript lines
def solve_dns(filename):
    config = read_config(filename)
    tag_encoding, number = decode_value(config["token_tag"])  # token_tag decodes to "5" so the real hint is hint5
    key = "hint" + number
    encoding, sentence = decode_value(config[key])
    word = sentence.rstrip(".").split()[-1]  # remove the full stop, split into words, take the last one -> sable
    return [
        f"TOKEN[DNS]={word}",
        f"EVIDENCE[DNS].KEY={key}",
        f"EVIDENCE[DNS].ENCODING={encoding}",
        f"EVIDENCE[DNS].DECODED_LINE={sentence}",
    ]


def main():
    for line in solve_dns("data/dns.cfg"):
        print(line)


if __name__ == "__main__":
    main()
