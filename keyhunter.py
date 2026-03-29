#!/usr/bin/env python3
import os
import time
import random
import string

# ─── State ────────────────────────────────────────────────────────────────────

inv = {}
flags = {}

def reset_state():
    global inv, flags
    inv = {
        "skeleton key(town)":   0,
        "skeleton key(mine)":   0,
        "skeleton key(lake)":   0,
        "skeleton key(forest)": 0,
        "lives":    3,
        "diving gear": 0,
        "ornate key":  0,
        "matches":     0,
        "pickaxe":     0,
        "machete":     0,
        "crowbar":     0,
        "grave clue":  0,
    }
    flags = {
        "crossroads_msg":  "intro",
        "forest_visited":  False,
        "mine_collapsed":  False,
    }

# ─── Display helpers ──────────────────────────────────────────────────────────

_KEYS = ["skeleton key(town)", "skeleton key(mine)", "skeleton key(lake)", "skeleton key(forest)"]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def header(title):
    """Bold cyan location header — printed at the top of every screen."""
    W = 50
    print(f"\033[1;36m{'─' * W}\033[0m")
    print(f"\033[1;36m  {title}\033[0m")
    print(f"\033[1;36m{'─' * W}\033[0m\n")

def event(msg):
    """Yellow highlight for item discoveries and story events."""
    print(f"\n\033[93m  ★  {msg}\033[0m\n")

def warning(msg):
    """Red highlight for dangers and warnings."""
    print(f"\n\033[91m  !  {msg}\033[0m\n")

def status_line():
    """Dim status bar showing lives and keys collected."""
    hearts = ("♥ " * inv["lives"] + "♡ " * (3 - inv["lives"])).strip()
    keys_found = sum(inv[k] for k in _KEYS)
    print(f"\n\033[2m  Lives: {hearts}   Keys: {keys_found}/4\033[0m")

def border():
    """Used for menu / win / lose screens only."""
    print("\033[1m-*-*-*-*-*-*-*-*-*-*-\033[0m")

def take_damage():
    """Decrement lives and queue a death message at the crossroads."""
    inv["lives"] -= 1
    flags["crossroads_msg"] = "death"

# ─── Input helpers ────────────────────────────────────────────────────────────

