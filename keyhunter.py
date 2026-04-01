#!/usr/bin/env python3
import asyncio
import random
import string

from textual.app import App, ComposeResult
from textual.widgets import Static, RichLog, Input
from textual.containers import Horizontal
from textual import events

# ─── State ────────────────────────────────────────────────────────────────────

inv = {}
flags = {}
_KEYS = [
    "skeleton key(town)",
    "skeleton key(mine)",
    "skeleton key(lake)",
    "skeleton key(forest)",
]


def reset_state():
    global inv, flags
    inv = {
        "skeleton key(town)":   0,
        "skeleton key(mine)":   0,
        "skeleton key(lake)":   0,
        "skeleton key(forest)": 0,
        "lives":      3,
        "diving gear":  0,
        "ornate key":   0,
        "matches":      0,
        "pickaxe":      0,
        "machete":      0,
        "crowbar":      0,
        "grave clue":   0,
    }
    flags = {
        "crossroads_msg": "intro",
        "forest_visited": False,
        "mine_collapsed": False,
    }


# ─── Widgets ──────────────────────────────────────────────────────────────────

class StatusBar(Static):
    """Top bar: title, lives, key count."""

    def refresh_status(self):
        hearts = ("♥ " * inv.get("lives", 3) + "♡ " * (3 - inv.get("lives", 3))).strip()
        keys = sum(inv.get(k, 0) for k in _KEYS)
        self.update(f"  Keyhunter: The Lost Temple of Cranmore      {hearts}   Keys: {keys}/4")


class NarrativeLog(RichLog):
    """Scrollable story panel."""


class InventoryPanel(Static):
    """Always-visible inventory panel."""

    def refresh_inventory(self):
        lines = [
            "[bold cyan]INVENTORY[/bold cyan]",
            "[dim]─────────────────────[/dim]",
        ]
        for item, qty in inv.items():
            if item == "lives":
                continue
            if qty > 0:
                lines.append(f"[bold green]✓[/bold green]  [white]{item}[/white]")
            else:
                lines.append(f"[dim]✗  {item}[/dim]")
        self.update("\n".join(lines))


class ChoicesBar(Static):
    """Bottom bar: current prompt and key hints."""


# ─── App ──────────────────────────────────────────────────────────────────────

