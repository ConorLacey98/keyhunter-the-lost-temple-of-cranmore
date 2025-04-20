#!/usr/bin/env python3
import time
import sys

# Inventory initialization
inv = {
    "skeleton key(town)": 0,
    "skeleton key(mine)": 0,
    "skeleton key(lake)": 0,
    "skeleton key(forest)": 0,
    "lives": 3,
    "diving gear": 0,
    "ornate key": 0,
    "cabin key": 0,
    "matches": 0,
    "pickaxe": 0,
    "machete": 0,
    "crowbar": 0,
    "grave clue": 0,
}

# Utility functions
def get_valid_input(prompt, valid_options):
    """Prompts the user for input and validates against valid options."""
    while True:
        try:
            user_input = int(input(prompt))
            if user_input in valid_options:
                return user_input
            print(f"Please choose from the following: {valid_options}")
        except ValueError:
            print("Invalid input. Please enter a number.")

def check_inventory():
    """Displays the player's current inventory."""
    print("\n\033[96mInventory:\033[0m")
    for item, quantity in inv.items():
        if quantity > 0:
            print(f"\033[96m{item}\033[0m: {quantity}")
    print()

def update_inventory(item, quantity=1):
    """Updates the inventory with the specified quantity of an item."""
    if item in inv:
        inv[item] += quantity
        check_inventory()

def border():
    """Prints a decorative border."""
    print("\033[1m-*-*-*-*-*-*-*-*-*-*-\033[0m")

def lose():
    """Handles the lose condition."""
    border()
    print("\033[93m ---- YOU LOSE ---- \n")
    print(
        "     .--------.     \n"
        "   .'          '.   \n"
        "  /   O      O   \  \n"
        " :           `    : \n"
        " |                | \n"
        " :    .------.    : \n"
        "  \  '        '  /  \n"
        "   '.          .'   \n"
        "     '-......-'     \n"
        " ---- YOU LOSE ---- \033[0m"
    )
    border()
    print()
    if get_valid_input("Would you like to play again? Yes [1] / No [2]:\n", [1, 2]) == 1:
        menu()
    else:
        print("Ok! Thanks for playing!")

