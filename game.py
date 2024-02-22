import random
import time
import tkinter as tk
from PIL import Image, ImageTk
from copy import deepcopy
from collections import deque

def initialize_grid(grid_size, num_carrot, num_holes):
    grid = [['-' for _ in range(grid_size)] for _ in range(grid_size)]

    rabbit_x, rabbit_y = random.randint(
        0, grid_size-1), random.randint(0, grid_size-1)
    grid[rabbit_x][rabbit_y] = 'r'

    carrots = []
    for _ in range(num_carrot):
        while True:
            x, y = random.randint(
                0, grid_size-1), random.randint(0, grid_size-1)
            if grid[x][y] == '-':
                grid[x][y] = 'c'
                carrots.append((x, y))
                break

    holes = []
    for _ in range(num_holes):
        while True:
            x, y = random.randint(
                0, grid_size-1), random.randint(0, grid_size-1)
            if grid[x][y] == '-':
                grid[x][y] = 'O'
                holes.append((x, y))
                break

    return grid, rabbit_x, rabbit_y, carrots, holes


def display_grid_tk(grid):
    canvas.delete("all")
    cell_size = 50 
    grid_height = len(grid)
    grid_width = len(grid[0])
    canvas_width = grid_width * cell_size
    canvas_height = grid_height * cell_size
    canvas.update()
    
    x_margin = (canvas.winfo_width() - canvas_width) // 2
    y_margin = (canvas.winfo_height() - canvas_height) // 2
    
    canvas.create_rectangle(x_margin, y_margin, x_margin + canvas_width, y_margin + canvas_height, outline="black")
    
    for i in range(grid_height):
        for j in range(grid_width):
            canvas.create_rectangle(x_margin + j * cell_size, y_margin + i * cell_size,
                                    x_margin + (j + 1) * cell_size, y_margin + (i + 1) * cell_size, outline="black")
            
            if grid[i][j] == 'r':
                canvas.create_image(x_margin + j * cell_size, y_margin + i * cell_size, anchor=tk.NW, image=rabbit_image)
            elif grid[i][j] == 'c':
                canvas.create_image(x_margin + j * cell_size, y_margin + i * cell_size, anchor=tk.NW, image=carrot_image)
            elif grid[i][j] == 'O':
                canvas.create_image(x_margin + j * cell_size, y_margin + i * cell_size, anchor=tk.NW, image=hole_image)
            elif grid[i][j] == 'R':
                canvas.create_image(x_margin + j * cell_size, y_margin + i * cell_size, anchor=tk.NW, image=rabbit_carrot_image)
                
    steps_label.config(text=f'Steps: {user_steps}')
    steps_label.grid(row=1, column=2)
    root.update()


def jump(grid, rabbit_x, rabbit_y):
    isCrossed = False
    grid_size = len(grid)
    new_x = rabbit_x
    new_y = rabbit_y
    if rabbit_x-2 >= 0 and grid[rabbit_x-1][rabbit_y] == 'O' and grid[rabbit_x-2][rabbit_y] != 'c':
        new_x = rabbit_x-2
        isCrossed = True
    if rabbit_y-2 >= 0 and grid[rabbit_x][rabbit_y-1] == 'O' and grid[rabbit_x][rabbit_y-2] != 'c' and not isCrossed:
        new_y = rabbit_y-2
        isCrossed = True
    if rabbit_x+2 < grid_size and grid[rabbit_x+1][rabbit_y] == 'O' and grid[rabbit_x+2][rabbit_y] != 'c' and not isCrossed:
        new_x = rabbit_x+2
        isCrossed = True
    if rabbit_y+2 < grid_size and grid[rabbit_x][rabbit_y+1] == 'O' and grid[rabbit_x][rabbit_y+2] != 'c' and not isCrossed:
        new_y = rabbit_y+2
        isCrossed = True
    return (new_x, new_y, isCrossed)