class KeyhunterApp(App):

    CSS = """
    Screen {
        background: #0d0d0d;
    }
    StatusBar {
        dock: top;
        height: 3;
        background: #0a1628;
        color: #00d4ff;
        text-style: bold;
        padding: 0 2;
        content-align: left middle;
    }
    #main-area {
        height: 1fr;
    }
    NarrativeLog {
        width: 65%;
        border: round #00d4ff;
        background: #050505;
        padding: 0 1;
        scrollbar-color: #00d4ff #0d0d0d;
    }
    InventoryPanel {
        width: 35%;
        border: round #00d4ff;
        background: #050505;
        padding: 1 2;
        color: #00ffff;
    }
    ChoicesBar {
        dock: bottom;
        height: 7;
        border: round #00ff41;
        background: #080808;
        color: #00ff41;
        padding: 1 2;
    }
    #text-input {
        dock: bottom;
        height: 3;
        border: round #ffff00;
        background: #080808;
        color: #ffff00;
        display: none;
    }
    #text-input.active {
        display: block;
    }
    ChoicesBar.hidden {
        display: none;
    }
    """

    def __init__(self):
        super().__init__()
        self._choice_queue: asyncio.Queue = asyncio.Queue()
        self._text_queue: asyncio.Queue = asyncio.Queue()
        self._valid_options: list = []
        self._awaiting_key: bool = False
        self._awaiting_text: bool = False

    def compose(self) -> ComposeResult:
        yield StatusBar("  Keyhunter: The Lost Temple of Cranmore", id="status")
        with Horizontal(id="main-area"):
            yield NarrativeLog(highlight=True, markup=True, id="narrative")
            yield InventoryPanel("", id="inventory")
        yield ChoicesBar("", id="choices")
        yield Input(placeholder="Type here and press Enter...", id="text-input")

    def on_mount(self) -> None:
        self.query_one(InventoryPanel).refresh_inventory()
        self.run_worker(self._main_loop(), exclusive=True)

    # ── Widget shortcuts ──────────────────────────────────────────────────────

    @property
    def _narrative(self) -> NarrativeLog:
        return self.query_one(NarrativeLog)

    @property
    def _inv_panel(self) -> InventoryPanel:
        return self.query_one(InventoryPanel)

    @property
    def _status(self) -> StatusBar:
        return self.query_one(StatusBar)

    @property
    def _choices(self) -> ChoicesBar:
        return self.query_one(ChoicesBar)

    # ── Output helpers ────────────────────────────────────────────────────────

    def write(self, msg: str = ""):
        """Write a line to the narrative panel."""
        self._narrative.write(msg)

    def write_event(self, msg: str):
        """Yellow discovery / event line."""
        self._narrative.write(f"[bold yellow]  ★  {msg}[/bold yellow]")

    def write_warning(self, msg: str):
        """Red danger / warning line."""
        self._narrative.write(f"[bold red]  !  {msg}[/bold red]")

    def set_location(self, title: str):
        """Clear the narrative and stamp a new location header."""
        self._narrative.clear()
        self._narrative.write(f"\n[bold cyan]{'─' * 50}[/bold cyan]")
        self._narrative.write(f"[bold cyan]  {title}[/bold cyan]")
        self._narrative.write(f"[bold cyan]{'─' * 50}[/bold cyan]\n")

    def refresh_inventory(self):
        self._inv_panel.refresh_inventory()
        self._status.refresh_status()

    # ── Input helpers ─────────────────────────────────────────────────────────

    async def get_choice(self, prompt: str, valid_options: list) -> int:
        """Show a prompt and wait for the player to press a valid number key."""
        self._valid_options = valid_options
        self._awaiting_key = True
        opts = "   ".join(f"[bold green][{o}][/bold green]" for o in valid_options)
        self._choices.update(f"[green]{prompt}[/green]\n\n  {opts}")
        result = await self._choice_queue.get()
        self._awaiting_key = False
        self._choices.update("")
        return result

    async def get_text(self, prompt: str) -> str:
        """Show the inline input bar and wait for a text submission."""
        text_input = self.query_one("#text-input", Input)
        self._choices.add_class("hidden")
        self._awaiting_text = True
        text_input.placeholder = prompt
        text_input.value = ""
        text_input.add_class("active")
        text_input.focus()
        result = await self._text_queue.get()
        self._awaiting_text = False
        text_input.remove_class("active")
        self._choices.remove_class("hidden")
        self.query_one(NarrativeLog).focus()
        return result

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        await self._text_queue.put(event.value.strip())
        event.input.value = ""

    async def on_key(self, event: events.Key) -> None:
        if self._awaiting_key and not self._awaiting_text and event.key.isdigit():
            choice = int(event.key)
            if choice in self._valid_options:
                await self._choice_queue.put(choice)
                event.stop()

    # ── Game helpers ──────────────────────────────────────────────────────────

    def update_inventory(self, item: str, quantity: int = 1):
        if item in inv:
            inv[item] += quantity
            self.write_event(f"Obtained: {item}")
            self.refresh_inventory()

    def take_damage(self):
        inv["lives"] -= 1
        flags["crossroads_msg"] = "death"
        self.refresh_inventory()

    # ── Top-level loop ────────────────────────────────────────────────────────

    async def _main_loop(self):
        while True:
            if not await self._menu():
                self.exit()
                return
            play_again = True
            while play_again:
                play_again = await self._run_game()

    async def _menu(self) -> bool:
        """Main menu. Returns True when the player starts a game."""
        self.set_location("KEYHUNTER: THE LOST TEMPLE OF CRANMORE")
        self.write("[bold red]  Welcome to Keyhunter: The Lost Temple of Cranmore[/bold red]\n")
        while True:
            choice = await self.get_choice(
                "Start[1]  How-to[2]  Credits[3]  Winners[4]  Quit[5]",
                [1, 2, 3, 4, 5],
            )
            if choice == 1:
                name = await self.get_text("Please enter your name:")
                self.write(f"\n[bold white]Welcome, {name or 'Stranger'}![/bold white]\n")
                await asyncio.sleep(1)
                return True
            elif choice == 2:
                self._show_howto()
            elif choice == 3:
                self._show_credits()
            elif choice == 4:
                self._show_winners()
            elif choice == 5:
                return False

    def _show_howto(self):
        self.write("\n[bold cyan]── HOW TO PLAY ──────────────────────────────────[/bold cyan]")
        self.write("  Keyhunter is a text-based adventure game.")
        self.write("  Press the number next to each option to make your choice.")
        self.write("  Find all four skeleton key parts to win.")
        self.write("  Dangers are flagged in red before you commit.\n")

    def _show_credits(self):
        self.write("\n[bold cyan]── DEVELOPERS ───────────────────────────────────[/bold cyan]")
        self.write("  Oisin Singleton")
        self.write("  Conor Lacey")
        self.write("  Andre Norton\n")

    def _show_winners(self):
        self.write("\n[bold cyan]── PREVIOUS WINNERS ─────────────────────────────[/bold cyan]")
        try:
            with open("winners.txt", "r", encoding="utf-8") as f:
                wlist = f.readlines()
            if wlist:
                for w in wlist:
                    self.write(f"  [yellow]{w.strip()}[/yellow]")
            else:
                self.write("  No winners yet!")
        except FileNotFoundError:
            self.write("  No winners file found.")
        self.write("")

    async def _run_game(self) -> bool:
        """Single playthrough. Returns True if the player wants to play again."""
        reset_state()
        self.refresh_inventory()
        location = "crossroads"
        while location not in ("WIN", "LOSE"):
            location = await LOCATIONS[location](self)
        if location == "WIN":
            return await self._screen_win()
        else:
            return await self._screen_lose()

    async def _screen_win(self) -> bool:
        self.set_location("── YOU WIN! ──────────────────────────────────────")
        self.write("[bold yellow]")
        self.write("     .--------.     ")
        self.write("   .'          '.   ")
        self.write("  /   O      O   \\  ")
        self.write(" :                : ")
        self.write(" |                | ")
        self.write(" : ',          ,' : ")
        self.write("  \\  '-......-'  /  ")
        self.write("   '.          .'   ")
        self.write("     '-......-'     [/bold yellow]")
        self.write("")
        name = await self.get_text("Enter your name for the winners list:")
        with open("winners.txt", "a", encoding="utf-8") as f:
            f.write((name or "Anonymous") + "\n")
        self.write_event(f"{name or 'Anonymous'} added to the winners list!")
        choice = await self.get_choice("Play again?  Yes[1]  No[2]", [1, 2])
        return choice == 1

    async def _screen_lose(self) -> bool:
        self.set_location("── YOU LOSE ──────────────────────────────────────")
        self.write("[bold yellow]")
        self.write("     .--------.     ")
        self.write("   .'          '.   ")
        self.write("  /   O      O   \\  ")
        self.write(" :           `    : ")
        self.write(" |                | ")
        self.write(" :    .------.    : ")
        self.write("  \\  '        '  /  ")
        self.write("   '.          .'   ")
        self.write("     '-......-'     [/bold yellow]")
        self.write("")
        choice = await self.get_choice("Play again?  Yes[1]  No[2]", [1, 2])
        return choice == 1


