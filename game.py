import random

from flask import session

directions = ["LEFT", "RIGHT", "UP", "DOWN"]
reverse_directions = {
    "UP": "DOWN",
    "LEFT": "RIGHT",
    "RIGHT": "LEFT",
    "DOWN": "UP",
}


def reveal_map():
    """Reveal the map entirely"""

    session["game_map_visibility"] = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1],
    ]


def create_simple_map_structure():
    """Create a simple map structure with caverns only"""

    return [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]


def reveal_location(y, x):
    """Reveal a specific location"""

    session["game_map_visibility"][y][x] = 1


def hide_location(y, x):
    """Hide a specific location"""

    session["game_map_visibility"][y][x] = 0


def create_map(difficulty):
    """Create a map of a certain difficulty"""

    game_map = create_simple_map_structure()
    corridors_number = get_corridors_number(difficulty)

    for i in range(corridors_number):
        (y, x) = get_random_cavern(game_map)
        game_map[y][x] = random.randint(5, 6)

    return game_map


def get_random_cavern(game_map):
    """Return a random cavern location"""

    y, x = 0, 0
    while game_map[y][x] != 0:
        y, x = random.randint(0, 5), random.randint(0, 7)

    return y, x


def get_corridors_number(difficulty):
    """Get the number of corridors depending on difficulty"""

    match difficulty:
        case 1:
            return random.randint(8, 14)
        case 2:
            return 18
        case 3:
            return 26

    return 0


def is_map_playable(game_map):
    """Determine whether the map is playable or not (=> all locations are accessible)"""

    neighbours = [(get_random_cavern(game_map), "CAVERN")]
    visited = set()
    while len(neighbours) != 0:
        ((y, x), entry) = neighbours.pop()

        room_type = game_map[y][x]
        if room_type == 0:
            actual_entry = "CAVERN"  # TODO: refactor variable name
        elif room_type == 5:
            actual_entry = "corridor1" if entry in ["UP", "LEFT"] else "corridor2"
        elif room_type == 6:
            actual_entry = "corridor1" if entry in ["UP", "RIGHT"] else "corridor2"
        else:
            actual_entry = entry

        if ((y, x), actual_entry) in visited:
            continue

        visited.add(((y, x), actual_entry))
        room_exits = get_exits(y, x, game_map, entry)
        for i in room_exits:
            neighbours.append(i)

    return len(visited) == room_number(game_map)


def room_number(game_map):
    """Return the number of rooms (caverns + corridors)"""

    total = 0
    for y in game_map:
        for x in y:
            if x in [5, 6]:
                total += 2
            else:
                total += 1
    return total


def get_exits(y, x, game_map, entry):
    """Return the list of possible exits of a specific location"""

    exits = []
    if game_map[y][x] != 5 and game_map[y][x] != 6:
        exits.append((wrap_position(y + 1, x), "UP"))
        exits.append((wrap_position(y - 1, x), "DOWN"))
        exits.append((wrap_position(y, x + 1), "LEFT"))
        exits.append((wrap_position(y, x - 1), "RIGHT"))
    elif game_map[y][x] == 5:
        if entry == "UP" or entry == "LEFT":
            exits.append((wrap_position(y - 1, x), "DOWN"))
            exits.append((wrap_position(y, x - 1), "RIGHT"))
        elif entry == "DOWN" or entry == "RIGHT":
            exits.append((wrap_position(y + 1, x), "UP"))
            exits.append((wrap_position(y, x + 1), "LEFT"))
    elif game_map[y][x] == 6:
        if entry == "UP" or entry == "RIGHT":
            exits.append((wrap_position(y - 1, x), "DOWN"))
            exits.append((wrap_position(y, x + 1), "LEFT"))
        elif entry == "DOWN" or entry == "LEFT":
            exits.append((wrap_position(y + 1, x), "UP"))
            exits.append((wrap_position(y, x - 1), "RIGHT"))

    return exits


def wrap_position(y, x):
    """Wrap position to stay inside the game grid"""

    new_y = y
    new_x = x
    if x < 0:
        new_x = 7
    elif x > 7:
        new_x = 0
    elif y < 0:
        new_y = 5
    elif y > 5:
        new_y = 0

    return new_y, new_x


def place_pits(game_map, number_pits=2):
    """Place a specific amount of pits in a randomly available cavern and color the adjacent caverns"""

    for i in range(number_pits):
        (y, x) = get_random_cavern(game_map)
        session[f"pit_{i + 1}"] = (y, x)
        session["unavailable_locations"].append((y, x))
        game_map[y][x] = 4

        for direction in directions:
            adjacent_y, adjacent_x = get_adjacent_cavern(y, x, game_map, direction)
            color_cavern(adjacent_y, adjacent_x, game_map, 2)


def place_wumpus(game_map):
    """Place the wumpus in a randomly available cavern and color the adjacent caverns"""

    y, x = get_random_cavern(game_map)
    session["wumpus"] = (y, x)
    session["unavailable_locations"].append((y, x))

    for direction1 in directions:
        neighbour1 = get_adjacent_cavern(y, x, game_map, direction1)
        color_cavern(neighbour1[0], neighbour1[1], game_map, 1)

        for direction2 in directions:
            neighbour2 = get_adjacent_cavern(neighbour1[0], neighbour1[1], game_map, direction2)
            color_cavern(neighbour2[0], neighbour2[1], game_map, 1)