def get_valid_input(prompt, valid_options):
    """Raw validated input — used for menu / win / lose screens."""
    while True:
        try:
            user_input = int(input(prompt))
            if user_input in valid_options:
                return user_input
            print(f"Please choose from: {valid_options}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def prompt_choice(prompt, valid_options):
    """In-game decision prompt with status line and green styling."""
    status_line()
    print(f"\033[1;36m{'─' * 50}\033[0m")
    return get_valid_input(f"\033[92m{prompt}\033[0m", valid_options)

# ─── Inventory ────────────────────────────────────────────────────────────────

def check_inventory():
    """Display the player's current inventory."""
    print("\n\033[96mInventory:\033[0m")
    for item, qty in inv.items():
        if qty > 0:
            print(f"\033[96m  {item}\033[0m: {qty}")
    print()

def update_inventory(item, quantity=1):
    """Add an item to inventory, announce it, and display the inventory."""
    if item in inv:
        inv[item] += quantity
        event(f"Obtained: {item}")
        check_inventory()

# ─── End screens ──────────────────────────────────────────────────────────────

def screen_lose():
    """Show the lose screen. Returns True if the player wants to play again."""
    clear_screen()
    border()
    print("\033[93m ---- YOU LOSE ---- \n")
    print(
        "     .--------.     \n"
        "   .'          '.   \n"
        "  /   O      O   \\  \n"
        " :           `    : \n"
        " |                | \n"
        " :    .------.    : \n"
        "  \\  '        '  /  \n"
        "   '.          .'   \n"
        "     '-......-'     \n"
        " ---- YOU LOSE ---- \033[0m"
    )
    border()
    print()
    return get_valid_input("Would you like to play again? Yes[1] / No[2]:\n", [1, 2]) == 1

def screen_win():
    """Show the win screen. Returns True if the player wants to play again."""
    clear_screen()
    border()
    print("\033[93m ---- YOU WIN! ---- \n")
    print(
        "     .--------.     \n"
        "   .'          '.   \n"
        "  /   O      O   \\  \n"
        " :                : \n"
        " |                | \n"
        " : ',          ,' : \n"
        "  \\  '-......-'  /  \n"
        "   '.          .'   \n"
        "     '-......-'     \033[0m"
    )
    print()
    name = input("Please enter a name for the previous winners list!:\n")
    with open("winners.txt", "a", encoding="utf-8") as f:
        f.write(name + "\n")
    print("Your name has been added to the previous winners list!")
    border()
    print()
    return get_valid_input("Would you like to play again? Yes[1] / No[2]:\n", [1, 2]) == 1

# ─── Menu ─────────────────────────────────────────────────────────────────────

def howto():
    print("\n" + "-" * 66)
    print("| Keyhunter is a text-based adventure game.                 |")
    print("| Use numbers shown in-game to control your character.      |")
    print("| Example: Type 1 and hit enter to move your character.     |")
    print("| Find all four skeleton key parts to win the game.         |")
    print("| Be cautious of dangers — you will be warned beforehand!   |")
    print("-" * 66 + "\n")

def credits():
    print("\n" + "-" * 57)
    print("|                    GAME DEVELOPERS                    |")
    print("|                    Oisin Singleton                    |")
    print("|                      Conor Lacey                      |")
    print("|                      Andre Norton                     |")
    print("-" * 57 + "\n")

def winners():
    border()
    try:
        with open("winners.txt", "r", encoding="utf-8") as f:
            winners_list = f.readlines()
        if winners_list:
            for winner in winners_list:
                print(winner.strip())
        else:
            print("No winners found yet!")
    except FileNotFoundError:
        print("No winners file found.")
    border()

def menu():
    """Main menu loop. Returns True when the player chooses to start."""
    while True:
        clear_screen()
        border()
        print("\033[91m\033[1m| Welcome to Keyhunter: The Lost Temple of Cranmore |\033[0m")
        border()
        sg = get_valid_input("Input [1] Start / [2] How-to / [3] Credits / [4] Winners:\n", [1, 2, 3, 4])
        if sg == 1:
            return True
        elif sg == 2:
            howto()
        elif sg == 3:
            credits()
        elif sg == 4:
            winners()

# ─── Minigames ────────────────────────────────────────────────────────────────

def digging_game():
    """Random-word digging minigame."""
    words = ["dig", "shovel", "scoop", "delve", "unearth"]
    word = random.choice(words)
    print()
    for i in range(1, 6):
        response = input(f"\033[92m[{i}/5] Type '{word}' to dig down into the grave:\n\033[0m").strip().lower()
        while response != word:
            response = input(f"      Literally just type '{word}'...\n").strip().lower()
        print("You dig the grave.")

def elevator_game():
    """Random-sequence elevator escape minigame."""
    seq = ''.join(random.choices(string.ascii_lowercase, k=4))
    print()
    warning("Quick! Pull yourself free from the web!")
    print(f"  Enter this sequence: \033[1;93m{seq.upper()}\033[0m")
    print("  (Type the full sequence and press enter)\n")
    for i in range(1, 4):
        response = input(f"\033[92m[{i}/3] > \033[0m").strip().lower()
        while response != seq:
            warning("The webs tighten around you!")
            response = input(f"\033[92m[{i}/3] > \033[0m").strip().lower()
        print("You pull hard on the ropes.")
    print("\nYou burst free and scramble to the top of the elevator shaft!")

# ─── Locations ────────────────────────────────────────────────────────────────
# Each function clears the screen, renders its scene, then returns a location string.

def loc_crossroads():
    msg = flags["crossroads_msg"]
    flags["crossroads_msg"] = "returning"

    clear_screen()
    header("THE CROSSROADS")

    if msg == "death":
        if inv["lives"] <= 0:
            return "LOSE"
        warning("You wake up, your head is pounding.")
        print("You're back at the crossroads once again.")
        lives_word = "life" if inv["lives"] == 1 else "lives"
        print(f"Maybe you should be more careful — you only have {inv['lives']} {lives_word} left!")
    elif msg == "intro":
        print("You wake up at a crossroads with no memory of how you got there.")
    else:
        print("You look at the signpost.")

    print("\n  North — Cranmore Town")
    print("  South — Old Steel Mine")
    print("  East  — Lacey Lake")
    print("  West  — Cranmore Forest")

    choice = prompt_choice("\nHead North[1] / South[2] / East[3] / West[4]:\n", [1, 2, 3, 4])
    return ["town", "mine", "lake", "forest"][choice - 1]

# ── Town ──────────────────────────────────────────────────────────────────────

def loc_town():
    clear_screen()
    header("CRANMORE TOWN")
    print("You wander into the small town. The place is seemingly deserted....")
    time.sleep(0.7)
    print("The place makes you feel uneasy... You see 3 buildings worth exploring further.\n")
    print("  Straight — The inn")
    print("  Left     — The church")
    print("  Right    — The burnt down house")
    choice = prompt_choice("\nGo Straight[1] / Left[2] / Right[3] / Back[4]:\n", [1, 2, 3, 4])
    return ["town_inn", "town_church", "town_bhouse", "crossroads"][choice - 1]

def loc_town_bhouse():
    clear_screen()
    header("THE BURNT HOUSE")
    print("You walk into the burnt down house. The house is a complete mess.")
    print("Looking around, you don't see much except a small, charred locker with a statue of a cross.")
    locker_choice = prompt_choice("\nDo you open the locker? Yes[1] / No[2]:\n", [1, 2])
    if locker_choice == 1:
        print("\nYou open the top drawer...")
        if inv["ornate key"] == 1:
            print("There is nothing left here.")
        else:
            print("You find an ornate key.")
            update_inventory("ornate key")
    print("\nYou leave the burnt down house for the town center.")
    return "town"

def loc_town_church():
    clear_screen()
    header("THE CHURCH")
    print("You arrive at an old church.")
    print("You try the door, but it is locked. It looks like it requires some sort of key?")
    if inv["ornate key"] == 1:
        print("\nYou use the key you found in the house.")
        time.sleep(0.7)
        print("The key opens the door to the church.")
        time.sleep(0.7)
        print("You explore the church and find a skeleton key on the altar.")
        if inv["skeleton key(town)"] == 1:
            print("You already have the key!")
        else:
            update_inventory("skeleton key(town)")
    else:
        print("\nYou cannot get through the front door and decide to try another way.")
        time.sleep(0.7)
        print("You look around the back of the church and find an entrance to the basement.")
        time.sleep(0.7)
        warning("The way is poorly lit, and a burst pipe has covered the stairs in treacherous water. Very dangerous!")
        cs = prompt_choice("Do you proceed? Yes[1] / No[2]:\n", [1, 2])
        if cs == 1:
            slip_chance = 0.15 if inv["matches"] == 1 else 0.60
            if random.random() < slip_chance:
                print("\nYou walk down the stairs and slip, hitting your head on a step.")
                take_damage()
                return "crossroads"
            else:
                print("\nYou pick your way carefully down the stairs. Dark and damp, but you make it.")
                print("There's nothing useful down here. You head back up.")
    print("\nYou leave the church for the town center.")
    return "town"

def loc_town_inn():
    clear_screen()
    header("THE INN")
    print("You explore the inn.")
    print("The place is cozy and looks like a decent place for a drink, but you don't have the time...")
    if inv["lives"] < 3:
        print("A carvery appears on the table in front of you. You think someone is playing tricks on you.")
        print("You eat the carvery, knowing your mom might not be too happy since she has dinner ready.")
        inv["lives"] += 1
        event(f"You gain a life! You now have {inv['lives']} lives.")
    else:
        print("A carvery appears on the table in front of you.")
        print("You know your mom has dinner ready, and you're not too hungry.")
        print("You leave the carvery alone and leave.")
    print("\nYou leave the inn for the town center.")
    return "town"

# ── Forest ────────────────────────────────────────────────────────────────────

def loc_forest():
    clear_screen()
    header("CRANMORE FOREST — THE CLEARING")
    time.sleep(0.5)
    if not flags["forest_visited"]:
        flags["forest_visited"] = True
        print("As you walk down the beaten path, the trees begin to rise higher and higher around you.")
        print("The tallest of them stretch up almost touching the sky.")
        print("You come to a small clearing with a better view of the forest.")
    else:
        print("You're back at the small clearing.")
    time.sleep(0.5)
    print("\n  Left    — An abandoned manor in the distance")
    print("  Straight — An overgrown graveyard at the edge of the clearing")
    print("  Right   — Darkness, but a low hum draws you in")
    choice = prompt_choice("\nGo Left[1] / Straight[2] / Right[3] / Back[4]:\n", [1, 2, 3, 4])
    if choice == 1:
        return "forest_manor"
    elif choice == 2:
        if inv["skeleton key(forest)"] == 1:
            print("You already found what you needed in there.")
            return "forest"
        return "forest_graveyard"
    elif choice == 3:
        return "forest_temple"
    else:
        return "crossroads"

def loc_forest_manor():
    clear_screen()
    header("THE ABANDONED MANOR")
    time.sleep(0.5)
    print("The manor's front door is bolted shut.")
    print("Around the back: the door is slightly ajar, and there's a small wooden shed at the end of the garden.")
    choice = prompt_choice("\n[1] Try the back door / [2] Check out the shed / [3] Head back:\n", [1, 2, 3])
    if choice == 1:
        if inv["crowbar"] == 1:
            print("\nYou lever the door open with the crowbar.")
            return "forest_manor_kitchen"
        else:
            warning("The door is jammed tight. You'll need something to pry it open.")
            return "forest_manor"
    elif choice == 2:
        return "forest_manor_shed"
    else:
        return "forest"

def loc_forest_manor_shed():
    clear_screen()
    header("THE GARDEN SHED")
    time.sleep(0.5)
    if inv["crowbar"] == 1:
        print("Nothing else useful in the shed. You head back to the manor.")
        time.sleep(1)
    else:
        print("The shed door is hanging off at an angle; you easily pull it off completely. Wow, you're massive.")
        print("The smell of mold hits your nose as you step into the shed.")
        print("You now realize the entire roof is being propped up by just a few branches.")
        time.sleep(2)
        update_inventory("crowbar")
        print("You head back to the manor.")
        time.sleep(1)
    return "forest_manor"

def loc_forest_manor_kitchen():
    clear_screen()
    header("MANOR — KITCHEN")
    time.sleep(1)
    print("The air in the kitchen is stale, and there is a thick coating of dust on all surfaces.")
    print("This place is mad creepy.")
    if inv["matches"] == 0:
        print("\nYou check the drawers for something to light the way and find an old box of matches, somehow still dry.")
        update_inventory("matches")
    print("You use the matches to light the candles around the room. Handy that they were just lying around.")
    print("\nYou can see two doorways: one leads to a living room, the other to a hallway.")
    choice = prompt_choice("\n[1] Go into the hallway / [2] The living room / [3] Leave the manor:\n", [1, 2, 3])
    if choice == 1:
        warning("You step into the hallway. The floorboards give way and you plummet into the darkness below.")
        take_damage()
        return "crossroads"
    elif choice == 2:
        return "forest_manor_living"
    else:
        return "forest_manor"

def loc_forest_manor_living():
    clear_screen()
    header("MANOR — LIVING ROOM")
    time.sleep(0.5)
    print("The living room is thick with dust. Old furniture sits under white sheets.")
    print("Hunting trophies line the walls and a cold fireplace dominates the far end of the room.")
    if inv["machete"] == 0:
        print("\nA large machete hangs above the fireplace, surprisingly well-maintained.")
        update_inventory("machete")
        print("You take it. Could come in handy.")
    if inv["grave clue"] == 0:
        print("\nAn old journal sits open on the coffee table. One entry catches your eye:")
        time.sleep(1)
        print('\n  "...buried the old key with D.R. in the forest graveyard. God rest him."\n')
        time.sleep(1)
        update_inventory("grave clue")
        print("You pocket the journal.")
    choice = prompt_choice("\n[1] Head back to the kitchen / [2] Leave the manor:\n", [1, 2])
    return "forest_manor_kitchen" if choice == 1 else "forest_manor"

def loc_forest_graveyard():
    clear_screen()
    header("THE GRAVEYARD")
    time.sleep(1)
    print("You walk into the graveyard. The graves are overgrown, and most of the tombstones are falling apart.")
    print("You try to read some of the headstones, but the engravings are long worn away.")
    if inv["grave clue"] == 1:
        time.sleep(1)
        print("\nOne of the graves catches your eye.")
        time.sleep(1)
        print()
        print("              ____")
        print("             (    )")
        print("             __)(__")
        print("       _____/      \\_____")
        print("      |  _     ___   _   ||")
        print("      | | \\     |   | \\  ||")
        print("      | |  |    |   |  | ||")
        print("      | |_/     |   |_/  ||")
        print("      | | \\     |   |    ||")
        print("      | |  \\    |   |    ||")
        print("      | |   \\. _|_. | .  ||")
        print("      |                  ||")
        print("      |  What you seek   ||")
        print("      |  lies beneath    ||")
        print("      | *   **    * **   |**      **")
        print(" \\))ejm97/.,(//,,..,,\\||(,,.,\\\\,.((//")
        time.sleep(2)
        print("\nYou look around the grave for something to dig with.")
        print("A shovel is sitting right next to it. That was handy, wasn't it?")
        digging_game()
        print("\nFinally, the shovel hits wood. Clearing off the top dirt, you open up the coffin below.")
        time.sleep(1)
        print("\nInside the coffin is completely empty except for a small cloth bag.")
        print("You reach down and grab the bag. Looking inside, you find part of a skeleton key!")
        time.sleep(1)
        update_inventory("skeleton key(forest)")
        print("\nThis place is giving you the creeps. You leave.")
    else:
        print("\nThe graveyard is cold and eerie. The tombstones you can read have cryptic messages")
        print("on them which mean nothing to you. You leave the graveyard for now.")
        time.sleep(1)
    return "forest"

def loc_forest_temple():
    clear_screen()
    header("THE LOST TEMPLE OF CRANMORE")
    print("You arrive at the temple. The entrance is blocked by thick vines.")
    if inv["machete"] == 0:
        warning("You'll need to find something to cut through the vines.")
        return "forest"
    print("You hack through the vines with the machete.")
    missing = [k for k in _KEYS if inv[k] == 0]
    if missing:
        warning("The temple door has four locks. You are still missing:")
        for k in missing:
            print(f"    — {k}")
        return "forest"
    event("You have all four skeleton keys!")
    print("You fit them into the four locks on the temple door one by one.")
    time.sleep(1)
    print("The door grinds open with a deep rumble. You step inside.")
    time.sleep(1)
    print("\nA shaft of light cuts through the dust onto a stone pedestal.")
    print("The Lost Temple of Cranmore has been found. You have won the game!!!")
    return "WIN"

# ── Lake ──────────────────────────────────────────────────────────────────────

def loc_lake():
    clear_screen()
    header("LACEY LAKE")
    print("You walk towards the lake.")
    time.sleep(1)
    if inv["diving gear"] == 1 and inv["skeleton key(lake)"] == 0:
        print("The water here looks deep. Something shimmers at the bottom.")
        print("You strap on the diving gear and plunge in.")
        time.sleep(1)
        print("You find a skeleton key at the bottom of the lake!")
        update_inventory("skeleton key(lake)")
    elif inv["skeleton key(lake)"] == 1:
        print("You have already been here, and there is nothing left to explore!")
    else:
        print("The water here looks deep. You see something shimmer at the bottom.")
        warning("Maybe if you had diving gear you could get to it?")
        print("You go back to the crossroads.")
    time.sleep(1)
    return "crossroads"

def loc_lake_from_mine():
    clear_screen()
    header("LACEY LAKE")
    print("After feeling your way through the darkness of the underwater tunnels, you emerge")
    print("and find yourself in the middle of Lacey Lake.")
    print("You notice something glimmering in the depths of the lake.")
    dive = prompt_choice("\nDo you want to dive down and give it a go? Yes[1] / No[2]:\n", [1, 2])
    if dive == 1:
        print("The mammy wanted you in for 9, so you decide not to waste your valuable game time.")
    else:
        print("Haha, you think you're going back to those crossroads empty-handed? The mammy wouldn't be impressed, I tell ya.")
    print("You dive down and find a key!")
    update_inventory("skeleton key(lake)")
    return "crossroads"

# ── Mine ──────────────────────────────────────────────────────────────────────

def loc_mine():
    clear_screen()
    header("THE OLD STEEL MINE")
    time.sleep(0.5)
    if inv["skeleton key(mine)"] == 1:
        print("You have already explored this mine, and the entrance is caved in.")
        print("You head back to the crossroads.")
        return "crossroads"
    if flags["mine_collapsed"]:
        print("The entrance is caved in but you squeeze through a gap in the rubble.")
        time.sleep(1)
        return "mine_routes"
    print("The mine feels eerie, but you press on to see if there is anything of interest inside.")
    warning("Without a source of light, it's impossible to proceed further.")
    choice = prompt_choice("Try to find a light[1] / Leave for now[2]:\n", [1, 2])
    if choice == 2:
        print("\nYou decide to return later when you feel more prepared.")
        print("You leave the mine and return to the crossroads.")
        return "crossroads"
    print("\nYou search for a while and uncover an old torch hidden behind overgrown vines.")
    if inv["matches"] == 0:
        warning("You cannot continue — you're missing a valuable item to ignite the torch.")
        print("You should return when you have located the item.")
        time.sleep(2)
        print("You leave the mine and return to the crossroads.")
        return "crossroads"
    light = prompt_choice("\nDo you want to light the torch? Yes[1] / No[2]:\n", [1, 2])
    if light == 2:
        print("\nYou leave the mine for now and head back to the crossroads.")
        time.sleep(1)
        return "crossroads"
    print("\nYou light the torch using the matches in your inventory...")
    time.sleep(2)
    return "mine_collapse"

def loc_mine_collapse():
    clear_screen()
    header("THE OLD STEEL MINE — DEEP")
    flags["mine_collapsed"] = True
    print("!!!!Rumble!!!!\n")
    print("Suddenly you hear a loud rumbling behind you!")
    time.sleep(2)
    print("  *-------------------------------------------* ")
    print("  *           _.-^^---....,,.._               * ")
    print("  *       _--                  --_            * ")
    print("  *      (<                      >)           * ")
    print("  *       |                      |            * ")
    print("  *        \\._                _./             * ")
    print("  *          ``--. . , ; .-''                 * ")
    print("  *              |  |   |                     * ")
    print("  *           .-=||  |  |=-.                  * ")
    print("  *            \\*--------*/                   * ")
    print("  *              | ;  : |                     * ")
    print("  *           ###o0o0o0o0###                  * ")
    print("  *-------------------------------------------* ")
    time.sleep(1)
    print("\nYou fall forward and realize the exit is blocked. There's no escape.")
    time.sleep(1)
    print("\nYou have no choice but to continue ahead.")
    time.sleep(2)
    print("\nAs you're walking, the floor beneath you collapses!")
    time.sleep(3)
    print("\nYou wake up in a new area with four routes ahead.")
    return "mine_routes"

def loc_mine_routes():
    clear_screen()
    header("THE OLD STEEL MINE — JUNCTION")
    while True:
        print("  [1] Water route")
        print("  [2] Spider-web route")
        print("  [3] Mine cart route")
        print("  [4] The cliff\n")
        choice = prompt_choice("Which route do you take?\n", [1, 2, 3, 4])
        if choice == 4:
            print("\nThere seems to be a fourth way, but it's a large drop. You decide to choose another way.")
        elif choice == 1:
            warning("The water route is too deep to navigate without equipment. Choose another way.")
        elif choice == 2:
            print("\nYou have decided to take the spider-web route.")
            print("\nBattling the webs, you find yourself face-to-face with a giant spider!")
            time.sleep(2)
            print(" ______________________________  ")
            print("| -*-*-*-*-*       *-*-*-*-*-  | ")
            print("|  __-----__       __-----__   | ")
            print("|-   ( 0 )   -   -   ( 0 )   - | ")
            print("| '---------'     '---------'  | ")
            print("|______________________________| ")
            time.sleep(1)
            print("\nYou dash to a nearby tunnel, escaping the spider.")
            print("You find a skeleton holding a chest containing diving gear and a pickaxe!")
            if inv["pickaxe"] == 0:
                inv["pickaxe"] += 1
            if inv["diving gear"] == 0:
                inv["diving gear"] += 1
            check_inventory()
            print("\nYou quickly run to the next tunnel, which leads to an elevator.")
            return "mine_elevator"
        else:
            print("\nYou take the mine cart down a thrilling ride, landing at the bottom!")
            print("You find a skeleton holding diving gear and a pickaxe.")
            if inv["pickaxe"] == 0:
                inv["pickaxe"] += 1
            if inv["diving gear"] == 0:
                inv["diving gear"] += 1
            check_inventory()
            print("\nA giant spider appears! You escape to a nearby tunnel leading to an elevator.")
            return "mine_elevator"

def loc_mine_elevator():
    clear_screen()
    header("MINE — ELEVATOR SHAFT")
    elevator_game()
    return "mine_fight"

def loc_mine_fight():
    clear_screen()
    header("MINE — SPIDER ENCOUNTER")
    print("A giant spider lunges at you from the shadows. You must act quickly!")
    choice = prompt_choice("\nUse: Diving gear[1] / Matches[2] / Pickaxe[3]:\n", [1, 2, 3])
    if choice == 3:
        event("You swing the pickaxe with all your strength, killing the spider!")
        update_inventory("skeleton key(mine)")
        print("You put on your diving gear and swim through an underwater tunnel.")
        return "lake_from_mine"
    else:
        warning("Your attempt to fend off the spider fails. The spider attacks and you lose a life.")
        print("You barely escape, dragging yourself back through the mine.")
        take_damage()
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

# ─── Game loop ────────────────────────────────────────────────────────────────

def run_game():
    """Run a single playthrough. Returns True if the player wants to play again."""
    reset_state()
    clear_screen()
    name = input("Please enter your name:\n")
    print(f"\nWelcome, {name}\n")
    time.sleep(1)
    location = "crossroads"
    while location not in ("WIN", "LOSE"):
        location = LOCATIONS[location]()
    if location == "WIN":
        return screen_win()
    else:
        return screen_lose()

def main():
    while menu():
        play_again = True
        while play_again:
            play_again = run_game()
    print("Ok! Thanks for playing!")

if __name__ == "__main__":
    main()
