# Written by Eirik Vesterkjær
# This is a basic dungeon layout generator.
# It supports dungeons of dimension > 5x5.
# Rooms are placed randomly, and the total area of rooms placed
# is determined by a density-parameter.
# Paths connect the rooms. The paths are drawn by separating
# diagonal lines them into two straight parts.
# To determine which paths to draw, I use a modified Prim's Algorithm.
# It creates a span tree which includes all rooms, but the weight of a new room
# is only determined by the distance between it and -any- room which
# has already been added to the span tree. So it is not a true MST.


import random
import sys

ROOM = 0
STONE = 1
WALL = 2

"""
Prints a finished dungeon, coordinates axis optional.
@arg dungeon: 2d array, finished dungeon
@arg axis_enabled: bool
"""
def printFinishedDungeon(dungeon, axis_enabled=True):
    ylength = len(dungeon[0])
    # Counter for X axis
    counter = 0
    # Counter for y axis
    marks = ylength // 5
    
    if axis_enabled:
        # Y-axis
        print("    ", end="")
        for i in range(marks):
            print(str(i*5).ljust(10, '-'), end="")
        print("Y")

    for row in dungeon:
        # X-axis
        if axis_enabled:
            print(str(counter).ljust(4) if (counter % 5) == 0 else "|   ", end= "")
            counter += 1
        # Actual dungeon printing
        for elem in row:
            if (elem == WALL):
                print("[]", end="")
            elif elem == STONE:
                print("**", end="")
            else:
                print("  ", end="")
        print()
    if axis_enabled:
        print("X")


"""
Euclidian distance rounded down to int
@arg x0,y0: coord
@arg x1,y1: coord
"""
def dist(x0, y0, x1, y1):
    return int(((x1-x0)**2 + (y1-y0)**2)**.5)

"""
Places a room that is of area height*width, 
Where x0,y0 is in the corner with lowest x / y indexes.
@arg dungeon: 2d array
@arg x0,y0: int coord
@arg height: int room height
@arg width: int room width
"""
def placeRoom(dungeon, x0, y0, height, width):
    # Place ROOM cells
    for x in range(x0, x0 + height):
        for y in range(y0, y0 + width):
            dungeon[x][y] = ROOM
    # Place WALL around room only if there is not already ROOM there
    for x in range(x0 - 1, x0 + height + 1):
        if dungeon[x][y0 - 1] == STONE:
            dungeon[x][y0 -1] = WALL
        if dungeon[x][y0 + width] == STONE:
            dungeon[x][y0 + width] = WALL
    for y in range(y0 - 1, y0 + width + 1):
        if dungeon[x0 - 1][y] == STONE:
            dungeon[x0 - 1][y] = WALL
        if dungeon[x0 + height][y] == STONE:
            dungeon[x0 + height][y] = WALL


"""
Creates an array[x][y] of size xlength * ylength, then
fills it with rooms
@arg xlength: int array length in x dimension
@arg ylength: int array length in y dimension
@arg density: float area of rooms placed as fraction of total array area
@arg random seed: int seed for RNG
@return dungeon: 2d array populated with rooms
@return room_list: coords of corners of all placed rooms, for use in pathmaking
"""
def getDungeonRooms(xlength, ylength, density, random_seed):
    random.seed(random_seed)
    # Create dungeon. If it is small, do not make rooms
    dungeon = [[ 1  for i in range(ylength)] for j in range(xlength)]
    if xlength < 4 or ylength < 4:
        return dungeon
    # Limiting room size
    max_room_height = 15
    max_room_width = 15
    # Room size scales with array size
    scale = 0.5
    # Area of rooms placed will be >= the area intensity * ylength * xlength
    intensity = density
    totalArea = xlength * ylength
    placedArea = 0

    room_list = []
    
    while placedArea < intensity * totalArea:
        room_height = random.randint(2, max(min(int(scale * xlength / 3), max_room_height), 2))
        room_width = random.randint(2, max(min(int(scale * ylength / 3), max_room_width), 2))

        # Rooms can overlap, so coords are chosen completely randomly
        x = random.randint(1, xlength - 1 - room_height)
        y = random.randint(1, ylength - 1 - room_width)

        placeRoom(dungeon, x, y, room_height, room_width)
        placedArea += room_height * room_width

        # Offset coords so that they are approx in the center of the room
        x += int(room_height / 2) 
        y += int(room_width / 2)

        room_list.append( (x,y) )

    return dungeon, room_list