# ─── Minigames ────────────────────────────────────────────────────────────────

async def digging_game(app: KeyhunterApp):
    """Random-word digging minigame."""
    words = ["dig", "shovel", "scoop", "delve", "unearth"]
    word = random.choice(words)
    for i in range(1, 6):
        response = await app.get_text(f"[{i}/5] Type '{word}' to dig down into the grave:")
        while response != word:
            app.write(f"  Literally just type '{word}'...")
            response = await app.get_text(f"[{i}/5] Type '{word}':")
        app.write("  You dig the grave.")


async def elevator_game(app: KeyhunterApp):
    """Random-sequence elevator escape minigame."""
    seq = "".join(random.choices(string.ascii_lowercase, k=4))
    app.write_warning("Quick! Pull yourself free from the web!")
    app.write(f"  Enter this sequence: [bold yellow]{seq.upper()}[/bold yellow]")
    app.write("  (Type the full sequence and press Enter)\n")
    for i in range(1, 4):
        response = await app.get_text(f"[{i}/3] Enter the sequence:")
        while response != seq:
            app.write_warning("The webs tighten around you!")
            response = await app.get_text(f"[{i}/3] Enter the sequence:")
        app.write("  You pull hard on the ropes.")
    app.write("\n[bold green]You burst free and scramble to the top of the shaft![/bold green]")


# ─── Locations ────────────────────────────────────────────────────────────────
# Each async function receives the app, renders its scene, returns a location string.

