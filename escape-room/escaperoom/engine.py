import argparse
import json
import os
import sys
from typing import Callable, Dict, List, Optional

from escaperoom.rooms import (
    dns as dns_puzzle,
    final_gate,
    malware as malware_puzzle,
    soc as soc_puzzle,
    vault as vault_puzzle,
)


class GameState:
    def __init__(self):
        self.inventory: List[str] = []
        self.item_descriptions: Dict[str, str] = {}
        self.collected_tokens: Dict[str, str] = {}
        self.current_room: str = "lobby"
        self.game_won: bool = False
        self.game_started: bool = False
        self.transcript_file: Optional[str] = None
        self.transcript_tags = set()

    def add_item(self, item: str, description: str = "") -> None:
        if item not in self.inventory:
            self.inventory.append(item)
            if description:
                self.item_descriptions[item] = description

    def has_item(self, item: str) -> bool:
        return item in self.inventory

    def add_token(self, token_name: str, token_value: str) -> None:
        self.collected_tokens[token_name] = token_value

    def to_dict(self) -> Dict:
        return {
            "inventory": self.inventory,
            "item_descriptions": self.item_descriptions,
            "current_room": self.current_room,
            "game_won": self.game_won,
            "game_started": self.game_started,
        }

    def from_dict(self, data: Dict) -> None:
        self.inventory = data.get("inventory", [])
        self.item_descriptions = data.get("item_descriptions", {})
        self.current_room = data.get("current_room", "lobby")
        self.game_won = data.get("game_won", False)
        self.game_started = data.get("game_started", False)

    def set_transcript_file(self, filename: str) -> None:
        self.transcript_file = filename
        self.transcript_tags.clear()
        try:
            with open(filename, "w", encoding="utf-8"):
                pass
        except OSError as error:
            print(f"Warning: Could not initialize transcript: {error}", file=sys.stderr)

    def write_transcript(self, text: str) -> None:
        if self.transcript_file:
            try:
                with open(self.transcript_file, "a") as f:
                    for line in text.splitlines() or [""]:
                        tag = self._transcript_tag(line)
                        if tag and tag in self.transcript_tags:
                            continue
                        f.write(line + "\n")
                        if tag:
                            self.transcript_tags.add(tag)
            except Exception as e:
                print(f"Warning: Could not write to transcript: {e}", file=sys.stderr)

    @staticmethod
    def _transcript_tag(line: str) -> Optional[str]:
        if line.startswith(("TOKEN[", "EVIDENCE[")):
            return line.split("=", 1)[0] if "=" in line else None
        if line.startswith(("FINAL_GATE=", "MSG=", "HMAC=")):
            return line.split("=", 1)[0]
        return None


class Room:
    def __init__(
        self,
        name: str,
        description: str,
        interact_dialog: str,
        item_name: str,
        item_description: str,
        post_interact_dialog: str,
        inspectable_item: str,
        hint_dialog: Optional[str] = None,
        puzzle_solver: Optional[Callable[[], Optional[List[str]]]] = None,
    ):
        self.name = name
        self.description = description
        self.interact_dialog = interact_dialog
        self.item_name = item_name
        self.item_description = item_description
        self.post_interact_dialog = post_interact_dialog
        self.inspectable_item = inspectable_item
        self.hint_dialog = hint_dialog
        self.puzzle_solver = puzzle_solver
        self.interacted = False
        self.exits: Dict[str, str] = {}

    def add_exit(self, direction: str, room_name: str) -> None:
        self.exits[direction] = room_name

    def look(self) -> str:
        if self.interacted:
            return f"{self.post_interact_dialog}"
        return f"{self.name}.\n{self.description}"

    def inspect(self, item: str, game_state: GameState) -> str:
        if not self.inspectable_item:
            return "There's nothing here to inspect."
        if item.lower() == self.inspectable_item.lower():
            return self.interact(game_state)
        return f"You don't see a '{item}' here."

    def interact(self, game_state: GameState) -> str:
        if not self.item_name:
            return self.interact_dialog

        if self.interacted:
            return f"{self.post_interact_dialog}"

        result_lines = self.puzzle_solver() if self.puzzle_solver else []
        token_line = next(
            (line for line in result_lines or [] if line.startswith("TOKEN[")),
            None,
        )
        if self.puzzle_solver and token_line is None:
            raise ValueError(f"{self.name} puzzle did not produce a token.")

        self.interacted = True
        game_state.add_item(self.item_name, self.item_description)
        if token_line:
            token_name, token_value = token_line[len("TOKEN["):].split("]=", 1)
            game_state.add_token(token_name, token_value)
        output = [self.interact_dialog, *(result_lines or []), f"You acquired: {self.item_name}"]
        return "\n\n".join(output)
    
    def hint(self) -> str:
        if self.interacted:
            return "You feel an ominous wind that whispers 'You have already interacted with this room. OoOoOoOoOoO.'"
        if self.hint_dialog:
            return self.hint_dialog
        return "No hints available for this room."