def place_bats(game_map, number_bats):
    """Place a specific number of bats in a random available cavern"""

    for i in range(number_bats):
        y, x = get_random_cavern(game_map)
        while (y, x) in session["unavailable_locations"]:
            y, x = get_random_cavern(game_map)

        session[f"bat_{i + 1}"] = [(y, x),
                                   False]  # TODO: maybe store trigger state is not needed : check whether the case is revealed or not
        session["unavailable_locations"].append((y, x))


def place_player(game_map):
    """Place a player in a randomly available cavern"""

    y, x = get_random_cavern(game_map)
    while (y, x) in session["unavailable_locations"]:
        y, x = get_random_cavern(game_map)

    session["player"] = (y, x)
    reveal_location(y, x)


def get_adjacent_cavern(y, x, game_map, direction, reveal_path=False):
    """Get the adjacent cavern of a location depending on the direction"""

    if direction == "UP":
        y, x = wrap_position(y - 1, x)
    elif direction == "LEFT":
        y, x = wrap_position(y, x - 1)
    elif direction == "RIGHT":
        y, x = wrap_position(y, x + 1)
    elif direction == "DOWN":
        y, x = wrap_position(y + 1, x)

    while game_map[y][x] not in [0, 1, 2, 3, 4]:
        if reveal_path:
            reveal_location(y, x)

        new_y, new_x, new_direction = get_corridor_exit(y, x, game_map, reverse_directions[direction])

        direction = new_direction
        y, x = new_y, new_x

    return y, x


def move_player(direction):
    """Move the player in a direction"""

    prev_y, prev_x = session["player"]
    new_y, new_x = prev_y, prev_x
    entered_by = session.get("entered_by", "")
    game_map = session["game_map"]
    express = session.get("express", False)
    blindfold = session.get("blindfold", False)

    if express:
        new_y, new_x = get_adjacent_cavern(prev_y, prev_x, game_map, direction, False if blindfold else True)
    else:
        if direction == "LEFT":
            new_y, new_x = wrap_position(prev_y, prev_x - 1)
        elif direction == "RIGHT":
            new_y, new_x = wrap_position(prev_y, prev_x + 1)
        elif direction == "DOWN":
            new_y, new_x = wrap_position(prev_y + 1, prev_x)
        elif direction == "UP":
            new_y, new_x = wrap_position(prev_y - 1, prev_x)

        session["entered_by"] = reverse_directions[direction]

        if game_map[prev_y][prev_x] == 5:
            if (entered_by in ("LEFT", "UP") and direction not in ("LEFT", "UP")) or (
                    entered_by in ("RIGHT", "DOWN") and direction not in ("RIGHT", "DOWN")):
                new_y, new_x = prev_y, prev_x
                session["entered_by"] = entered_by
        elif game_map[prev_y][prev_x] == 6:
            if (entered_by in ("LEFT", "DOWN") and direction not in ("LEFT", "DOWN")) or (
                    entered_by in ("RIGHT", "UP") and direction not in ("RIGHT", "UP")):
                new_y, new_x = prev_y, prev_x
                session["entered_by"] = entered_by

    session["player"] = (new_y, new_x)

    if blindfold:
        hide_location(prev_y, prev_x)

    reveal_location(new_y, new_x)

    if (new_y, new_x) in (session["wumpus"], session["pit_1"], session["pit_2"]):
        session["game_state"] = "DEFEAT"
        reveal_map()


def get_corridor_exit(y, x, game_map, entry):  # TODO: refactor with an object UP: (0, -1) LEFT: (-1, 0), etc...
    """Get the corridor exit as well as the direction to exit the corridor"""

    if game_map[y][x] == 5:
        if entry == "UP":
            new_y, new_x = wrap_position(y, x - 1)
            return new_y, new_x, "LEFT"
        elif entry == "LEFT":
            new_y, new_x = wrap_position(y - 1, x)
            return new_y, new_x, "UP"
        elif entry == "DOWN":
            new_y, new_x = wrap_position(y, x + 1)
            return new_y, new_x, "RIGHT"
        else:
            new_y, new_x = wrap_position(y + 1, x)
            return new_y, new_x, "DOWN"
    elif game_map[y][x] == 6:
        if entry == "UP":
            new_y, new_x = wrap_position(y, x + 1)
            return new_y, new_x, "RIGHT"
        elif entry == "LEFT":
            new_y, new_x = wrap_position(y + 1, x)
            return new_y, new_x, "DOWN"
        elif entry == "DOWN":
            new_y, new_x = wrap_position(y, x - 1)
            return new_y, new_x, "LEFT"
        else:
            new_y, new_x = wrap_position(y - 1, x)
            return new_y, new_x, "UP"
    else:
        return None


def color_cavern(y, x, game_map, cavern_type):
    """Color a specific cavern"""

    current_type = game_map[y][x]

    if current_type not in [0, 1, 2, 3]:
        return

    if session.get("wumpus") == (y, x):
        return

    if current_type == 0:
        game_map[y][x] = cavern_type
    if (current_type == 1 and cavern_type == 2) or (current_type == 2 and cavern_type == 1):
        game_map[y][x] = 3


def shoot_arrow(direction):
    """Shoot the arrow in a specific direction"""

    game_map = session["game_map"]
    wumpus = session["wumpus"]
    y, x = session["player"]
    target = get_adjacent_cavern(y, x, game_map, direction)

    if target == wumpus:
        session["game_state"] = "VICTORY"
    else:
        session["game_state"] = "DEFEAT"

    reveal_map()