def win():
    """Handles the win condition."""
    border()
    print("\033[93m ---- YOU WIN! ---- \n")
    print(
        "     .--------.     \n"
        "   .'          '.   \n"
        "  /   O      O   \  \n"
        " :                : \n"
        " |                | \n"
        " : ',          ,' : \n"
        "  \  '-......-'  /  \n"
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
    if get_valid_input("Would you like to play again? Yes [1] / No [2]:\n", [1, 2]) == 1:
        menu()
    else:
        print("Ok! Thanks for playing!")

# Navigation and menu functions
def menu():
    """Displays the game menu."""
    border()
    print("\033[91m\033[1m| Welcome to Keyhunter: The Lost Temple of Cranmore |\033[0m")
    border()
    sg = get_valid_input("Input [1] Start / [2] How-to / [3] Credits / [4] Winners:\n", [1, 2, 3, 4])
    if sg == 1:
        name = input("Please enter your name:\n")
        print(f"\nWelcome, {name}\n")
        intro()
    elif sg == 2:
        howto()
    elif sg == 3:
        credits()
    elif sg == 4:
        winners()

def navigate(prompt, options):
    """Handles navigation logic with a prompt and a dictionary of options."""
    choice = get_valid_input(prompt, list(options.keys()))
    options[choice]()  # Call the corresponding function

def howto():
    """Displays a basic guide to the game."""
    print("\n" + "-" * 66)
    print("| X is a text-based adventure game.                         |")
    print("| Use keys when shown in-game to control your character.    |")
    print("| Example: Type 1 and hit enter to move your character.     |")
    print("| Find key parts in each area to win the game.              |")
    print("| Be cautious of dangers, but you'll be warned beforehand!  |")
    print("-" * 66 + "\n")
    menu()

def credits():
    """Displays game credits."""
    print("\n" + "-" * 57)
    print("|                    GAME DEVELOPERS                    |")
    print("|                    Oisin Singleton                    |")
    print("|                      Conor Lacey                      |")
    print("|                      Andre Norton                     |")
    print("-" * 57 + "\n")
    menu()

def winners():
    """Displays previous winners."""
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
    menu()

def intro():
    """Handles the game's introduction."""
    border()
    print("You wake up at a crossroads with no memory of how you got there.")
    print("North - Cranmore Town\nSouth - Old Steel Mine\nEast - Lacey Lake\nWest - Cranmore Forest")
    border()
    dir_choice = get_valid_input("You decide to head North[1] / South[2] / East[3] / West[4]:\n", [1, 2, 3, 4])
    navigate_to_area(dir_choice)

def navigate_to_area(choice):
    """Routes player based on directional choice."""
    if choice == 1:
        town()
    elif choice == 2:
        mine()
    elif choice == 3:
        lake()
    elif choice == 4:
        forest()

def backintro():
    """Handles returning to the sign choices."""
    print("\nYou look at the sign post.")
    border()
    print("The sign points 4 different directions down different paths.\n")
    print("North - Cranmore Town\nSouth - Old Steel Mine\nEast - Lacey Lake\nWest - Cranmore Forest")
    border()
    dir_choice = get_valid_input("You decide to head North[1] / South[2] / East[3] / West[4]:\n", [1, 2, 3, 4])
    navigate_to_area(dir_choice)

def deathintro():
    """Handles player respawning with reduced lives."""
    if inv["lives"] <= 0:
        lose()
        return  # Exit the function early as the game is over
    print("\nYou wake up, your head is pounding.")
    print("You're back at the crossroads once again.")
    print(f"Maybe you should be more careful; you only have {inv['lives']} lives left!")
    border()
    print("The sign points 4 different directions down different paths.\n")
    print("North - Cranmore Town\nSouth - Old Steel Mine\nEast - Lacey Lake\nWest - Cranmore Forest")
    border()
    dir_choice = get_valid_input("You decide to head North[1] / South[2] / East[3] / West[4]:\n", [1, 2, 3, 4])
    navigate_to_area(dir_choice)

# Town Functions

def town():
    """Handles the town section when the player chooses North."""
    print()
    border()
    print("You wander into the small town. The place is seemingly deserted....")
    time.sleep(0.7)
    print("The place makes you feel uneasy... You see 3 buildings worth exploring further.\n")
    print("Straight - Head towards the inn...\nLeft - Head towards the church...\nRight - Head towards the burnt down house...")
    border()
    navigate(
        "Do you go Straight[1] / Left[2] / Right[3] or Back[4]:\n",
        {1: inn, 2: church, 3: bhouse, 4: backintro}
    )

def bhouse():
    """Handles the burnt down house section."""
    print()
    border()
    print("You walk into the burnt down house. The house is a complete mess.")
    print("Looking around, you don't see much except a small, charred locker with a statue of a cross.")
    border()
    locker_choice = get_valid_input("Do you open the locker? Yes[1] / No[2] / Maybe[3]:\n", [1, 2, 3])
    if locker_choice == 1:
        print()
        border()
        print("You open the top drawer...")
        if inv["ornate key"] == 1:
            print("There is nothing left here.")
        else:
            update_inventory("ornate key")
            print("You find an ornate key.")
        border()
    leavingbhouse()

def leavingbhouse():
    """Handles leaving the burnt down house."""
    print()
    border()
    print("You leave the burnt down house for the town center.")
    print("Straight - Head towards the inn...\nLeft - Head towards the church...")
    border()
    navigate(
        "Do you go Straight[1] / Left[2] / Back[3]:\n",
        {1: inn, 2: church, 3: backintro}
    )

def church():
    """Handles the church section in the town."""
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
        print("The way is poorly lit, and a burst pipe has covered the stairs in treacherous water. This way in is clearly very dangerous!")
        cs = get_valid_input("Do you proceed? Yes[1] / No[2]:\n", [1, 2])
        if cs == 1:
            print("\nYou walk down the stairs and slip, hitting your head on a step.")
            border()
            inv["lives"] -= 1
            deathintro()
        else:
            leavingchurch()
    leavingchurch()

def leavingchurch():
    """Handles leaving the church."""
    print()
    border()
    print("You leave the church for the town center.")
    print("Straight - Head towards the inn...\nRight - Head towards the burnt down house...\n")
    border()
    navigate(
        "Do you go Straight[1] / Right[2] / Back[3]:\n",
        {1: inn, 2: bhouse, 3: backintro}
    )

def inn():
    """Handles the inn section in the town."""
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
    leavinginn()

def leavinginn():
    """Handles leaving the inn."""
    print()
    border()
    print("You leave the inn for the town center.")
    print("Right - Head towards the burnt down house...\nLeft - Head towards the church...")
    border()
    navigate(
        "Do you go Left[2] / Right[3] / Back[4]:\n",
        {2: church, 3: bhouse, 4: backintro}
    )

# Forest Functions

def forest():
    """Handles the forest section of the game."""
    print()
    time.sleep(1)
    border()
    print("\nAs you walk down the beaten path, the trees begin to rise higher and higher around you.")
    print("The tallest of them stretch up almost touching the sky.")
    print("You come to a small clearing.")
    print("From here, you get a better view of the forest.")
    border()
    time.sleep(2)
    print("\nTo your left, you can see what looks to be an abandoned manor in the distance.")
    print("Straight ahead, at the edge of the clearing, is an overgrown graveyard.")
    print("You can't see anything to your right, but there seems to be a low hum coming from the forest, drawing you in.")
    border()
    navigate(
        "You decide to go [1] Left / [2] Straight / [3] Right / [4] Back:\n",
        {
            1: lambda: manorbk() if inv["skeleton key(forest)"] == 1 else manor(),
            2: lambda: print("You already have the skeleton key from there!") or forestbk() if inv["skeleton key(forest)"] == 1 else graveyard(),
            3: temple,
            4: backintro,
        }
    )

def forestbk():
    """Handles returning to the forest clearing."""
    print()
    time.sleep(1)
    border()
    print("\nYou're back at the small clearing.")
    border()
    print("\nTo your left is the abandoned manor in the distance.")
    print("Straight ahead, at the edge of the clearing, is the graveyard.")
    print("To the right is the strange sound.")
    border()
    navigate(
        "You decide to go [1] Left / [2] Straight / [3] Right / [4] Back:\n",
        {
            1: lambda: manorbk() if inv["skeleton key(forest)"] == 1 else manor(),
            2: lambda: print("You already have the skeleton key from there!") or forestbk() if inv["skeleton key(forest)"] == 1 else graveyard(),
            3: temple,
            4: backintro,
        }
    )

def manor():
    """Handles the manor back door area."""
    print()
    time.sleep(1)
    border()
    print("\nYou get to the door of the manor to find it is bolted shut.")
    print("Heading around to the back, you notice that the door here is slightly open.")
    print("There is also a small wooden shed at the end of the garden.")
    border()
    navigate(
        "[1] Try the door / [2] Check out the shed / [3] Go back:\n",
        {
            1: lambda: print("You successfully open the door with the crowbar.") or manorkitchen() if inv["crowbar"] == 1 else shed(),
            2: shed,
            3: forest,
        }
    )

def manorbk():
    """Handles going back to the manor's back door area."""
    print()
    time.sleep(1)
    border()
    print("\nYou're back outside the backdoor of the manor.")
    border()
    navigate(
        "[1] Go into the manor / [2] Check out the shed / [3] Head back to the clearing:\n",
        {
            1: manorkitchenbk if inv["matches"] == 1 else lambda: print("You successfully open the door with the crowbar.") or manorkitchen(),
            2: shed,
            3: forestbk,
        }
    )

def shed():
    """Handles the shed at the bottom of the manor's back garden."""
    print()
    time.sleep(1)
    border()
    if inv["crowbar"] == 1:
        print("There is nothing you can use in this shed. You leave and head back to the manor.")
        time.sleep(2)
        manorbk()
    else:
        print("The shed door is hanging off at an angle; you easily pull it off completely. Wow, you're massive.")
        print("The smell of mold hits your nose as you step into the shed. You now realize the entire roof is being propped up by just a few branches.")
        time.sleep(3)
        update_inventory("crowbar")
        print("You head back to the manor.")
        time.sleep(3)
        manorbk()

def manorkitchen():
    """Handles the manor's kitchen area."""
    print()
    time.sleep(2)
    border()
    print("\nThe air in the kitchen is stale, and there is a thick coating of dust on all surfaces.")
    print("This place is mad creepy.")
    if inv["matches"] != 1:
        print("\nYou check the drawers for something to light the way and find an old box of matches, somehow still dry.")
        update_inventory("matches")
    print("You use the matches to light the candles around the room. Handy that they were just lying around.")
    print("You can see two doorways now: one leads to a living room, and the other to a hallway.")
    border()
    navigate(
        "Do you [1] go into the hallway / [2] the living room / [3] leave the manor?\n",
        {
            1: lambda: print("You plummet into the abyss.") or lose_life() or deathintro(),
            2: livingroom,
            3: manorbk,
        }
    )

def graveyard():
    """Handles the graveyard where the skeleton key is found."""
    print()
    time.sleep(2)
    border()
    print("\nYou walk into the graveyard. The graves are overgrown, and most of the tombstones are falling apart.")
    print("You try to read some of the headstones, but the engravings are long worn away.")
    if inv["grave clue"] == 1:  # Check if you have the clue from the manor
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
        print("\nYou look around the grave for something to dig with. A shovel is sitting right next to it. That was handy, wasn't it?")
        print()
        digging_game()
        print("\nFinally, the shovel hits wood. Clearing off the top dirt, you open up the coffin below.")
        time.sleep(1)
        print("\nInside the coffin is completely empty except for a small cloth bag.")
        print("You reach down and grab the bag. Looking inside, you find part of a skeleton key!")
        time.sleep(1)
        inv["skeleton key(forest)"] += 1
        checkinv()
        print("\nThis place is giving you the creeps. You leave.")
        forestbk()
    else:
        print("The graveyard is cold and eerie. The tombstones you can read have cryptic messages on them which mean nothing to you.")
        print("You leave the graveyard for now.")
        time.sleep(1)
        forestbk()

def digging_game():
    """Handles the digging minigame in the graveyard."""
    print()
    i = 0
    while i < 5:
        dig = input("Type 'dig' to dig down into the grave:\n").strip().lower()
        while dig != "dig":
            dig = input("Literally just type the word 'dig'...\n").strip().lower()
        print("You dig the grave.")
        i += 1

def temple():
    """Handles the temple in the forest where the game can be completed."""
    print()
    border()
    print("You arrive at the temple hoping to wrap up the game. The entrance is blocked by vines.")
    if inv["machete"] == 1:
        print("You are so close to victory. You hear victory songs through the grapevine.")
        if all(inv[key] == 1 for key in ["skeleton key(town)", "skeleton key(lake)", "skeleton key(forest)", "skeleton key(mine)"]):
            print("You have all the Skeleton Keys and have won the game!!!")
            win()
        else:
            print("You don't have all 4 skeleton keys yet!")
            forestbk()
    else:
        print("You'll need to find something to cut through the vines.")
        forestbk()

# Lake Functions

def lakefrommine():
    """Handles going to the lake through the mine."""
    print()
    border()
    print("After feeling your way through the darkness of the underwater tunnels, you emerge and find yourself in the middle of Lacey Lake.")
    print("You notice something glimmering in the depths of the lake.")
    dive = get_valid_input("Do you want to dive down and give it a go? Yes[1] / No[2]: ", [1, 2])
    if dive == 1:
        print("The mammy wanted you in for 9, so you decide not to waste your valuable game time.")
    else:
        print("Haha, you think you're going back to those crossroads empty-handed? The mammy wouldn't be impressed, I tell ya.")
    print("You dive down and find a key!")
    update_inventory("skeleton key(lake)")
    border()
    backintro()

def lake():
    """Handles coming to the lake from the crossroads."""
    print()
    border()
    print("You walk towards the lake.")
    print()
    time.sleep(1)
    if inv["diving gear"] != 1:
        print("The water here looks deep. You see something shimmer at the bottom. Maybe if you had diving gear you could get to it?")
        print("You go back to the crossroads.")
    else:
        print("You have already been here, and there is nothing left to explore!")
    border()
    time.sleep(1)
    backintro()

# MINE SECTION

def light_torch():
    """Handles lighting a torch in the mine."""
    if inv["matches"] == 0:
        print("You cannot continue as you are missing a valuable item to ignite the torch. You should return when you have located the item.")
        border()
        time.sleep(2)
        leave_mine()
    else:
        choice = get_valid_input("Do you want to light the torch? Yes[1] / No[2]: ", [1, 2])
        if choice == 1:
            print("\nYou light the torch using the matches in your inventory...")
            time.sleep(2)
            border()
            mine_collapse()
        else:
            print("\nYou leave the mine for now and head back to the crossroads.")
            time.sleep(2)
            backintro()

def mine_intro():
    """Handles the introduction to the mine."""
    choice = get_valid_input("Take a look around for a source of light[1] / Leave mine because you're scared[2]: ", [1, 2])
    if choice == 1:
        print("\nYou search for a while and uncover an old torch hidden behind overgrown vines.")
        border()
        light_torch()
    else:
        print("\nYou leave the mine and return to the crossroads to gather courage.")
        border()
        backintro()

def leave_mine():
    """Handles leaving the mine and returning to the crossroads."""
    print("You leave the mine and return to the crossroads. Perhaps you need to locate a necessary item to proceed.")
    navigate()

def mine_continue():
    """Handles the decision to continue in the mine or leave."""
    choice = get_valid_input("Try to find a light to continue through the mine[1] / Leave for now[2]: ", [1, 2])
    if choice == 1:
        print("\nYou choose to explore further in hopes of finding another Skeleton Key.")
        border()
        mine_intro()
    else:
        print("\nYou decide to return later when you feel more prepared.")
        border()
        leave_mine()

def mine():
    """Handles entry into the mine."""
    print("\nYou head towards the Old Steel Mine.")
    time.sleep(1)
    if inv["skeleton key(mine)"] == 1:
        print("\nYou have already explored this mine, and the entrance is caved in. You head back to the crossroads.")
        backintro()
    else:
        print("\nThe mine feels eerie, but you press on to see if there is anything of interest inside.")
        print("Without a source of light, it's impossible to proceed further.")
        border()
        mine_continue()

def elevator_game():
    """Handles the elevator escape game."""
    for _ in range(5):
        prompt = input("Type 'p' to pull yourself free from the web: ").strip().lower()
        while prompt != "p":
            prompt = input("Just type 'p'...").strip().lower()
        print("You pull on the ropes with all your might.")
    print("\nYou manage to escape and make it to the top of the elevator shaft.")
    border()
    fight()

def fight():
    """Handles the spider fight in the mine."""
    print("\nA giant spider lunges at you, and you must act quickly!")
    choice = get_valid_input("Use: Diving gear[1] / Matches[2] / Pickaxe[3]: ", [1, 2, 3])
    if choice == 3:
        print("\nYou swing the pickaxe with all your strength, killing the spider!")
        inv["skeleton key(mine)"] += 1
        update_inventory("skeleton key(mine)")
        print("\nYou put on your diving gear and swim through an underwater tunnel.")
        lakefrommine()
    else:
        print("\nYour attempt to fend off the spider fails. The spider attacks and you lose a life.")
        inv["lives"] -= 1
        deathintro()

def mine_routes():
    """Handles the routes available in the mine."""
    try:
        print()
        mroutes = int(input("Input [1] Water route / [2] Spider-web route / [3] Mine cart route / [4] Cliff:\n"))
        while mroutes not in (1, 2, 3, 4):
            mroutes = int(input("Please only input [1], [2], [3], or [4]:\n"))
        if mroutes == 4:
            print("\nThere seems to be a fourth way, but it's a large drop. You decide to choose another way.")
            border()
            mine_routes()
        elif mroutes == 1:
            print("\nThe water route is too deep to navigate without equipment. Choose another way.")
            border()
            mine_routes()
        elif mroutes == 2:
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
            inv["pickaxe"] += 1
            inv["diving gear"] += 1
            checkinv()
            print("\nYou quickly run to the next tunnel, which leads to an elevator.")
            elevator_game()
        elif mroutes == 3:
            print("\nYou take the mine cart down a thrilling ride, landing at the bottom!")
            print("You find a skeleton holding diving gear and a pickaxe.")
            inv["pickaxe"] += 1
            inv["diving gear"] += 1
            checkinv()
            print("\nA giant spider appears! You escape to a nearby tunnel leading to an elevator.")
            elevator_game()
    except ValueError:
        print("Invalid input. Returning to mine routes.")
        mine_routes()

def mine_collapse():
    """Handles the mine collapse event."""
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
    mine_routes()
menu()