def adjacent_target_cord(grid, rabbit_x, rabbit_y, target):
    adj = [(0, -1), (0, 1), (-1, 0), (1, 0),
           (-1, -1), (-1, 1), (1, -1), (1, 1)]
    for dx, dy in adj:
        new_x, new_y = rabbit_x + dx, rabbit_y + dy
        if 0 <= new_x < len(grid) and 0 <= new_y < len(grid) and grid[new_x][new_y] == target:
            return (new_x, new_y)
    return (-1, -1)

class Path:
    def __init__(self, x, y, path):
        self.x = x
        self.y = y
        self.path = path

def bfs(grid, moves, start_x, start_y, goal_x, goal_y):
    visited = set()
    queue = deque([Path(start_x, start_y, [])])

    while queue:
        val = queue.popleft()
        x, y, path = val.x, val.y, val.path
        if abs(x - goal_x) <= 1 and abs(y - goal_y) <= 1:
            return path

        for dx, dy in moves:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < len(grid) and 0 <= new_y < len(grid)) and ((new_x, new_y) not in visited) and (grid[new_x][new_y] != 'c'):
                if grid[new_x][new_y] == 'O':
                    new_x, new_y, isCrossed = jump(grid, x, y)
                    if isCrossed:
                        visited.add((new_x, new_y))
                        queue.append(
                            Path(new_x, new_y, path + [(new_x, new_y)]))
                else:
                    visited.add((new_x, new_y))
                    queue.append(Path(new_x, new_y, path + [(new_x, new_y)]))

    return []

def find_shortest_path_to_win(grid, rabbit_x, rabbit_y, carrots, holes):
    moves = [(0, -1), (0, 1), (-1, 0), (1, 0),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]

    path_to_carrot = []
    path_to_hole = []

    shortest_path_len = float('inf')

    for carrot_x, carrot_y in carrots:
        new_x, new_y = rabbit_x, rabbit_y
        new_path_to_carrot = bfs(
            grid, moves, rabbit_x, rabbit_y, carrot_x, carrot_y)
        for hole_x, hole_y in holes:
            if len(new_path_to_carrot):
                new_x, new_y = new_path_to_carrot[-1]
            new_path_to_hole = bfs(grid, moves, new_x, new_y, hole_x, hole_y)

            total_path_len = len(new_path_to_carrot) + len(new_path_to_hole)
            if total_path_len < shortest_path_len:
                shortest_path_len = total_path_len
                path_to_carrot = new_path_to_carrot[:]
                path_to_hole = new_path_to_hole[:]

    return (path_to_carrot, path_to_hole)

def simulate(grid, rabbit_x, rabbit_y, path_to_carrot, path_to_hole, user_steps):
    steps = 0
    display_grid_tk(grid)
    minimum_steps_label.config(text=f'Congats you made it in {user_steps} steps')
    user_steps_label.config(text="Here is simulation of an efficient approach")
    root.update()
    time.sleep(2)
    minimum_steps_label.config(text="")
    user_steps_label.config(text="")
    time.sleep(1)

    for x, y in path_to_carrot:
        grid[rabbit_x][rabbit_y] = '-'
        grid[x][y] = 'r'
        rabbit_x, rabbit_y = x, y
        display_grid_tk(grid)
        root.update()
        time.sleep(1)
        steps += 1

    temp_x, temp_y = adjacent_target_cord(grid, rabbit_x, rabbit_y, 'c')
    grid[temp_x][temp_y] = '-'
    grid[rabbit_x][rabbit_y] = 'R'
    display_grid_tk(grid)
    root.update()
    time.sleep(1)
    steps += 1

    for x, y in path_to_hole:
        grid[rabbit_x][rabbit_y] = '-'
        grid[x][y] = 'R'
        rabbit_x, rabbit_y = x, y
        display_grid_tk(grid)
        root.update()
        time.sleep(1)
        steps += 1

    display_grid_tk(grid)
    minimum_steps_label.config(text=f'Minimum number of steps required: {steps}')
    user_steps_label.config(text=f'Total number of steps you made: {user_steps}')
    root.update()
    time.sleep(2)
    return
    