async def loc_crossroads(app: KeyhunterApp):
    msg = flags["crossroads_msg"]
    flags["crossroads_msg"] = "returning"
    app.set_location("THE CROSSROADS")
    if msg == "death":
        if inv["lives"] <= 0:
            return "LOSE"
        app.write_warning("You wake up, your head is pounding.")
        app.write("You're back at the crossroads once again.")
        lives_word = "life" if inv["lives"] == 1 else "lives"
        app.write(f"Maybe you should be more careful — you only have {inv['lives']} {lives_word} left!")
    elif msg == "intro":
        app.write("You wake up at a crossroads with no memory of how you got there.")
    else:
        app.write("You look at the signpost.")
    app.write("\n  [cyan]North[/cyan] — Cranmore Town")
    app.write("  [cyan]South[/cyan] — Old Steel Mine")
    app.write("  [cyan]East[/cyan]  — Lacey Lake")
    app.write("  [cyan]West[/cyan]  — Cranmore Forest")
    choice = await app.get_choice("\nHead North[1] / South[2] / East[3] / West[4]:", [1, 2, 3, 4])
    return ["town", "mine", "lake", "forest"][choice - 1]


# ── Town ──────────────────────────────────────────────────────────────────────

async def loc_town(app: KeyhunterApp):
    app.set_location("CRANMORE TOWN")
    app.write("You wander into the small town. The place is seemingly deserted....")
    await asyncio.sleep(0.7)
    app.write("The place makes you feel uneasy... You see 3 buildings worth exploring.\n")
    app.write("  [cyan]Straight[/cyan] — The inn")
    app.write("  [cyan]Left[/cyan]     — The church")
    app.write("  [cyan]Right[/cyan]    — The burnt down house")
    choice = await app.get_choice("\nGo Straight[1] / Left[2] / Right[3] / Back[4]:", [1, 2, 3, 4])
    return ["town_inn", "town_church", "town_bhouse", "crossroads"][choice - 1]


async def loc_town_bhouse(app: KeyhunterApp):
    app.set_location("THE BURNT HOUSE")
    app.write("You walk into the burnt down house. The house is a complete mess.")
    app.write("A small charred locker sits in the corner with a statue of a cross on top.")
    choice = await app.get_choice("\nDo you open the locker?  Yes[1]  No[2]:", [1, 2])
    if choice == 1:
        app.write("\nYou open the top drawer...")
        if inv["ornate key"] == 1:
            app.write("There is nothing left here.")
        else:
            app.write("You find an ornate key.")
            app.update_inventory("ornate key")
    app.write("\nYou leave the burnt down house for the town center.")
    return "town"


async def loc_town_church(app: KeyhunterApp):
    app.set_location("THE CHURCH")
    app.write("You arrive at an old church.")
    app.write("You try the door, but it is locked. It looks like it requires some sort of key?")
    if inv["ornate key"] == 1:
        app.write("\nYou use the key you found in the house.")
        await asyncio.sleep(0.7)
        app.write("The key opens the door to the church.")
        await asyncio.sleep(0.7)
        app.write("You explore the church and find a skeleton key on the altar.")
        if inv["skeleton key(town)"] == 1:
            app.write("You already have the key!")
        else:
            app.update_inventory("skeleton key(town)")
    else:
        app.write("\nYou cannot get through the front door and decide to try another way.")
        await asyncio.sleep(0.7)
        app.write("You look around the back of the church and find an entrance to the basement.")
        await asyncio.sleep(0.7)
        app.write_warning("The way is poorly lit and a burst pipe has covered the stairs in treacherous water. Very dangerous!")
        cs = await app.get_choice("Do you proceed?  Yes[1]  No[2]:", [1, 2])
        if cs == 1:
            slip_chance = 0.15 if inv["matches"] == 1 else 0.60
            if random.random() < slip_chance:
                app.write("\nYou walk down the stairs and slip, hitting your head on a step.")
                app.take_damage()
                return "crossroads"
            else:
                app.write("\nYou pick your way carefully down the stairs. Dark and damp, but you make it.")
                app.write("There's nothing useful down here. You head back up.")
    app.write("\nYou leave the church for the town center.")
    return "town"