class FinalRoom(Room):
    def __init__(self, data_dir: str = "data"):
        super().__init__(
            "An Ominous Gate that feels like a Final Gate",
            "A massive obelisk of silicon and wiring seemingly glares down at you in front of the gates. \n At its base, a you-sized-terminal can be seen. \n Feels like you need access from all security departments to go on...",
            "The obelisk whirrs to artificial life, its cold machinery scanning your hard-earned credentials...",
            "escape_key",
            "The final credential, strangely warm to the touch...",
            "As quickly as it started, the obelisk falls back into silence. \nAfter a definitively suspenseful pause you feel the ground rumbling as the massive gates slide open. \n With a fearful pace you go outside the massive gates and get blinded by the sudden sunlight. \n All you see as you look back is an empty field. Was this all a cybersecurity dream?",
            "terminal",
            "The obelisk seems to be scanning for your credentials. You can swear you hear it whispering 'You need all the tokens to proceed, then interact with the terminal. OoOoOoOoOo.'"
        )
        self.required_items = ["vault_token", "soc_token", "dns_token", "malware_token"]
        self.data_dir = data_dir

    def interact(self, game_state: GameState) -> str:
        missing_items = [item for item in self.required_items if not game_state.has_item(item)]

        if missing_items:
            return f"You try to interact with the you-sized-terminal. Try as you might, it seems you haven't managed to figure it out yet. \n You can swear you hear the wind, softly whispering 'You're missing: {', '.join(missing_items)}'. \n Thanks, wind."

        if self.interacted:
            return "Why would you try to come back get out live your life"

        missing_tokens = [
            token for token in ("DNS", "PID", "SAFE", "KEYPAD")
            if token not in game_state.collected_tokens
        ]
        if missing_tokens:
            return f"Missing puzzle evidence: {', '.join(missing_tokens)}"

        gate_lines = final_gate.solve_final_gate(
            os.path.join(self.data_dir, "final_gate.txt"),
            game_state.collected_tokens,
        )
        self.interacted = True
        game_state.add_item(self.item_name, self.item_description)
        game_state.game_won = True
        return (
            "\n".join(gate_lines)
            + "\n\n"
            + f"{self.interact_dialog}\n\nYou acquired: {self.item_name}"
            + "\n\nCongratulations! You've escaped the Cyber Escape Room!"
        )


