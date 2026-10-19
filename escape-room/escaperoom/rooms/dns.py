import base64
import codecs
def read_config(filename):
    config = {}
    with open(filename, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "" or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            config[key.strip()] = value.strip()
    return config


def decode_value(value):
    encoding, payload = value.split(":", 1)
    if encoding == "b64":
        raw_bytes = base64.b64decode(payload)
    elif encoding == "rot13+b64":
        unrotated = codecs.decode(payload, "rot13")
        raw_bytes = base64.b64decode(unrotated)
    else:
        raise ValueError("Unknown encoding: " + encoding)
    return encoding, raw_bytes.decode("utf-8")


def solve_dns(filename):
    config = read_config(filename)
    tag_encoding, number = decode_value(config["token_tag"])
    key = "hint" + number
    encoding, sentence = decode_value(config[key])
    word = sentence.rstrip(".").split()[-1]
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