def start_game():
    global grid_size, num_carrot, num_holes, grid, rabbit_x, rabbit_y, carrots, holes, grid_1, rabbit_x_1, rabbit_y_1, carrot_held, isWon, user_steps

    grid_size = int(grid_size_entry.get())
    num_carrot = int(num_carrot_entry.get())
    num_holes = int(num_holes_entry.get())

    grid, rabbit_x, rabbit_y, carrots, holes = initialize_grid(
        grid_size, num_carrot, num_holes)
    grid_1 = deepcopy(grid)
    rabbit_x_1 = rabbit_x
    rabbit_y_1 = rabbit_y
    carrot_held = False
    isWon = False
    user_steps = 0

    display_grid_tk(grid)

    # Update event bindings
    root.bind("<Left>", move_left)
    root.bind("<Right>", move_right)
    root.bind("<Up>", move_up)
    root.bind("<Down>", move_down)
    root.bind("w", move_up)
    root.bind("s", move_down)
    root.bind("a", move_left)
    root.bind("d", move_right)
    root.bind("p", pickup_carrot)
    root.bind("j", jump_rabbit)
    root.bind("q", quit_game)
    root.bind("c", pickup_carrot)

    size_label.destroy()
    grid_size_entry.destroy()
    carrots_label.destroy()
    num_carrot_entry.destroy()
    holes_label.destroy()
    num_holes_entry.destroy()
    start_button.destroy()



def move_left(event):
    move_rabbit(0, -1)

def move_right(event):
    move_rabbit(0, 1)

def move_up(event):
    move_rabbit(-1, 0)

def move_down(event):
    move_rabbit(1, 0)

def move_rabbit(dx, dy):
    global rabbit_x, rabbit_y, carrot_held, user_steps, isWon

    new_x, new_y = rabbit_x + dx, rabbit_y + dy
    if 0 <= new_x < grid_size and 0 <= new_y < grid_size and grid[new_x][new_y] != 'c' and grid[new_x][new_y] != 'O':
        grid[rabbit_x][rabbit_y], grid[new_x][new_y] = '-', 'R' if carrot_held else 'r'
        rabbit_x, rabbit_y = new_x, new_y
        display_grid_tk(grid)
        user_steps += 1  # Increment steps when user moves
        steps_label.config(text=f'Steps: {user_steps}')

    if carrot_held and ((rabbit_x >= 1 and grid[rabbit_x-1][rabbit_y]=='O') or (rabbit_x < grid_size-1 and grid[rabbit_x+1][rabbit_y]=='O') or (rabbit_y >= 1 and grid[rabbit_x][rabbit_y-1]=='O') or (rabbit_y < grid_size-1 and grid[rabbit_x][rabbit_y+1]=='O') or (rabbit_x >= 1 and rabbit_y >= 1 and grid[rabbit_x-1][rabbit_y-1]=='O') or (rabbit_x >= 1 and rabbit_y < grid_size - 1 and grid[rabbit_x-1][rabbit_y+1]=='O') or (rabbit_x < grid_size - 1 and rabbit_y >= 1 and grid[rabbit_x+1][rabbit_y-1]=='O') or (rabbit_x < grid_size - 1 and rabbit_y < grid_size - 1 and grid[rabbit_x+1][rabbit_y+1]=='O')):
        isWon=True

    if isWon:

        path_to_carrot, path_to_hole = find_shortest_path_to_win(
            grid_1, rabbit_x_1, rabbit_y_1, carrots, holes)
        simulate(grid_1, rabbit_x_1, rabbit_y_1,
                 path_to_carrot, path_to_hole, user_steps)