class GameEngine:
    def __init__(self, data_dir: str = "data", transcript_file: Optional[str] = None):
        self.game_state = GameState()
        self.data_dir = data_dir
        if transcript_file:
            self.game_state.set_transcript_file(transcript_file)
        self.rooms: Dict[str, Room] = {}
        self.setup_rooms()

    def output(self, text: str, write_transcript: bool = True) -> None:
        print(text)
        if write_transcript:
            self.game_state.write_transcript(text)

    def setup_rooms(self) -> None:
        lobby = Room(
            "Lobby",
            "A helpful screen in the middle of this room blinks with marked arrows pointing at every door you can see. You can see that the doors are tagged soc, dns, vault, malware, final.",
            "The terminal displays valuable information, but no more. Would have been easier to put a sign outside each door, but you appreciate it nonetheless.",
            "",
            "",
            "The terminal continues to blink, waiting for your next move.",
            "terminal",
            "You feel an ominous wind that whispers 'You can see that the doors are tagged soc, dns, vault, malware, final. OoOoOoOoOoO.'"
        )
        lobby.add_exit("soc", "soc_desk")
        lobby.add_exit("dns", "dns_server")
        lobby.add_exit("vault", "vault_corridor")
        lobby.add_exit("malware", "malware_lab")
        lobby.add_exit("final", "final_gate")
        self.rooms["lobby"] = lobby

        vault = Room(
            "Vault Corridor",
            "As you open the door, you see an opulently decorated hallway of gold that leads to a cartoonishly massive vault.\n On a wall right next to the vault door, an over-decorated terminal can be seen. It's screen seems to show possible safe combinations.",
            "With a swift mind you manage to find the correct combination among a sea of fakes. \n Inputting it into the vault door's keypad, the vault hisses in response, hydraulic pistons struggling against the sheer weight of the door. \n As the vault door fully opens to reveal its contents, all you see inside is a single token. \n Seems like they spent whatever was in there decorating the hallway. \n Shame.",
            "vault_token",
            "A security token from the vault system. It is, regrettably, not as valuable as the hallway it came from.",
            "The vault terminal now displays 'ACCESS GRANTED'.\n You think about taking some of the golden decor with you, but sadly your pockets are exclusively for non-golden cybersecurity credentials.",
            "terminal",
            "You feel an ominous wind that whispers 'Interact with the terminal to find the combination. OoOoOoOoOoO.'",
            lambda: vault_puzzle.solve_vault(os.path.join(self.data_dir, "vault_dump.txt")),
        )
        vault.add_exit("lobby", "lobby")
        self.rooms["vault_corridor"] = vault

        soc = Room(
            "SOC Triage Desk",
            "As you open the door, you see a small office with a desk overburdened with a clutter of papers. \n As you go around the desk to get a better look, you manage to see a small monitor buried under the bureaucratic ocean of papers. \n You instinctively recognize the weird strings of text on screen as failed SSH login attempts.",
            "Seems like someone tried to attack this console, as if it wasn't burdened enough already by the piles of documents. \n You selflessly examine the authentication logs and identify the attack patterns, granting a brief respite to this humble system.",
            "soc_token",
            "A security token from the SOC system",
            "The screen now shows 'THREAT ANALYZED'. Due to cuts on this game's nonexistant budget you decide not to mess with the papers.",
            "monitor",
            "You feel an ominous wind that whispers 'Interact with the monitor to analyze the threat. OoOoOoOoOoO.'",
            lambda: soc_puzzle.solve_soc(os.path.join(self.data_dir, "auth.log")),
        )
        soc.add_exit("lobby", "lobby")
        self.rooms["soc_desk"] = soc

        dns = Room(
            "DNS Server Room",
            "As you open the door, you feel a gust of cold air hit you. \n You can see a room full of racks upon racks of server racks, a cacophony of tiny green lights blinking at random intervals. \n In the middle of the room you spot an unattended server console.",
            "With your massive brain you manage to analyze the DNS configuration and identify the resolution patterns. \n The green lights start blinking in unison, as if acknowledging your expertise.",
            "dns_token",
            "A security token from the DNS system",
            "The server console now displays 'NETWORK SECURED :)'.",
            "console",
            "You feel an ominous wind that whispers 'Interact with the console to view the DNS configuration. OoOoOoOoOoO.'",
            lambda: dns_puzzle.solve_dns(os.path.join(self.data_dir, "dns.cfg")),
        )
        dns.add_exit("lobby", "lobby")
        self.rooms["dns_server"] = dns

        malware = Room(
            "Malware Analysis Lab",
            "As you open the door, you see a room of white where even the air seems sterile, and you feel like you shouldn't touch anything inside. \n You probably will anyways, as you see multiple computer screens displaying the same process trees and execution traces.",
            "As careful as you can be to only touch what is necessary, you manage to examine the process relationships and identify the malware's execution flow. The analysis system validates your findings. \n It seems you've helped keep this system squeaky clean for one more day.",
            "malware_token",
            "A security token from the malware analysis system. \n It smells like disinfectant.",
            "The malware lab monitors now show 'THREAT NEUTRALIZED'. \n Looking around once more, you start wondering to yourself if it was really necessary to make this room feel like a chemical lab.",
            "screens",
            "You feel an ominous wind that whispers 'Interact with the screens to analyze the malware. OoOoOoOoOoO.'",
            lambda: self._solve_malware(),
        )
        malware.add_exit("lobby", "lobby")
        self.rooms["malware_lab"] = malware

        final_room = FinalRoom(self.data_dir)
        final_room.add_exit("lobby", "lobby")
        self.rooms["final_gate"] = final_room

    def _solve_malware(self) -> List[str]:
        lines = malware_puzzle.solve_malware(os.path.join(self.data_dir, "proc_tree.jsonl"))
        if lines is None:
            raise ValueError("The malware solver did not find an exfiltration token.")
        return lines

    def get_current_room(self) -> Room:
        return self.rooms[self.game_state.current_room]

    def print_intro(self) -> None:
        self.output("\n" + "=" * 60)
        self.output("Team 09's Cyber Escape Room")
        self.output("=" * 60)
        self.output("\nWelcome to the Cyber Escape Room!")
        self.output("You are a security analyst that woke up trapped in a seemingly high-tech facility.")
        self.output("Can you find a way to get out of this facility?")
        self.output("Use your cyber security knowledge to find your path!")
        self.output("\nType 'help' for available commands.")
        self.output("=" * 60 + "\n")

    def print_help(self) -> None:
        self.output("\nAvailable commands:")
        self.output("  look              - Look around the current room")
        self.output("  move <room>       - Move to another room")
        self.output("  inspect <item>    - Inspect an item in the room")
        self.output("  inventory         - Show collected tokens")
        self.output("  hint              - Show a hint for the current room")
        self.output("  save <file>       - Save your game")
        self.output("  load <file>       - Load your game")
        self.output("  quit              - Quit the game")
        self.output("")

    def process_command(self, command: str) -> bool:
        command = command.strip().lower()

        if not command:
            return True

        parts = command.split()
        cmd = parts[0]
        args = parts[1:] if len(parts) > 1 else []

        if cmd == "help":
            self.print_help()
        elif cmd == "look":
            self.output(self.get_current_room().look())
        elif cmd == "move":
            if not args:
                self.output("Move where?")
            else:
                self.handle_move(args[0])
        elif cmd == "inspect":
            if not args:
                self.output("Inspect what?")
            else:
                item = " ".join(args)
                self.output(self.get_current_room().inspect(item, self.game_state))
        elif cmd == "hint":
            self.output(self.get_current_room().hint())
        elif cmd == "inventory":
            self.show_inventory()
        elif cmd == "save":
            if not args:
                self.output("Save to what file?")
            else:
                self.save_game(args[0])
        elif cmd == "load":
            if not args:
                self.output("Load from what file?")
            else:
                self.load_game(args[0])
        elif cmd == "quit":
            return False
        else:
            self.output(f"Unknown command: '{cmd}'. Type 'help' for available commands.")

        return True

    def handle_move(self, room_name: str) -> None:
        current_room = self.get_current_room()

        if room_name in current_room.exits:
            new_room_name = current_room.exits[room_name]
            self.game_state.current_room = new_room_name
            new_room = self.get_current_room()
            entry_message = f"You enter the {new_room.name}."
            print(entry_message)
            self.game_state.write_transcript(entry_message)
            room_desc = new_room.look()
            print(room_desc)
            self.game_state.write_transcript(room_desc)
        else:
            self.output(f"You can't move to {room_name} from here.")

    def show_inventory(self) -> None:
        if not self.game_state.inventory:
            self.output("\nYou haven't collected any tokens yet.")
        else:
            self.output("\nCollected tokens:")
            for item in self.game_state.inventory:
                description = self.game_state.item_descriptions.get(item, "")
                if description:
                    self.output(f"  - {item}: {description}")
                else:
                    self.output(f"  - {item}")

    @staticmethod
    def _save_file_path(filename: str) -> Optional[str]:
        filename = filename.strip()
        if not filename:
            return None
        if os.path.splitext(filename)[1]:
            raise ValueError("Save/load name must not include a file extension.")
        return filename + ".txt"

    def save_game(self, filename: str) -> None:
        try:
            save_path = self._save_file_path(filename)
            if save_path is None:
                self.output("\nPlease provide a save name.")
                return
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self.game_state.to_dict(), f, indent=2)
            self.output(f"\nGame saved to {save_path}")
        except ValueError as e:
            self.output(f"\nInvalid save name: {e}")
        except Exception as e:
            self.output(f"\nError saving game: {e}")

    def load_game(self, filename: str) -> None:
        try:
            save_path = self._save_file_path(filename)
            if save_path is None:
                self.output("\nPlease provide a save name.")
                return
            if not os.path.exists(save_path):
                self.output(f"\nSave file '{save_path}' not found.")
                return

            with open(save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.game_state.from_dict(data)
            self.output(f"\nGame loaded from {save_path}")
            self.output(self.get_current_room().look())
        except ValueError as e:
            self.output(f"\nInvalid load name: {e}")
        except Exception as e:
            self.output(f"\nError loading game: {e}")

    def run(self) -> None:
        print("[Game] Cyber Escape Room started. Type 'help' for commands.")
        self.game_state.game_started = True
        room_desc = self.get_current_room().look()
        print(room_desc)
        self.game_state.write_transcript(room_desc)

        while True:
            try:
                command = input("\n> ").strip()
                self.game_state.write_transcript(f"> {command}")
                if not self.process_command(command):
                    print("\nThanks for playing!")
                    self.game_state.write_transcript("\nThanks for playing!")
                    break
            except KeyboardInterrupt:
                print("\n\nUse 'quit' to exit the game.")
            except EOFError:
                print("\n\nThanks for playing!")
                self.game_state.write_transcript("\n\nThanks for playing!")
                break


def main() -> None:
    parser = argparse.ArgumentParser(description="Cyber Escape Room - CLI Text Adventure Game")
    parser.add_argument("--start", choices=["intro"], help="Start the game (currently only 'intro' mode is supported)")
    parser.add_argument("--data", default="data", help="Data directory containing puzzle files")
    parser.add_argument("--transcript", default="run.txt", help="File to record game transcript (default: run.txt)")

    args = parser.parse_args()
    game = GameEngine(data_dir=args.data, transcript_file=args.transcript)
    game.run()


if __name__ == "__main__":
    main()