"""
Places a path from x0,y0 to x1,y1 in a 2d array dungeon
Splits diagonal paths into two straight parts
@arg dungeon: 2d array
@arg x0,y0: int coords
@arg x1,y1: int coords

"""
def placeDungeonPath(dungeon, x0, y0, x1, y1):
    # No path to draw!
    if x0 == x1 and y0 == y1:
        return dungeon

    # Make drawing coords increasing from x0 to x1, and y0 to y1.
    if x0 >= x1 and y0 >= y1:
        temp = x0
        x0 = x1
        x1 = temp
        temp = y0
        y0 = y1
        y1 = temp

    # (midX, midY) is the coord of the bend in the path
    midX = 0 
    midY = 0


    if x0 < x1:
        midX = x1
        midY = y0


    else: # If both were <, then x0,y0 would have been swapped with x1,y1 above
        midX = x0
        midY = y1


    # Todo: Limit these to 0 and length/height

    # Draw path from (x0,y0) to (midX, midY)
    for x in range(min(x0, midX), max(x0 + 1, midX + 1)):
        dungeon[x][y0] = ROOM
        if dungeon[x][y0 - 1] == STONE:
            dungeon[x][y0 - 1] = WALL
        if dungeon[x][y0 + 1] == STONE:
            dungeon[x][y0 + 1] = WALL
    for y in range(min(y0, midY), max(midY + 1, y0, + 1)):
        dungeon[x0][y] = ROOM
        if dungeon[x0 - 1][y] == STONE:
            dungeon[x0 - 1][y] = WALL
        if dungeon[x0 + 1][y] == STONE:
            dungeon[x0 + 1][y] = WALL
    
    # Draw path from (midX, midY) to (x1, y1)
    for x in range(min(midX, x1), max(midX + 1, x1 + 1)):
        dungeon[x][y1] = ROOM
        if dungeon[x][y1 - 1] == STONE:
            dungeon[x][y1 - 1] = WALL
        if dungeon[x][y1 + 1] == STONE:
            dungeon[x][y1 + 1] = WALL
    for y in range(min(midY, y1), max(midY + 1, y1, + 1)):
        dungeon[x1][y] = ROOM
        if dungeon[x1 - 1][y] == STONE:
            dungeon[x1 - 1][y] = WALL
        if dungeon[x1 + 1][y] == STONE:
            dungeon[x1 + 1][y] = WALL


    # Replace STONE around the path with WALL
    for i in range(max(0, x0 - 1), min(x0 + 2, len(dungeon))):
        for j in range(max(0, y0 - 1), min(y0 + 2, len(dungeon[i]))):
            dungeon[i][j] = WALL if dungeon[i][j] == STONE else dungeon[i][j]
    
    for i in range(max(0, midX - 1), min(midX + 2, len(dungeon))):
        for j in range(max(0, midY - 1), min(midY + 2, len(dungeon[i]))):
            dungeon[i][j] = WALL if dungeon[i][j] == STONE else dungeon[i][j]
    
    for i in range(max(0, x1 - 1), min(x1 + 2, len(dungeon))):
        for j in range(max(0, y1 - 1), min(y1 + 2, len(dungeon[i]))):
            dungeon[i][j] = WALL if dungeon[i][j] == STONE else dungeon[i][j]
    


"""
Makes a span tree connecting all rooms using a modified Prim's algorithm.
Distance to new rooms added to the span tree is the distance to the closest room,
so this does not make a true MST. But, it connects all rooms.
@arg dungeon: 2d array
@arg room_list: list of coord int tuples (x,y) of room centers
@arg random_seed: int seed for RNG
"""
def makeDungeonPaths(dungeon, room_list, random_seed):
    random.seed(random_seed)

    n = len(room_list)
    # List of rooms in span tree
    connected_rooms = []
    # Distances to rooms not in span tree
    distances = dict()
    # Start the span tree with the room added last
    connected_rooms.append(room_list.pop(-1))
    for room in room_list:
        # Each entry in the dict is given by:
        # distances[to this room] = (shortest distance, from this room)
        distances[room] = (dist(connected_rooms[0][0], 
                        connected_rooms[0][1], room[0], room[1]), connected_rooms[0])
    # Each room is now in the dict

    # Prim's Algorithm
    i = 0
    while len(distances):
        i += 1
        # Get closest room from the dict
        closest_room_source = (-1, (1,1))
        closest_room = (1,1)
        for key in distances:
            if distances[key][0] < closest_room_source[0] or closest_room_source[0] < 0:
                closest_room = key
                closest_room_source = distances[key]

        # Expand MST with the closest room
        distances.pop( closest_room )
        placeDungeonPath(dungeon, closest_room_source[1][0], closest_room_source[1][1], closest_room[0], closest_room[1])
        connected_rooms.append(closest_room)

        # Calculate new distances in MST
        for room in distances:
            this_room_dist = dist(closest_room[0], closest_room[1], room[0], room[1])
            # <= so that we prefer expanding the MST from newly added rooms.
            if this_room_dist <= distances[room][0]:
                # Commenting out the next statement results in an interesting effect 
                # where all rooms are connected to a central room
                distances[room] = (this_room_dist, closest_room) 
                continue # This is here in case the prev line is commented out

        # Prevent infinite loop if something goes horribly wrong (hasn't for me so far though)
        if i > 500:
            print("Error! Possible infinite loop in makeDungeonPaths - 500 paths placed.")
            break



"""
Creates a dungeon[x][y] of dimensions xlength, ylength, with the given density and seed
@arg xlength: int dungeon length in x dim
@arg ylength: int dungeon length in y dim
@density: float density of rooms, recommended around 0.2-0.5
@random_seed: int seed for RNG
@return: 2d array representing a dungeon
"""
def getDungeon(xlength, ylength, density, random_seed):
    # Minimum size
    if (xlength < 5 or ylength < 5):
        print("Error! Minimum size 5x5")
        return [[]]
    dungeon, room_list = getDungeonRooms(xlength, ylength, density, random_seed)
    makeDungeonPaths(dungeon, room_list, random_seed)

    return dungeon


# For running in a CLI
if __name__ == "__main__":
    if 2 < len(sys.argv):
        height = int(sys.argv[1])
        width = int(sys.argv[2])
        density_val = 0.25
        ran_seed = 0
        if 3 < len(sys.argv):
            density_val = float(sys.argv[3])
            if 4 < len(sys.argv):
                ran_seed = int(sys.argv[4])
        printFinishedDungeon( getDungeon( height, width, density_val, ran_seed ), axis_enabled=False )
    
    else:
        print("Error! Run as: python dungeon.py height width [density 0 <= float <= 1] [seed int]"
        ,"\nMinimum size 5x5")