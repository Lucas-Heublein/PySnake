# -*- coding: utf-8 -*-
"""
@author: Lucas
This is not the most efficient (or cleanest) way to do it, but i had some fun programming it.
Feel free to change anything you like ^^
"""
try:
    import tkinter as tk 
except ImportError:
    import Tkinter as tk  # use a capital T for python 2.
import random
import copy
import os
import numpy as np
import gc
import heapq


class Cell(object):
    def __init__(self, x, y, reachable):
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f


class AStar(object):
    def __init__(self, walls, snake_places_start, start_place, goal, grid_height=40, grid_width=40):
        self.opened = []
        heapq.heapify(self.opened)
        self.closed = set()
        self.cells = []
        self.path_to_food = []
        self.grid_height = grid_height
        self.grid_width = grid_width
        self.walls = walls
        self.start_place = start_place
        self.goal = goal
        self.path_curr = None
        self.old_snake_places = snake_places_start
        self.snake_places = 0

    def update_cells_and_pos(self, snake_places, goal):
        self.opened = []
        self.closed = set()
        self.path_to_food = []
        self.goal = goal
        self.path_curr = None
        self.snake_places = snake_places
        for x,y in zip(self.old_snake_places[1], self.old_snake_places[0]):
            self.cells[x*self.grid_width+y].reachable = True
        for x,y in zip(self.snake_places[1], self.snake_places[0]):
            self.cells[x*self.grid_width+y].reachable = False
        self.old_snake_places = self.snake_places
        self.end = self.get_cell(self.goal%self.grid_width, self.goal//self.grid_height)

    def init_grid(self):
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in self.walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(self.start_place%self.grid_width, self.start_place//self.grid_height)
        self.end = self.get_cell(self.goal%self.grid_width, self.goal//self.grid_height)

    def get_heuristic(self, cell):
        return 10 * (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_cell(self, x, y):
        return self.cells[x * self.grid_height + y]

    def get_adjacent_cells(self, cell):
        cells = []
        if cell.x < self.grid_width - 1:
            cells.append(self.get_cell(cell.x + 1, cell.y))
        else:
            cells.append(self.get_cell(0, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y - 1))
        else:
            cells.append(self.get_cell(cell.x, self.grid_height - 1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x - 1, cell.y))
        else:
            cells.append(self.get_cell(self.grid_width - 1, cell.y))
        if cell.y < self.grid_height - 1:
            cells.append(self.get_cell(cell.x, cell.y + 1))
        else:
            cells.append(self.get_cell(cell.x, 0))
        return cells

    def display_path(self):
        cell = self.end
        self.path_to_food = []
        self.path_curr = [cell.x, cell.y]
        while cell.parent is not self.start:
            cell = cell.parent
            if cell.x < self.path_curr[0]:
                self.path_to_food.append(0)
            elif cell.x > self.path_curr[0]:
                self.path_to_food.append(2)
            else:
                if cell.y < self.path_curr[1]:
                    self.path_to_food.append(1)
                else:
                    self.path_to_food.append(3)
            self.path_curr=[cell.x,cell.y]
        if self.start.x < self.path_curr[0]:
            self.path_to_food.append(0)
        elif self.start.x > self.path_curr[0]:
            self.path_to_food.append(2)
        else:
            if self.start.y < self.path_curr[1]:
                self.path_to_food.append(1)
            else:
                self.path_to_food.append(3)

    def update_cell(self, adj, cell):
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def process(self, start_place):
        self.start = self.get_cell(start_place%self.grid_width, start_place//self.grid_height)
        self.opened = []
        self.closed = set()
        heapq.heappush(self.opened, (self.start.f, self.start))
        while len(self.opened):
            f, cell = heapq.heappop(self.opened)
            self.closed.add(cell)
            if cell is self.end:
                self.display_path()
                break
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closed:
                    if (adj_cell.f, adj_cell) in self.opened:
                        if adj_cell.g > cell.g + 10:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        heapq.heappush(self.opened, (adj_cell.f, adj_cell))
        return self.path_to_food


class Snake(tk.Frame):
    def __init__(self, parent):
        with open(os.path.join(os.getcwd(), "levels_info.txt"),"r") as f:
            self.level_info=f.readlines()
        self.level_info=np.array(self.level_info)
        with open(os.path.join(os.getcwd(), "level.txt"),"r") as f:
            self.max_level=f.readlines()
        self.max_level=int(self.max_level[0])
        self.level_cap=int(self.level_info[-1].split("\t")[-1].split("\n")[0])
        self.current_level=1
        self.current_mode=0
        self.snake_colors=["green", "blue", "orange", "black"]
        tk.Frame.__init__(self, parent, width=430, height=545)
        parent.bind('<Left>', self.leftkey)
        parent.bind('<Right>', self.rightkey)
        parent.bind('<Up>', self.upkey)
        parent.bind('<Down>', self.downkey)
        parent.bind('<a>', self.akey)
        parent.bind('<d>', self.dkey)
        parent.bind('<w>', self.wkey)
        parent.bind('<s>', self.skey)
        parent.bind('<f>', self.fkey)
        parent.bind('<h>', self.hkey)
        parent.bind('<t>', self.tkey)
        parent.bind('<g>', self.gkey)
        parent.bind('<j>', self.jkey)
        parent.bind('<l>', self.lkey)
        parent.bind('<i>', self.ikey)
        parent.bind('<k>', self.kkey)
        # Start
        self.Label_Start = tk.Label(self, text="Speed:(20-1)", anchor="w")
        self.submit_Start = tk.Button(self, text="Start", command = self.start_free_mode)
        self.entry_Start = tk.Entry(self)
        self.output_Start = tk.Label(self, text="", anchor="w")
        # Start Layout 
        self.Label_Start.pack(side="left")
        self.output_Start.pack(side="right")
        self.entry_Start.pack(side="left", padx=20)
        self.submit_Start.pack(side="right")
        # Start Place
        self.Label_Start.place(y=5,x=5,height=30, width=120)
        self.entry_Start.place(y=5,x=125,height=30, width=50)
        self.submit_Start.place(y=5,x=175,height=30, width=50)
        self.output_Start.place(y=65,x=175,height=30, width=100)
        # Select Player
        self.Label_SP = tk.Label(self, text="Player:(0-4)", anchor="w")
        self.entry_SP = tk.Entry(self)
        # Select Player Layout 
        self.Label_SP.pack(side="left")
        self.entry_SP.pack(side="left", padx=20)
        # Select Player Place
        self.Label_SP.place(y=35,x=5,height=30, width=120)
        self.entry_SP.place(y=35,x=125,height=30, width=50)
        # Select PC difficulty
        self.Label_diff = tk.Label(self, text="PC lvl:(0-2)", anchor="w")
        self.entry_diff = tk.Entry(self)
        # Select PC difficulty layout
        self.Label_diff.pack(side="left")
        self.entry_diff.pack(side="left", padx=20)
        # Select PC difficulty place
        self.Label_diff.place(y=65,x=5,height=30, width=120)
        self.entry_diff.place(y=65,x=125,height=30, width=50)
        # Random Wall
        self.Label_random_wall = tk.Label(self, text="R-Wall:(0-20)", anchor="w")
        self.entry_random_wall = tk.Entry(self)
        # Random Wall Layout 
        self.Label_random_wall.pack(side="left")
        self.entry_random_wall.pack(side="left", padx=20)
        # Random Wall Place
        self.Label_random_wall.place(y=35,x=175,height=30, width=100)
        self.entry_random_wall.place(y=35,x=275,height=30, width=50)
        # Stop
        self.submit_Stop = tk.Button(self, text="Stop", command = self.stop_game)
        self.submit_Stop.pack(side="right")
        self.submit_Stop.place(y=95,x=5,height=30, width=100)
        # Continue
        self.submit_Continue = tk.Button(self, text="Continue", command = self.continue_game)
        self.submit_Continue.pack(side="right")
        self.submit_Continue.place(y=95,x=105,height=30, width=100)
        # Mode Change
        self.mode_button = tk.Button(self, text="Free Mode", command = self.change_mode)
        self.mode_button.pack(side="right")
        self.mode_button.place(y=35,x=325,height=30, width=100)
        # Level Selection
        var = tk.DoubleVar(value=1)
        self.level_select=tk.Spinbox(self,from_=0,to=self.max_level,textvariable=var)
        self.level_select.pack(side="right")
        self.level_select.place(y=65,x=325,height=30, width=100)
        self.level_select['state'] = 'disabled'
        # Score P1
        self.Score_Label_p1 = tk.Label(self, text="P1: 0", anchor="w")
        self.Score_Label_p1.pack(side="left")
        self.Score_Label_p1.place(y=5,x=225,height=30, width=50)
        # Score P2
        self.Score_Label_p2 = tk.Label(self, text="P2: 0", anchor="w")
        self.Score_Label_p2.pack(side="left")
        self.Score_Label_p2.place(y=5,x=275,height=30, width=50)
        # Score P3
        self.Score_Label_p3 = tk.Label(self, text="P3: 0", anchor="w")
        self.Score_Label_p3.pack(side="left")
        self.Score_Label_p3.place(y=5,x=325,height=30, width=50)
        # Score P4
        self.Score_Label_p4 = tk.Label(self, text="P4: 0", anchor="w")
        self.Score_Label_p4.pack(side="left")
        self.Score_Label_p4.place(y=5,x=375,height=30, width=50)
        #-----------------------#
        self.npc_level=0
        self.rwall=0
        self.random_wall=[]
        self.old_random_wall=[]
        self.wall_iter=0
        self.player_count=0
        self.game_over = [0, 0, 0, 0]
        self.start_test=1
        self.score = [0, 0, 0, 0]
        self.grown = [0, 0, 0, 0]
        self.started=0
        self.stopped=0
        self.points_needed = 0
        self.n=40
        self.dest=0
        self.field_places=[]
        self.directions = [0, 2, 1, 3]
        self.snakes = [[self.n+1, self.n+2], [self.n**2-self.n-2, self.n**2-self.n-3], [self.n*2-2, self.n*3-2], [self.n**2-self.n*2+1, self.n**2-self.n*3+1]]
        self.food=2*self.n+1
        self.parent=parent
        self.targets_path = []

    def update_level_selection(self):
        if self.current_level==self.max_level and self.max_level!=self.level_cap:
            self.max_level+=1
            self.level_select.config(to=self.max_level)
            with open(os.path.join(os.getcwd(), "level.txt"),"w") as f:
                f.write(str(self.max_level))
        
    def change_mode(self):
        if self.current_mode==0:
            self.entry_Start['state'] = 'disabled'
            self.entry_SP['state'] = 'disabled'
            self.entry_random_wall['state'] = 'disabled'
            self.entry_diff['state'] = 'disabled'
            self.level_select['state'] = 'readonly'
            self.submit_Start.configure(command=self.start_level_mode)
            self.mode_button.configure(text="Level Mode")
            self.current_mode=1
        else:
            self.entry_Start['state'] = 'normal'
            self.entry_SP['state'] = 'normal'
            self.entry_random_wall['state'] = 'normal'
            self.entry_diff['state'] = 'normal'
            self.level_select['state'] = 'disabled'
            self.submit_Start.configure(command=self.start_free_mode)
            self.mode_button.configure(text="Free Mode")
            self.current_mode=0
        
    def stop_game(self):
        if self.current_mode==0:
            self.entry_Start['state'] = 'normal'
            self.entry_SP['state'] = 'normal'
            self.entry_random_wall['state'] = 'normal'
            self.entry_diff['state'] = 'normal'
        self.stopped=1
        
    def leftkey(self,event):
        if self.player_count!=0 and self.directions[0] != 0:
            self.directions[0]=2
        
    def rightkey(self,event):
        if self.player_count!=0 and self.directions[0] != 2:
            self.directions[0]=0
        
    def upkey(self,event):
        if self.player_count!=0 and self.directions[0] != 1:
            self.directions[0]=3
        
    def downkey(self,event):
        if self.player_count!=0 and self.directions[0] != 3:
            self.directions[0]=1
        
    def akey(self,event):
        if self.player_count>=2 and self.directions[1] != 0:
            self.directions[1]=2
        
    def dkey(self,event):
        if self.player_count>=2 and self.directions[1] != 2:
            self.directions[1]=0
        
    def wkey(self,event):
        if self.player_count>=2 and self.directions[1] != 1:
            self.directions[1]=3
        
    def skey(self,event):
        if self.player_count>=2 and self.directions[1] != 3:
            self.directions[1]=1
            
    def gkey(self,event):
        if self.player_count>=3 and self.directions[2] != 3:
            self.directions[2]=1
        
    def fkey(self,event):
        if self.player_count>=3 and self.directions[2] != 0:
            self.directions[2]=2
        
    def tkey(self,event):
        if self.player_count>=3 and self.directions[2] != 1:
            self.directions[2]=3
        
    def hkey(self,event):
        if self.player_count>=3 and self.directions[2] != 2:
            self.directions[2]=0
            
    def jkey(self,event):
        if self.player_count>=4 and self.directions[3] != 0:
            self.directions[3]=2
        
    def lkey(self,event):
        if self.player_count>=4 and self.directions[3] != 2:
            self.directions[3]=0
        
    def ikey(self,event):
        if self.player_count>=4 and self.directions[3] != 1:
            self.directions[3]=3
        
    def kkey(self,event):
        if self.player_count>=4 and self.directions[3] != 3:
            self.directions[3]=1
        
    def win(self):
        self.game_over = [1, 1, 1, 1]
        self.stop_game()
        self.output_Start.configure(text="Game Over")
        if self.current_level==self.max_level and self.max_level!=self.level_cap:
            highlighted=[525,527,529,530,531,533,535,540,544,546,547,548,550,554,565,567,569,571,573,575,580,584,586,588,590,591,594,606,609,611,613,615,620,622,624,626,628,630,632,634,646,649,651,653,655,660,662,664,666,668,670,673,674,686,689,690,691,693,694,695,701,703,706,707,708,710,714,889,893,895,896,897,899,903,908,910,914,916,924,929,930,933,935,939,943,948,951,953,956,963,964,965,969,971,973,975,976,979,983,988,991,993,996,1004,1009,1012,1013,1015,1019,1021,1023,1028,1032,1036,1049,1053,1055,1056,1057,1060,1062,1068,1072,1076]
        else:
            highlighted=[525,527,529,530,531,533,535,540,544,546,547,548,550,554,565,567,569,571,573,575,580,584,586,588,590,591,594,606,609,611,613,615,620,622,624,626,628,630,632,634,646,649,651,653,655,660,662,664,666,668,670,673,674,686,689,690,691,693,694,695,701,703,706,707,708,710,714]
        for i in highlighted:
            self.field_places[i].configure(bg="yellow")
        self.update_level_selection()
        
    def loose(self):
        self.game_over = [1, 1, 1, 1]
        self.stop_game()
        self.output_Start.configure(text="Game Over")
        highlighted=[525,527,529,530,531,533,535,540,544,545,546,548,549,550,552,553,554,565,567,569,571,573,575,580,584,586,588,593,606,609,611,613,615,620,624,626,628,629,630,633,646,649,651,653,655,660,664,666,670,673,686,689,690,691,693,694,695,700,701,702,704,705,706,708,709,710,713]
        for i in highlighted:
            self.field_places[i].configure(bg="yellow")
        
    def continue_game(self):
        if self.started==1 and self.stopped==1 and np.sum(self.game_over)!=4:
            self.entry_Start['state'] = 'disabled'
            self.entry_SP['state'] = 'disabled'
            self.entry_random_wall['state'] = 'disabled'
            self.entry_diff['state'] = 'disabled'
            self.stopped=0
            self.start_moving()
            
    def start_level_mode(self):
        if self.started==0 or self.stopped==1:
            gc.collect()
            try:
                self.output_Start.configure(text="")
                self.current_level=int(self.level_select.get())
                if self.current_level==0:
                    self.current_level=1
                self.player_count=1
                self.text_pos=np.where(self.level_info=="Level:\t%d\n"%(self.current_level))[0][0]
                self.npc_level=int(self.level_info[self.text_pos+1].split("\t")[-1].split("\n")[0])
                self.points_needed=int(self.level_info[self.text_pos+2].split("\t")[-1].split("\n")[0])
                self.difficulty=int(self.level_info[self.text_pos+3].split("\t")[-1].split("\n")[0])
                self.rwall=int(self.level_info[self.text_pos+4].split("\t")[-1].split("\n")[0])
                self.wall_places=self.level_info[self.text_pos+5].split("\t")[-1].split("\n")[0].split(",")
                if (self.difficulty<1 or self.difficulty>20) or (self.rwall<0 or self.rwall>20) or (self.player_count<0 or self.player_count>4):
                    self.start_test=1
                    self.dest=0
                    self.fail()
                else:
                    self.start_test=0
                if self.start_test==0:
                    self.old_random_wall=[]
                    self.random_wall=[]
                    self.wall_iter=0
                    self.game_over = [0, 0, 0, 0]
                    self.score = [0, 0, 0, 0]
                    self.grown = [0, 0, 0, 0]
                    self.create_field_levels()
                    self.create_visual_field()
                    self.dest=1
                    self.directions = [0, 2, 1, 3]
                    self.started=1
                    self.stopped=0
                    self.snakes = [[self.n+1, self.n+2], [self.n**2-self.n-2, self.n**2-self.n-3], [self.n*2-2, self.n*3-2], [self.n**2-self.n*2+1, self.n**2-self.n*3+1]]
                    self.Score_Label_p1.configure(text="P1: 0")
                    self.Score_Label_p2.configure(text="P2: 0")
                    self.Score_Label_p3.configure(text="P3: 0")
                    self.Score_Label_p4.configure(text="P4: 0")
                    self.place_food()
                    self.occupied_space = self.field!=0
                    self.no_food_space = self.field!=1
                    self.occupied = np.where(self.occupied_space * self.no_food_space)
                    self.occupied = np.array([self.occupied[1],self.occupied[0]]).transpose()
                    self.occupied = [(item[0],item[1]) for item in self.occupied]
                    self.start_place = self.snakes[3][-1]
                    self.snake_places = np.where(self.field>2)
                    self.Target_Movement = AStar(self.occupied, self.snake_places, self.start_place, self.food, grid_height=self.n, grid_width=self.n)
                    self.Target_Movement.init_grid()
                    self.start_moving()
            except ValueError:
                self.dest=0
                self.fail()
    
    def start_free_mode(self):
        if self.started==0 or self.stopped==1:
            gc.collect()
            try:
                self.output_Start.configure(text="")
                self.difficulty=int(self.entry_Start.get())
                self.rwall=int(self.entry_random_wall.get())
                self.player_count=int(self.entry_SP.get())
                self.npc_level=int(self.entry_diff.get())
                if (self.difficulty<1 or self.difficulty>20) or (self.rwall<0 or self.rwall>20) or (self.player_count<0 or self.player_count>4) or (self.npc_level<0 or self.npc_level>2):
                    self.start_test=1
                    self.dest=0
                    self.fail()
                else:
                    self.start_test=0
                if (self.start_test==0):
                    self.old_random_wall=[]
                    self.random_wall=[]
                    self.wall_iter=0
                    self.entry_Start['state'] = 'disabled'
                    self.entry_SP['state'] = 'disabled'
                    self.entry_random_wall['state'] = 'disabled'
                    self.entry_diff['state'] = 'disabled'
                    self.game_over = [0, 0, 0, 0]
                    self.score = [0, 0, 0, 0]
                    self.grown = [0, 0, 0, 0]
                    self.create_field()
                    self.create_visual_field()
                    self.dest=1
                    self.directions = [0, 2, 1, 3]
                    self.started=1
                    self.stopped=0
                    self.snakes = [[self.n+1, self.n+2], [self.n**2-self.n-2, self.n**2-self.n-3], [self.n*2-2, self.n*3-2], [self.n**2-self.n*2+1, self.n**2-self.n*3+1]]
                    self.Score_Label_p1.configure(text="P1: 0")
                    self.Score_Label_p2.configure(text="P2: 0")
                    self.Score_Label_p3.configure(text="P3: 0")
                    self.Score_Label_p4.configure(text="P4: 0")
                    self.place_food()
                    self.occupied_space = self.field!=0
                    self.no_food_space = self.field!=1
                    self.occupied = np.where(self.occupied_space * self.no_food_space)
                    self.occupied = np.array([self.occupied[1],self.occupied[0]]).transpose()
                    self.occupied = [(item[0],item[1]) for item in self.occupied]
                    self.start_place = self.snakes[3][-1]
                    self.snake_places = np.where(self.field>2)
                    self.Target_Movement = AStar(self.occupied, self.snake_places, self.start_place, self.food, grid_height=self.n, grid_width=self.n)
                    self.Target_Movement.init_grid()
                    self.targets_path = []
                    self.start_moving()
            except ValueError:
                self.dest=0
                self.fail()
            
    def place_food(self):
        if self.rwall!=0:
            if self.wall_iter==0:
                self.random_wall=random.sample(range(self.n+1,(self.n**2)-self.n-2),self.rwall)
                while not all(self.field[x//self.n,x%self.n]==0 for x in self.random_wall):
                    self.random_wall=random.sample(range(self.n+1,(self.n**2)-self.n-2),self.rwall)
                for x in self.random_wall:
                    self.field[x//self.n,x%self.n]=0
                    self.field_places[x].configure(bg="cyan")
                if len(self.old_random_wall)!=0:
                    for x in self.old_random_wall:
                        self.field[x//self.n,x%self.n]=0
                        self.field_places[x].configure(bg="white")
                self.wall_iter=1
            else:
                for x in self.random_wall:
                    self.field[x//self.n,x%self.n]=2
                    self.field_places[x].configure(bg="grey40")
                self.old_random_wall=copy.deepcopy(self.random_wall)
                self.wall_iter=0
        self.food=random.randint(self.n+1,(self.n**2)-self.n-2)
        while self.field[self.food//self.n,self.food%self.n]!=0:
            self.food=random.randint(self.n+1,(self.n**2)-self.n-2)
        self.field[self.food//self.n,self.food%self.n]=1
        self.field_places[self.food].configure(bg="red")
        if self.npc_level == 2:
            try:
                self.update_Astart()
            except:
                pass
        
    def update_Astart(self):
        self.snake_places = np.where(self.field>2)
        self.Target_Movement.update_cells_and_pos(self.snake_places, self.food)
        self.targets_path = []
            
    def update_scores(self):
        self.Score_Label_p1.configure(text="P1: %d"%(self.score[0]))
        self.Score_Label_p2.configure(text="P2: %d"%(self.score[1]))
        self.Score_Label_p3.configure(text="P3: %d"%(self.score[2]))
        self.Score_Label_p4.configure(text="P4: %d"%(self.score[3]))
        
    def start_moving(self):
        if self.stopped==0:
            self.grown = [0, 0, 0, 0]
            if np.sum(self.score)>500:
                self.game_over = [1, 1, 1, 1]
                self.stop_game()
                self.output_Start.configure(text="Game Over")
            for snake in range(4):
                if self.game_over[snake]==0:
                    if self.player_count <= snake:
                        if self.npc_level==0:
                            self.directions[snake]=self.random_direction(self.snakes[snake], self.directions[snake])
                        else:
                            if self.npc_level==2 and snake==3:
                                self.directions[snake], self.targets_path=self.target_aimed_direction(self.snakes[snake], self.directions[snake], self.targets_path)
                            else:
                                self.directions[snake]=self.less_random_direction(self.snakes[snake], self.directions[snake])
                    if self.field[(self.snakes[snake][-1]//self.n + (self.directions[snake]%2) - 2*(self.directions[snake]//2)*(self.directions[snake]%2))%self.n,(self.snakes[snake][-1]%self.n + ((self.directions[snake]+1)%2) - 2*(self.directions[snake]//2)*((self.directions[snake]+1)%2))%self.n]>1:
                        self.game_over[snake]=1
                        if np.sum(self.game_over==4):
                            self.stop_game()
                        self.output_Start.configure(text="Game Over")
                    elif self.field[(self.snakes[snake][-1]//self.n + (self.directions[snake]%2) - 2*(self.directions[snake]//2)*(self.directions[snake]%2))%self.n,(self.snakes[snake][-1]%self.n + ((self.directions[snake]+1)%2) - 2*(self.directions[snake]//2)*((self.directions[snake]+1)%2))%self.n]==1:
                        self.score[snake]+=1
                        self.update_scores()
                        self.grown[snake]=1
                        self.place_food()
                    if (self.snakes[snake][-1]%self.n) * ((self.directions[snake]+1)%2) + (self.snakes[snake][-1]//self.n) * (self.directions[snake]%2) != (self.n-1) * (np.abs(self.directions[snake] - 3)//2):
                        self.snakes[snake].append(self.snakes[snake][-1] + ((self.directions[snake]+1)%2 + self.n*(self.directions[snake]%2)) * (-2*(self.directions[snake]//2)+1))
                    else:
                        self.snakes[snake].append((self.snakes[snake][-1] + (((self.directions[snake]+1)%2) * (self.n-1) + (self.directions[snake]%2)*self.n) * (2*(((self.directions[snake]+1)//2)%2)-1))%(self.n**2))
                    self.field[self.snakes[snake][-1]//self.n,self.snakes[snake][-1]%self.n]=snake + 3
                    self.field_places[self.snakes[snake][-1]].configure(bg=self.snake_colors[snake])
                    if self.grown[snake]==0:
                        self.field_places[self.snakes[snake][0]].configure(bg="white")
                        self.field[self.snakes[snake][0]//self.n,self.snakes[snake][0]%self.n]=0
                        del self.snakes[snake][0]
            if self.current_mode==1:
                if self.game_over[0]==1:
                    self.loose()
                if self.score[1]>=self.points_needed or self.score[2]>=self.points_needed or self.score[3]>=self.points_needed:
                    self.loose()
                if self.score[0]>=self.points_needed:
                    self.win()
            self.parent.after(self.difficulty*10,self.start_moving)
  
    def less_random_direction(self, snake_places, direction):
        if direction==0:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                direction=0
            else:
                if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]>1:
                    direction=1
                elif self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]>1:
                    direction=3
                else:
                    direction=random.choice([1,3])
        elif direction==1:
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                direction=1
            else:
                if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]>1:
                    direction=0
                elif self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]>1:
                    direction=2
                else:
                    direction=random.choice([0,2])
        elif direction==2:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                direction=2
            else:
                if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]>1:
                    direction=1
                elif self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]>1:
                    direction=3
                else:
                    direction=random.choice([1,3])
        elif direction==3:
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                direction=3
            else:
                if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]>1:
                    direction=0
                elif self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]>1:
                    direction=2
                else:
                    direction=random.choice([0,2])
        if snake_places[-1]%self.n==self.food%self.n:
            if self.food>=snake_places[-1]:
                if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                    direction=1
            else:
                if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                    direction=3
        elif snake_places[-1]//self.n==self.food//self.n:
            if self.food>=snake_places[-1]:
                if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                    direction=0
            else:
                if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                    direction=2
        return direction
                    
    def target_aimed_direction(self, snake_places, direction, target_path):
        calculate_new_target_path = 0
        allowed_moves = []
        if direction==0:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        elif direction==1:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
        elif direction==2:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        elif direction==3:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        if len(target_path) != 0:
            if target_path[-1] in allowed_moves:
                direction=target_path[-1]
                del target_path[-1]
            else:
                calculate_new_target_path = 1
                target_path = []
        else:
            calculate_new_target_path = 1
            target_path = []
        if calculate_new_target_path == 1:
            self.update_Astart()
            start_place = snake_places[-1]
            target_path = self.Target_Movement.process(start_place)
            if len(target_path)!=0 and target_path[-1] in allowed_moves:
                direction=target_path[-1]
                del target_path[-1]
            else:
                try:
                    direction=random.choice(allowed_moves)
                except:
                    direction=0
        return direction, target_path

    def random_direction(self, snake_places, direction):
        allowed_moves=[]
        if direction==0:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        elif direction==1:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
        elif direction==2:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
            if self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(1)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        elif direction==3:
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]<2:
                allowed_moves.append(0)
            if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]<2:
                allowed_moves.append(2)
            if self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]<2:
                allowed_moves.append(3)
        if self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]==1 or (self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+1)%self.n]==0 and self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n+2)%self.n]==1):
            direction=0
        elif self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]==1 or (self.field[(snake_places[-1]//self.n+1)%self.n,snake_places[-1]%self.n]==0 and self.field[(snake_places[-1]//self.n+2)%self.n,snake_places[-1]%self.n]==1):
            direction=1
        elif self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]==1 or (self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-1)%self.n]==0 and self.field[snake_places[-1]//self.n,(snake_places[-1]%self.n-2)%self.n]==1):
            direction=2
        elif self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]==1 or (self.field[(snake_places[-1]//self.n-1)%self.n,snake_places[-1]%self.n]==0 and self.field[(snake_places[-1]//self.n-2)%self.n,snake_places[-1]%self.n]==1):
            direction=3
        else:
            if len(allowed_moves)!=0:
                direction=random.choice(allowed_moves)
        return direction
                
    def create_field_levels(self):
        self.field = np.zeros((self.n,self.n))
        self.field[1,1]=3
        self.field[1,2]=3
        self.field[self.n-2,self.n-2]=4
        self.field[self.n-2,self.n-3]=4
        self.field[1,self.n-2]=5
        self.field[2,self.n-2]=5
        self.field[self.n-2,1]=6
        self.field[self.n-3,1]=6
        if int(self.wall_places[0])!=-1:
            for i in self.wall_places:
                pos=int(i)
                self.field[pos//self.n,pos%self.n]=2
                
    def create_field(self):
        self.field = np.zeros((self.n,self.n))
        self.field[1,1]=3
        self.field[1,2]=3
        self.field[self.n-2,self.n-2]=4
        self.field[self.n-2,self.n-3]=4
        self.field[1,self.n-2]=5
        self.field[2,self.n-2]=5
        self.field[self.n-2,1]=6
        self.field[self.n-3,1]=6
        self.field[:,0]=2
        self.field[0,:]=2
        self.field[self.n-1,:]=2
        self.field[:,self.n-1]=2
        
    def create_visual_field(self):
        self.field=np.array(self.field)
        if self.dest==0:
            self.field_places=[]
            for i,n in enumerate([x for sublist in self.field for x in sublist]):
                self.field_places.append(tk.Label(self))
                self.field_places[i].pack(side="left", padx=20)
                self.field_places[i].place(y=140+(i//self.n)*10,x=15+(i%self.n)*10,height=10, width=10)
                if n==2:
                    self.field_places[i].configure(bg="grey40")
                elif n==4:
                    self.field_places[i].configure(bg=self.snake_colors[0])
                elif n==4:
                    self.field_places[i].configure(bg=self.snake_colors[1])
                elif n==5:
                    self.field_places[i].configure(bg=self.snake_colors[2])
                elif n==6:
                    self.field_places[i].configure(bg=self.snake_colors[3])
                else:
                    self.field_places[i].configure(bg="white")
        else:
            for i,n in enumerate([x for sublist in self.field for x in sublist]):
                if n==2:
                    self.field_places[i].configure(bg="grey40")
                elif n==3:
                    self.field_places[i].configure(bg=self.snake_colors[0])
                elif n==4:
                    self.field_places[i].configure(bg=self.snake_colors[0])
                elif n==5:
                    self.field_places[i].configure(bg=self.snake_colors[0])
                elif n==6:
                    self.field_places[i].configure(bg=self.snake_colors[0])
                else:
                    self.field_places[i].configure(bg="white")
                
    def fail(self):
        self.output_Start.configure(text="Check inputs")


if __name__ == "__main__":
    root = tk.Tk()
    app=Snake(parent=root)
    app.pack(fill="both", expand=True)
    root.mainloop()