async def loc_town_inn(app: KeyhunterApp):
    app.set_location("THE INN")
    app.write("You explore the inn.")
    app.write("The place is cozy and looks like a decent place for a drink, but you don't have the time...")
    if inv["lives"] < 3:
        app.write("A carvery appears on the table in front of you. You think someone is playing tricks on you.")
        app.write("You eat the carvery, knowing your mom might not be too happy since she has dinner ready.")
        inv["lives"] += 1
        app.refresh_inventory()
        app.write_event(f"You gain a life! You now have {inv['lives']} lives.")
    else:
        app.write("A carvery appears on the table in front of you.")
        app.write("You know your mom has dinner ready, and you're not too hungry.")
        app.write("You leave the carvery alone and leave.")
    app.write("\nYou leave the inn for the town center.")
    return "town"


# ── Forest ────────────────────────────────────────────────────────────────────

async def loc_forest(app: KeyhunterApp):
    app.set_location("CRANMORE FOREST — THE CLEARING")
    await asyncio.sleep(0.5)
    if not flags["forest_visited"]:
        flags["forest_visited"] = True
        app.write("As you walk down the beaten path, the trees begin to rise higher and higher around you.")
        app.write("The tallest of them stretch up almost touching the sky.")
        app.write("You come to a small clearing with a better view of the forest.")
    else:
        app.write("You're back at the small clearing.")
    await asyncio.sleep(0.5)
    app.write("\n  [cyan]Left[/cyan]     — An abandoned manor in the distance")
    app.write("  [cyan]Straight[/cyan] — An overgrown graveyard at the edge of the clearing")
    app.write("  [cyan]Right[/cyan]    — Darkness, but a low hum draws you in")
    choice = await app.get_choice("\nGo Left[1] / Straight[2] / Right[3] / Back[4]:", [1, 2, 3, 4])
    if choice == 1:
        return "forest_manor"
    elif choice == 2:
        if inv["skeleton key(forest)"] == 1:
            app.write("You already found what you needed in there.")
            return "forest"
        return "forest_graveyard"
    elif choice == 3:
        return "forest_temple"
    else:
        return "crossroads"


async def loc_forest_manor(app: KeyhunterApp):
    app.set_location("THE ABANDONED MANOR")
    await asyncio.sleep(0.5)
    app.write("The manor's front door is bolted shut.")
    app.write("Around the back: the door is slightly ajar, and there's a small wooden shed at the end of the garden.")
    choice = await app.get_choice("\n[1] Try the back door   [2] Check out the shed   [3] Head back:", [1, 2, 3])
    if choice == 1:
        if inv["crowbar"] == 1:
            app.write("\nYou lever the door open with the crowbar.")
            return "forest_manor_kitchen"
        else:
            app.write_warning("The door is jammed tight. You'll need something to pry it open.")
            return "forest_manor"
    elif choice == 2:
        return "forest_manor_shed"
    else:
        return "forest"


async def loc_forest_manor_shed(app: KeyhunterApp):
    app.set_location("THE GARDEN SHED")
    await asyncio.sleep(0.5)
    if inv["crowbar"] == 1:
        app.write("Nothing else useful in the shed. You head back to the manor.")
        await asyncio.sleep(1)
    else:
        app.write("The shed door is hanging off at an angle; you easily pull it off completely. Wow, you're massive.")
        app.write("The smell of mold hits your nose as you step into the shed.")
        app.write("You now realize the entire roof is being propped up by just a few branches.")
        await asyncio.sleep(2)
        app.update_inventory("crowbar")
        app.write("You head back to the manor.")
        await asyncio.sleep(1)
    return "forest_manor"


async def loc_forest_manor_kitchen(app: KeyhunterApp):
    app.set_location("MANOR — KITCHEN")
    await asyncio.sleep(1)
    app.write("The air in the kitchen is stale, and there is a thick coating of dust on all surfaces.")
    app.write("This place is mad creepy.")
    if inv["matches"] == 0:
        app.write("\nYou check the drawers for something to light the way and find an old box of matches, somehow still dry.")
        app.update_inventory("matches")
    app.write("You use the matches to light the candles around the room. Handy that they were just lying around.")
    app.write("\nYou can see two doorways: one leads to a living room, the other to a hallway.")
    choice = await app.get_choice("\n[1] Go into the hallway   [2] The living room   [3] Leave the manor:", [1, 2, 3])
    if choice == 1:
        app.write_warning("You step into the hallway. The floorboards give way and you plummet into the darkness below.")
        app.take_damage()
        return "crossroads"
    elif choice == 2:
        return "forest_manor_living"
    else:
        return "forest_manor"