def pickup_carrot(event):
    global rabbit_x, rabbit_y, carrot_held, user_steps

    adj = [(0, -1), (0, 1), (-1, 0), (1, 0),
           (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dx, dy in adj:
        new_x, new_y = rabbit_x + dx, rabbit_y + dy
        if 0 <= new_x < grid_size and 0 <= new_y < grid_size and grid[new_x][new_y] == 'c':
            grid[new_x][new_y] = '-'
            carrot_held = True
            grid[rabbit_x][rabbit_y] = 'R'
            display_grid_tk(grid)
            user_steps += 1 
            steps_label.config(text=f'Steps: {user_steps}')
            break

def jump_rabbit(event):
    global rabbit_x, rabbit_y

    new_x, new_y, _ = jump(grid, rabbit_x, rabbit_y)
    grid[rabbit_x][rabbit_y], grid[new_x][new_y] = '-', 'R' if carrot_held else 'r'
    rabbit_x, rabbit_y = new_x, new_y
    display_grid_tk(grid)
    user_steps += 1 
    steps_label.config(text=f'Steps: {user_steps}')

def quit_game(event):
    root.destroy()

def restart_game():
    global grid, rabbit_x, rabbit_y, carrots, holes, grid_1, rabbit_x_1, rabbit_y_1, carrot_held, isWon, user_steps
    grid, rabbit_x, rabbit_y, carrots, holes = initialize_grid(
        grid_size, num_carrot, num_holes)
    grid_1 = deepcopy(grid)
    rabbit_x_1 = rabbit_x
    rabbit_y_1 = rabbit_y
    carrot_held = False
    isWon = False
    user_steps = 0
    minimum_steps_label.config(text="")
    user_steps_label.config(text="")
    display_grid_tk(grid)
    root.update()

# GUI initialization
root = tk.Tk()
root.title("Rabbit Game")
canvas = tk.Canvas(root, width=500, height=500)
canvas.grid(row=0, column=0, columnspan=3, pady=10)
root.grid_rowconfigure(1, weight=1)

# Load PNG images
rabbit_png = Image.open("rabbit.png")
rabbit_carrot_png = Image.open("rabbit_carrot.png")
carrot_png = Image.open("carrot.png")
hole_png = Image.open("hole.png")
rabbit_png = rabbit_png.resize((50, 50), Image.ANTIALIAS)
rabbit_carrot_png = rabbit_carrot_png.resize((50, 50), Image.ANTIALIAS)
carrot_png = carrot_png.resize((50, 50), Image.ANTIALIAS)
hole_png = hole_png.resize((50, 50), Image.ANTIALIAS)
rabbit_image = ImageTk.PhotoImage(rabbit_png)
rabbit_carrot_image = ImageTk.PhotoImage(rabbit_carrot_png)
carrot_image = ImageTk.PhotoImage(carrot_png)
hole_image = ImageTk.PhotoImage(hole_png)

# Game initialization
grid_size = 0
num_carrot = 0
num_holes = 0
grid = []
rabbit_x = 0
rabbit_y = 0
carrots = []
holes = []
grid_1 = []
rabbit_x_1 = 0
rabbit_y_1 = 0
carrot_held = False
isWon = False
user_steps = 0



# Input fields
# Input fields
size_label = tk.Label(root, text="Size:")
size_label.grid(row=1, column=0)

grid_size_entry = tk.Entry(root)
grid_size_entry.grid(row=1, column=1)

carrots_label = tk.Label(root, text="Carrots:")
carrots_label.grid(row=2, column=0)

num_carrot_entry = tk.Entry(root)
num_carrot_entry.grid(row=2, column=1)

holes_label = tk.Label(root, text="Holes:")
holes_label.grid(row=3, column=0)

num_holes_entry = tk.Entry(root)
num_holes_entry.grid(row=3, column=1)

start_button = tk.Button(root, text="Start Game", command=start_game)
start_button.grid(row=2, column=2)

restart_button = tk.Button(root, text="Restart Game", command=restart_game)
restart_button.grid(row=3, column=2, pady=(2, 10))

steps_label = tk.Label(root, text=f'Steps: {user_steps}')
steps_label.grid(row=1, column=2)


minimum_steps_label = tk.Label(root, text="")
minimum_steps_label.grid(row=2, column=0, columnspan=2, pady=(2, 1))
user_steps_label = tk.Label(root, text="")
user_steps_label.grid(row=3, column=0, columnspan=2, pady=(2, 10))


root.mainloop()
