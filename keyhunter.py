#!/usr/bin/env python3
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

# ─── Utilities ────────────────────────────────────────────────────────────────

def get_valid_input(prompt, valid_options):
    """Prompt for input and validate against valid options."""
    while True:
        try:
            user_input = int(input(prompt))
            if user_input in valid_options:
                return user_input
            print(f"Please choose from: {valid_options}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def check_inventory():
    """Display the player's current inventory."""
    print("\n\033[96mInventory:\033[0m")
    for item, qty in inv.items():
        if qty > 0:
            print(f"\033[96m  {item}\033[0m: {qty}")
    print()

def update_inventory(item, quantity=1):
    """Add an item to inventory and display it."""
    if item in inv:
        inv[item] += quantity
        check_inventory()

def border():
    print("\033[1m-*-*-*-*-*-*-*-*-*-*-\033[0m")

def take_damage():
    """Decrement lives and queue a death message at the crossroads."""
    inv["lives"] -= 1
    flags["crossroads_msg"] = "death"

# ─── End screens ──────────────────────────────────────────────────────────────

def screen_lose():
    """Show the lose screen. Returns True if the player wants to play again."""
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
        response = input(f"[{i}/5] Type '{word}' to dig down into the grave:\n").strip().lower()
        while response != word:
            response = input(f"      Literally just type '{word}'...\n").strip().lower()
        print("You dig the grave.")

def elevator_game():
    """Random-sequence elevator escape minigame."""
    seq = ''.join(random.choices(string.ascii_lowercase, k=4))
    print()
    print(f"Quick! Type this sequence to pull yourself free from the web: {seq.upper()}")
    print("(Enter the full sequence and press enter)\n")
    for i in range(1, 4):
        response = input(f"[{i}/3] > ").strip().lower()
        while response != seq:
            print("The webs tighten around you!")
            response = input(f"[{i}/3] > ").strip().lower()
        print("You pull hard on the ropes.")
    print("\nYou burst free and scramble to the top of the elevator shaft!")
    border()

# ─── Locations ────────────────────────────────────────────────────────────────
# Each function prints its narrative then returns a location string.

def loc_crossroads():
    msg = flags["crossroads_msg"]
    flags["crossroads_msg"] = "returning"

    if msg == "death":
        if inv["lives"] <= 0:
            return "LOSE"
        print("\nYou wake up, your head is pounding.")
        print("You're back at the crossroads once again.")
        lives_word = "life" if inv["lives"] == 1 else "lives"
        print(f"Maybe you should be more careful — you only have {inv['lives']} {lives_word} left!")
    elif msg == "intro":
        print("You wake up at a crossroads with no memory of how you got there.")
    else:
        print("\nYou look at the signpost.")

    border()
    print("North - Cranmore Town\nSouth - Old Steel Mine\nEast - Lacey Lake\nWest - Cranmore Forest")
    border()
    choice = get_valid_input("You decide to head North[1] / South[2] / East[3] / West[4]:\n", [1, 2, 3, 4])
    return ["town", "mine", "lake", "forest"][choice - 1]

# ── Town ──────────────────────────────────────────────────────────────────────

def loc_town():
    print()
    border()
    print("You wander into the small town. The place is seemingly deserted....")
    time.sleep(0.7)
    print("The place makes you feel uneasy... You see 3 buildings worth exploring further.\n")
    print("Straight - Head towards the inn...\nLeft - Head towards the church...\nRight - Head towards the burnt down house...")
    border()
    choice = get_valid_input("Do you go Straight[1] / Left[2] / Right[3] or Back[4]:\n", [1, 2, 3, 4])
    return ["town_inn", "town_church", "town_bhouse", "crossroads"][choice - 1]

def loc_town_bhouse():
    print()
    border()
    print("You walk into the burnt down house. The house is a complete mess.")
    print("Looking around, you don't see much except a small, charred locker with a statue of a cross.")
    border()
    locker_choice = get_valid_input("Do you open the locker? Yes[1] / No[2]:\n", [1, 2])
    if locker_choice == 1:
        print()
        border()
        print("You open the top drawer...")
        if inv["ornate key"] == 1:
            print("There is nothing left here.")
        else:
            print("You find an ornate key.")
            update_inventory("ornate key")
        border()
    print("\nYou leave the burnt down house for the town center.")
    return "town"

def loc_town_church():
    print()
    border()
    print("You arrive at an old church.")
    print("You try the door, but it is locked. It looks like it requires some sort of key?")
    if inv["ornate key"] == 1:
        border()
        print("You use the key you found in the house.")
        time.sleep(0.7)
        print("The key opens the door to the church.")
        time.sleep(0.7)
        print("You explore the church and find a skeleton key on the altar.")
        if inv["skeleton key(town)"] == 1:
            print("You already have the key!")
        else:
            update_inventory("skeleton key(town)")
            print("You pick up the skeleton key (town).")
        border()
    else:
        print("\nYou cannot get through the front door and decide to try another way.")
        time.sleep(0.7)
        print("You look around the back of the church and find an entrance to the basement.")
        time.sleep(0.7)
        print("The way is poorly lit, and a burst pipe has covered the stairs in treacherous water.")
        print("This way in is clearly very dangerous!")
        cs = get_valid_input("Do you proceed? Yes[1] / No[2]:\n", [1, 2])
        if cs == 1:
            slip_chance = 0.15 if inv["matches"] == 1 else 0.60
            if random.random() < slip_chance:
                print("\nYou walk down the stairs and slip, hitting your head on a step.")
                border()
                take_damage()
                return "crossroads"
            else:
                print("\nYou pick your way carefully down the stairs. It's dark and damp, but you make it.")
                print("There's nothing useful down here. You head back up.")
    print("\nYou leave the church for the town center.")
    return "town"

def loc_town_inn():
    print()
    border()
    print("You explore the inn.")
    print("The place is cozy and looks like a decent place for a drink, but you don't have the time...")
    if inv["lives"] < 3:
        print("A carvery appears on the table in front of you. You think someone is playing tricks on you.")
        print("You eat the carvery, knowing your mom might not be too happy since she has dinner ready.")
        inv["lives"] += 1
        print(f"You gain a life! You now have {inv['lives']} lives.")
    else:
        print("A carvery appears on the table in front of you.")
        print("You know your mom has dinner ready, and you're not too hungry.")
        print("You leave the carvery alone and leave.")
    border()
    print("\nYou leave the inn for the town center.")
    return "town"

# ── Forest ────────────────────────────────────────────────────────────────────

def loc_forest():
    print()
    time.sleep(1)
    border()
    if not flags["forest_visited"]:
        flags["forest_visited"] = True
        print("\nAs you walk down the beaten path, the trees begin to rise higher and higher around you.")
        print("The tallest of them stretch up almost touching the sky.")
        print("You come to a small clearing.")
        print("From here, you get a better view of the forest.")
    else:
        print("\nYou're back at the small clearing.")
    border()
    time.sleep(1)
    print("\nTo your left, you can see what looks to be an abandoned manor in the distance.")
    print("Straight ahead, at the edge of the clearing, is an overgrown graveyard.")
    print("You can't see anything to your right, but there seems to be a low hum coming from the forest.")
    border()
    choice = get_valid_input("You decide to go [1] Left / [2] Straight / [3] Right / [4] Back:\n", [1, 2, 3, 4])
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
    print()
    time.sleep(1)
    border()
    print("\nThe manor's front door is bolted shut.")
    print("Around the back: the door is slightly ajar, and there's a small wooden shed at the end of the garden.")
    border()
    choice = get_valid_input("[1] Try the back door / [2] Check out the shed / [3] Head back:\n", [1, 2, 3])
    if choice == 1:
        if inv["crowbar"] == 1:
            print("\nYou lever the door open with the crowbar.")
            return "forest_manor_kitchen"
        else:
            print("\nThe door is jammed tight. You'll need something to pry it open.")
            return "forest_manor"
    elif choice == 2:
        return "forest_manor_shed"
    else:
        return "forest"

def loc_forest_manor_shed():
    print()
    time.sleep(1)
    border()
    if inv["crowbar"] == 1:
        print("Nothing else useful in the shed. You head back to the manor.")
        time.sleep(2)
    else:
        print("The shed door is hanging off at an angle; you easily pull it off completely. Wow, you're massive.")
        print("The smell of mold hits your nose as you step into the shed. You now realize the entire roof is being propped up by just a few branches.")
        time.sleep(3)
        update_inventory("crowbar")
        print("You head back to the manor.")
        time.sleep(2)
    return "forest_manor"

def loc_forest_manor_kitchen():
    print()
    time.sleep(2)
    border()
    print("\nThe air in the kitchen is stale, and there is a thick coating of dust on all surfaces.")
    print("This place is mad creepy.")
    if inv["matches"] == 0:
        print("\nYou check the drawers for something to light the way and find an old box of matches, somehow still dry.")
        update_inventory("matches")
    print("You use the matches to light the candles around the room. Handy that they were just lying around.")
    print("You can see two doorways now: one leads to a living room, and the other to a hallway.")
    border()
    choice = get_valid_input("Do you [1] go into the hallway / [2] the living room / [3] leave the manor?\n", [1, 2, 3])
    if choice == 1:
        print("\nYou step into the hallway. The floorboards give way and you plummet into the darkness below.")
        border()
        take_damage()
        return "crossroads"
    elif choice == 2:
        return "forest_manor_living"
    else:
        return "forest_manor"

def loc_forest_manor_living():
    print()
    time.sleep(1)
    border()
    print("\nThe living room is thick with dust. Old furniture sits under white sheets.")
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
    border()
    choice = get_valid_input("Do you [1] head back to the kitchen / [2] leave the manor?\n", [1, 2])
    return "forest_manor_kitchen" if choice == 1 else "forest_manor"

def loc_forest_graveyard():
    print()
    time.sleep(2)
    border()
    print("\nYou walk into the graveyard. The graves are overgrown, and most of the tombstones are falling apart.")
    print("You try to read some of the headstones, but the engravings are long worn away.")
    if inv["grave clue"] == 1:
        time.sleep(1)
        print("One of the graves catches your eye.")
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
        print("\nYou look around the grave for something to dig with. A shovel is sitting right next to it.")
        print("That was handy, wasn't it?")
        print()
        digging_game()
        print("\nFinally, the shovel hits wood. Clearing off the top dirt, you open up the coffin below.")
        time.sleep(1)
        print("\nInside the coffin is completely empty except for a small cloth bag.")
        print("You reach down and grab the bag. Looking inside, you find part of a skeleton key!")
        time.sleep(1)
        update_inventory("skeleton key(forest)")
        print("\nThis place is giving you the creeps. You leave.")
    else:
        print("The graveyard is cold and eerie. The tombstones you can read have cryptic messages")
        print("on them which mean nothing to you. You leave the graveyard for now.")
        time.sleep(1)
    return "forest"

def loc_forest_temple():
    print()
    border()
    print("You arrive at the temple hoping to wrap up the game. The entrance is blocked by vines.")
    if inv["machete"] == 0:
        print("You'll need to find something to cut through the vines.")
        return "forest"
    print("You hack through the vines with the machete.")
    missing = [k for k in ["skeleton key(town)", "skeleton key(lake)", "skeleton key(forest)", "skeleton key(mine)"] if inv[k] == 0]
    if missing:
        print(f"The temple door has four locks. You are still missing: {', '.join(missing)}.")
        return "forest"
    print("You have all four skeleton keys!")
    print("You fit them into the four locks on the temple door one by one.")
    time.sleep(1)
    print("The door grinds open with a deep rumble. You step inside.")
    time.sleep(1)
    print("\nA shaft of light cuts through the dust onto a stone pedestal.")
    print("The Lost Temple of Cranmore has been found. You have won the game!!!")
    return "WIN"

# ── Lake ──────────────────────────────────────────────────────────────────────

def loc_lake():
    print()
    border()
    print("You walk towards the lake.")
    print()
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
        print("Maybe if you had diving gear you could get to it?")
        print("You go back to the crossroads.")
    border()
    time.sleep(1)
    return "crossroads"

def loc_lake_from_mine():
    print()
    border()
    print("After feeling your way through the darkness of the underwater tunnels, you emerge")
    print("and find yourself in the middle of Lacey Lake.")
    print("You notice something glimmering in the depths of the lake.")
    dive = get_valid_input("Do you want to dive down and give it a go? Yes[1] / No[2]: ", [1, 2])
    if dive == 1:
        print("The mammy wanted you in for 9, so you decide not to waste your valuable game time.")
    else:
        print("Haha, you think you're going back to those crossroads empty-handed? The mammy wouldn't be impressed, I tell ya.")
    print("You dive down and find a key!")
    update_inventory("skeleton key(lake)")
    border()
    return "crossroads"

# ── Mine ──────────────────────────────────────────────────────────────────────

def loc_mine():
    print("\nYou head towards the Old Steel Mine.")
    time.sleep(1)
    if inv["skeleton key(mine)"] == 1:
        print("\nYou have already explored this mine, and the entrance is caved in.")
        print("You head back to the crossroads.")
        return "crossroads"
    if flags["mine_collapsed"]:
        print("\nThe entrance is caved in but you squeeze through a gap in the rubble.")
        time.sleep(1)
        return "mine_routes"
    print("\nThe mine feels eerie, but you press on to see if there is anything of interest inside.")
    print("Without a source of light, it's impossible to proceed further.")
    border()
    choice = get_valid_input("Try to find a light[1] / Leave for now[2]: ", [1, 2])
    if choice == 2:
        print("\nYou decide to return later when you feel more prepared.")
        border()
        print("You leave the mine and return to the crossroads.")
        return "crossroads"
    print("\nYou search for a while and uncover an old torch hidden behind overgrown vines.")
    border()
    if inv["matches"] == 0:
        print("You cannot continue — you're missing a valuable item to ignite the torch.")
        print("You should return when you have located the item.")
        border()
        time.sleep(2)
        print("You leave the mine and return to the crossroads.")
        return "crossroads"
    light = get_valid_input("Do you want to light the torch? Yes[1] / No[2]: ", [1, 2])
    if light == 2:
        print("\nYou leave the mine for now and head back to the crossroads.")
        time.sleep(2)
        return "crossroads"
    print("\nYou light the torch using the matches in your inventory...")
    time.sleep(2)
    border()
    return "mine_collapse"

def loc_mine_collapse():
    flags["mine_collapsed"] = True
    print("\n!!!!Rumble!!!!")
    print("\nSuddenly you hear a loud rumbling behind you!")
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
    border()
    return "mine_routes"

def loc_mine_routes():
    while True:
        print()
        choice = get_valid_input(
            "Input [1] Water route / [2] Spider-web route / [3] Mine cart route / [4] Cliff:\n",
            [1, 2, 3, 4]
        )
        if choice == 4:
            print("\nThere seems to be a fourth way, but it's a large drop. You decide to choose another way.")
            border()
        elif choice == 1:
            print("\nThe water route is too deep to navigate without equipment. Choose another way.")
            border()
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
    elevator_game()
    return "mine_fight"

def loc_mine_fight():
    print("\nA giant spider lunges at you, and you must act quickly!")
    choice = get_valid_input("Use: Diving gear[1] / Matches[2] / Pickaxe[3]: ", [1, 2, 3])
    if choice == 3:
        print("\nYou swing the pickaxe with all your strength, killing the spider!")
        update_inventory("skeleton key(mine)")
        print("\nYou put on your diving gear and swim through an underwater tunnel.")
        return "lake_from_mine"
    else:
        print("\nYour attempt to fend off the spider fails. The spider attacks and you lose a life.")
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
    name = input("Please enter your name:\n")
    print(f"\nWelcome, {name}\n")
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