async def loc_forest_manor_living(app: KeyhunterApp):
    app.set_location("MANOR — LIVING ROOM")
    await asyncio.sleep(0.5)
    app.write("The living room is thick with dust. Old furniture sits under white sheets.")
    app.write("Hunting trophies line the walls and a cold fireplace dominates the far end of the room.")
    if inv["machete"] == 0:
        app.write("\nA large machete hangs above the fireplace, surprisingly well-maintained.")
        app.update_inventory("machete")
        app.write("You take it. Could come in handy.")
    if inv["grave clue"] == 0:
        app.write("\nAn old journal sits open on the coffee table. One entry catches your eye:")
        await asyncio.sleep(1)
        app.write('\n  [italic]"...buried the old key with D.R. in the forest graveyard. God rest him."[/italic]\n')
        await asyncio.sleep(1)
        app.update_inventory("grave clue")
        app.write("You pocket the journal.")
    choice = await app.get_choice("\n[1] Head back to the kitchen   [2] Leave the manor:", [1, 2])
    return "forest_manor_kitchen" if choice == 1 else "forest_manor"


async def loc_forest_graveyard(app: KeyhunterApp):
    app.set_location("THE GRAVEYARD")
    await asyncio.sleep(1)
    app.write("You walk into the graveyard. The graves are overgrown, and most of the tombstones are falling apart.")
    app.write("You try to read some of the headstones, but the engravings are long worn away.")
    if inv["grave clue"] == 1:
        await asyncio.sleep(1)
        app.write("\nOne of the graves catches your eye.")
        await asyncio.sleep(1)
        app.write("")
        app.write("              ____")
        app.write("             (    )")
        app.write("             __)(__")
        app.write("       _____/      \\_____")
        app.write("      |  _     ___   _   ||")
        app.write("      | | \\     |   | \\  ||")
        app.write("      | |  |    |   |  | ||")
        app.write("      | |_/     |   |_/  ||")
        app.write("      | | \\     |   |    ||")
        app.write("      | |  \\    |   |    ||")
        app.write("      | |   \\. _|_. | .  ||")
        app.write("      |                  ||")
        app.write("      |  What you seek   ||")
        app.write("      |  lies beneath    ||")
        app.write("      | *   **    * **   |**      **")
        app.write(" \\))ejm97/.,(//,,..,,\\||(,,.,\\\\,.((//")
        await asyncio.sleep(2)
        app.write("\nYou look around the grave for something to dig with.")
        app.write("A shovel is sitting right next to it. That was handy, wasn't it?")
        await digging_game(app)
        app.write("\nFinally, the shovel hits wood. Clearing off the top dirt, you open up the coffin below.")
        await asyncio.sleep(1)
        app.write("\nInside the coffin is completely empty except for a small cloth bag.")
        app.write("You reach down and grab the bag. Looking inside, you find part of a skeleton key!")
        await asyncio.sleep(1)
        app.update_inventory("skeleton key(forest)")
        app.write("\nThis place is giving you the creeps. You leave.")
    else:
        app.write("\nThe graveyard is cold and eerie. The tombstones you can read have cryptic messages")
        app.write("on them which mean nothing to you. You leave the graveyard for now.")
        await asyncio.sleep(1)
    return "forest"


async def loc_forest_temple(app: KeyhunterApp):
    app.set_location("THE LOST TEMPLE OF CRANMORE")
    app.write("You arrive at the temple. The entrance is blocked by thick vines.")
    if inv["machete"] == 0:
        app.write_warning("You'll need to find something to cut through the vines.")
        return "forest"
    app.write("You hack through the vines with the machete.")
    missing = [k for k in _KEYS if inv[k] == 0]
    if missing:
        app.write_warning("The temple door has four locks. You are still missing:")
        for k in missing:
            app.write(f"    [red]—[/red] {k}")
        return "forest"
    app.write_event("You have all four skeleton keys!")
    app.write("You fit them into the four locks on the temple door one by one.")
    await asyncio.sleep(1)
    app.write("The door grinds open with a deep rumble. You step inside.")
    await asyncio.sleep(1)
    app.write("\nA shaft of light cuts through the dust onto a stone pedestal.")
    app.write("[bold yellow]The Lost Temple of Cranmore has been found. You have won the game!!![/bold yellow]")
    return "WIN"


# ── Lake ──────────────────────────────────────────────────────────────────────

async def loc_lake(app: KeyhunterApp):
    app.set_location("LACEY LAKE")
    app.write("You walk towards the lake.")
    await asyncio.sleep(1)
    if inv["diving gear"] == 1 and inv["skeleton key(lake)"] == 0:
        app.write("The water here looks deep. Something shimmers at the bottom.")
        app.write("You strap on the diving gear and plunge in.")
        await asyncio.sleep(1)
        app.write("You find a skeleton key at the bottom of the lake!")
        app.update_inventory("skeleton key(lake)")
    elif inv["skeleton key(lake)"] == 1:
        app.write("You have already been here, and there is nothing left to explore!")
    else:
        app.write("The water here looks deep. You see something shimmer at the bottom.")
        app.write_warning("Maybe if you had diving gear you could get to it?")
        app.write("You go back to the crossroads.")
    await asyncio.sleep(1)
    return "crossroads"


async def loc_lake_from_mine(app: KeyhunterApp):
    app.set_location("LACEY LAKE")
    app.write("After feeling your way through the darkness of the underwater tunnels, you emerge")
    app.write("and find yourself in the middle of Lacey Lake.")
    app.write("You notice something glimmering in the depths of the lake.")
    dive = await app.get_choice("\nDive down and give it a go?  Yes[1]  No[2]:", [1, 2])
    if dive == 1:
        app.write("The mammy wanted you in for 9, so you decide not to waste your valuable game time.")
    else:
        app.write("Haha, you think you're going back to those crossroads empty-handed? The mammy wouldn't be impressed, I tell ya.")
    app.write("You dive down and find a key!")
    app.update_inventory("skeleton key(lake)")
    return "crossroads"


# ── Mine ──────────────────────────────────────────────────────────────────────

async def loc_mine(app: KeyhunterApp):
    app.set_location("THE OLD STEEL MINE")
    await asyncio.sleep(0.5)
    if inv["skeleton key(mine)"] == 1:
        app.write("You have already explored this mine, and the entrance is caved in.")
        app.write("You head back to the crossroads.")
        return "crossroads"
    if flags["mine_collapsed"]:
        app.write("The entrance is caved in but you squeeze through a gap in the rubble.")
        await asyncio.sleep(1)
        return "mine_routes"
    app.write("The mine feels eerie, but you press on to see if there is anything of interest inside.")
    app.write_warning("Without a source of light, it's impossible to proceed further.")
    choice = await app.get_choice("Try to find a light[1]  Leave for now[2]:", [1, 2])
    if choice == 2:
        app.write("\nYou decide to return later when you feel more prepared.")
        app.write("You leave the mine and return to the crossroads.")
        return "crossroads"
    app.write("\nYou search for a while and uncover an old torch hidden behind overgrown vines.")
    if inv["matches"] == 0:
        app.write_warning("You cannot continue — you're missing a valuable item to ignite the torch.")
        app.write("You should return when you have located the item.")
        await asyncio.sleep(2)
        app.write("You leave the mine and return to the crossroads.")
        return "crossroads"
    light = await app.get_choice("Light the torch?  Yes[1]  No[2]:", [1, 2])
    if light == 2:
        app.write("\nYou leave the mine for now and head back to the crossroads.")
        await asyncio.sleep(1)
        return "crossroads"
    app.write("\nYou light the torch using the matches in your inventory...")
    await asyncio.sleep(2)
    return "mine_collapse"


async def loc_mine_collapse(app: KeyhunterApp):
    app.set_location("THE OLD STEEL MINE — DEEP")
    flags["mine_collapsed"] = True
    app.write("[bold]!!!!Rumble!!!![/bold]\n")
    app.write("Suddenly you hear a loud rumbling behind you!")
    await asyncio.sleep(2)
    app.write("  *-------------------------------------------* ")
    app.write("  *           _.-^^---....,,.._               * ")
    app.write("  *       _--                  --_            * ")
    app.write("  *      (<                      >)           * ")
    app.write("  *       |                      |            * ")
    app.write("  *        \\._                _./             * ")
    app.write("  *          ``--. . , ; .-''                 * ")
    app.write("  *              |  |   |                     * ")
    app.write("  *           .-=||  |  |=-.                  * ")
    app.write("  *            \\*--------*/                   * ")
    app.write("  *              | ;  : |                     * ")
    app.write("  *           ###o0o0o0o0###                  * ")
    app.write("  *-------------------------------------------* ")
    await asyncio.sleep(1)
    app.write("\nYou fall forward and realize the exit is blocked. There's no escape.")
    await asyncio.sleep(1)
    app.write("\nYou have no choice but to continue ahead.")
    await asyncio.sleep(2)
    app.write("\nAs you're walking, the floor beneath you collapses!")
    await asyncio.sleep(3)
    app.write("\nYou wake up in a new area with four routes ahead.")
    return "mine_routes"


async def loc_mine_routes(app: KeyhunterApp):
    app.set_location("THE OLD STEEL MINE — JUNCTION")
    while True:
        app.write("  [1] Water route")
        app.write("  [2] Spider-web route")
        app.write("  [3] Mine cart route")
        app.write("  [4] The cliff\n")
        choice = await app.get_choice("Which route do you take?", [1, 2, 3, 4])
        if choice == 4:
            app.write("\nThere seems to be a fourth way, but it's a large drop. You decide to choose another way.\n")
        elif choice == 1:
            app.write_warning("The water route is too deep to navigate without equipment. Choose another way.\n")
        elif choice == 2:
            app.write("\nYou have decided to take the spider-web route.")
            app.write("\nBattling the webs, you find yourself face-to-face with a giant spider!")
            await asyncio.sleep(2)
            app.write(" ______________________________  ")
            app.write("| -*-*-*-*-*       *-*-*-*-*-  | ")
            app.write("|  __-----__       __-----__   | ")
            app.write("|-   ( 0 )   -   -   ( 0 )   - | ")
            app.write("| '---------'     '---------'  | ")
            app.write("|______________________________| ")
            await asyncio.sleep(1)
            app.write("\nYou dash to a nearby tunnel, escaping the spider.")
            app.write("You find a skeleton holding a chest containing diving gear and a pickaxe!")
            if inv["pickaxe"] == 0:
                inv["pickaxe"] += 1
            if inv["diving gear"] == 0:
                inv["diving gear"] += 1
            app.refresh_inventory()
            app.write("\nYou quickly run to the next tunnel, which leads to an elevator.")
            return "mine_elevator"
        else:
            app.write("\nYou take the mine cart down a thrilling ride, landing at the bottom!")
            app.write("You find a skeleton holding diving gear and a pickaxe.")
            if inv["pickaxe"] == 0:
                inv["pickaxe"] += 1
            if inv["diving gear"] == 0:
                inv["diving gear"] += 1
            app.refresh_inventory()
            app.write("\nA giant spider appears! You escape to a nearby tunnel leading to an elevator.")
            return "mine_elevator"


async def loc_mine_elevator(app: KeyhunterApp):
    app.set_location("MINE — ELEVATOR SHAFT")
    await elevator_game(app)
    return "mine_fight"


async def loc_mine_fight(app: KeyhunterApp):
    app.set_location("MINE — SPIDER ENCOUNTER")
    app.write("A giant spider lunges at you from the shadows. You must act quickly!")
    choice = await app.get_choice("\nUse:  Diving gear[1]  Matches[2]  Pickaxe[3]:", [1, 2, 3])
    if choice == 3:
        app.write_event("You swing the pickaxe with all your strength, killing the spider!")
        app.update_inventory("skeleton key(mine)")
        app.write("You put on your diving gear and swim through an underwater tunnel.")
        return "lake_from_mine"
    else:
        app.write_warning("Your attempt to fend off the spider fails. The spider attacks and you lose a life.")
        app.write("You barely escape, dragging yourself back through the mine.")
        app.take_damage()
        return "crossroads"


# ─── Dispatch table ───────────────────────────────────────────────────────────

LOCATIONS = {
    "crossroads":           loc_crossroads,
    "town":                 loc_town,
    "town_inn":             loc_town_inn,
    "town_church":          loc_town_church,
    "town_bhouse":          loc_town_bhouse,
    "forest":               loc_forest,
    "forest_manor":         loc_forest_manor,
    "forest_manor_shed":    loc_forest_manor_shed,
    "forest_manor_kitchen": loc_forest_manor_kitchen,
    "forest_manor_living":  loc_forest_manor_living,
    "forest_graveyard":     loc_forest_graveyard,
    "forest_temple":        loc_forest_temple,
    "lake":                 loc_lake,
    "lake_from_mine":       loc_lake_from_mine,
    "mine":                 loc_mine,
    "mine_collapse":        loc_mine_collapse,
    "mine_routes":          loc_mine_routes,
    "mine_elevator":        loc_mine_elevator,
    "mine_fight":           loc_mine_fight,
}


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    KeyhunterApp().run()
