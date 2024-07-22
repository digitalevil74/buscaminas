"""
BuscaMinas 2024
"""
import sys
import pandas as pd
import numpy as np
import random
# Kivy
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.clock import Clock

# Set the window size
Window.size = (800, 558)
Window.minimum_width = 800
Window.minimum_height = 558
Window.resizable = False

class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)
        main_layout=BoxLayout(orientation='vertical')
        hor_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)

        #label = Label(text='Select Difficulty')
        #layout.add_widget(self.label)

        game_logo = Image(source='bm.webp')

        self.add_widget(main_layout)
        main_layout.add_widget(hor_layout)

        button_text = {0: 'Facil 8x8', 1: 'Medio 16x16', 2: 'Dificil 24x24', 3: 'Brigido 30x24'}
        for i in range(4):
            self.dif_button = Button(text=button_text[i], size_hint=(None, None), size=(200, 100))
            self.dif_button.bind(on_press=lambda x, i=i: self.select_difficulty(i))
            hor_layout.add_widget(self.dif_button)

        main_layout.add_widget(game_logo)



    def select_difficulty(self, difficulty):
        self.manager.get_screen('game').start_game(difficulty)
        self.manager.current = 'game'


class GameScreen(Screen):
    def __init__(self, **kwargs):
        super(GameScreen, self).__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical')
        self.top_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        self.bombs_layout = GridLayout()
        self.label1 = Label(text=f'Minas restantes:{remaining_mines}')
        label2 = Label(text='Bombas:')
        label3 = Label(text='Tiempo:')
        self.add_widget(self.main_layout)
        self.main_layout.add_widget(self.top_info)
        self.top_info.add_widget(self.label1)
        self.top_info.add_widget(label2)
        self.top_info.add_widget(label3)
        self.main_layout.add_widget(self.bombs_layout)
        self.buttons = {}  # Dictionary to store buttons

    def on_pre_enter(self):
        self.update_mines()

    def update_mines(self):
        self.label1.text = f'Minas restantes: {remaining_mines}'

    def start_game(self, dif):

        if dif == 0:
            self.x, self.y = (8, 8)
        elif dif == 1:
            self.x, self.y = (16, 16)
        elif dif == 2:
            self.x, self.y = (24, 24)
        elif dif == 3:
            self.x, self.y = (30, 24)
        Window.size = (32*self.x, 32*self.y + self.top_info.height)
        Window.resizable = False
        Window.minimum_width = 32*self.x
        Window.minimum_height = 32*self.y + self.top_info.height
        reset_board(self.x, self.y, dif)
        self.bombs_layout.cols = self.x
        self.create_grid(dif)

    def create_grid(self, dif):
        # grid populates lr-tb
        for i in range(self.y):
            for j in range(self.x):
                button = MinesweeperButton(grid_pos=(j, i), game_screen=self, text='', size_hint=(None, None), size=(32, 32))
                self.buttons[(j, i)] = button
                self.bombs_layout.add_widget(button)


class MinesweeperButton(Button):
    def __init__(self, grid_pos, game_screen, **kwargs):
        super(MinesweeperButton, self).__init__(**kwargs)
        self.grid_pos = grid_pos
        # self.background_normal = "bomb.png"
        # self.bind(on_press=self.on_button_press)
        self.long_press_time = 0.5  # Time in seconds to detect a long press
        self.long_press_event = None
        self.game_screen = game_screen
        self.font_name = 'Roboto-Bold'
        self.long_press_detected = False
        # self.bind(on_touch_down=self.on_touch_down)
        # self.bind(on_touch_up=self.on_touch_up)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Start a timer to detect long press
            self.long_press_event = Clock.schedule_once(self.trigger_long_press, self.long_press_time)
            self.long_press_detected = False  # Reset long press flag
            return True
        return super(MinesweeperButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.long_press_event:
                # Cancel the long press event if the touch is released before the timer ends
                self.long_press_event.cancel()
                self.long_press_event = None
                # Handle short press here
                if not self.long_press_detected:
                    self.handle_short_press()
            return True
        return super(MinesweeperButton, self).on_touch_up(touch)

    def trigger_long_press(self, dt):
        # Handle long press here
        self.long_press_detected = True
        self.handle_long_press()

    def handle_short_press(self):
        # Implement your short press logic here
        print(f"Button at {self.grid_pos} short pressed")
        # Example logic for Minesweeper
        if board[self.grid_pos] == 9:
            self.background_normal = "bomb.png"
            loose()
        elif board[self.grid_pos] == 0:
            self.uncover_neighbors(*self.grid_pos, set())
        else:
            self.text = str(board[self.grid_pos])
            self.background_color = "#000000"
            self.set_color()

    def handle_long_press(self):
        global remaining_mines
        # Implement your long press logic here
        print(f"Button at {self.grid_pos} long pressed")
        # Example logic for Minesweeper (e.g., flagging a mine)
        if self.background_normal == 'atlas://data/images/defaulttheme/button':
            self.background_normal = 'flag.png'  # Example flag image
            remaining_mines -= 1
        elif self.background_normal == 'flag.png':
            self.background_normal = 'question.png'
            remaining_mines += 1
        elif self.background_normal == 'question.png':
            self.background_normal = 'atlas://data/images/defaulttheme/button'


        self.game_screen.update_mines()


    def uncover_neighbors(self, x, y, processed):
        if (x, y) in processed:
            return
        processed.add((x, y))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0:
                    self.game_screen.buttons[x + dx, y + dy].text = ''
                    self.game_screen.buttons[x + dx, y + dy].background_color = "#000000"
                else:
                    if 0 <= x + dx <= x_board and 0 <= y + dy <= y_board and self.game_screen.buttons[x + dx, y + dy].background_color != "#000000":
                        if board[(x + dx, y + dy)] == 0 and self.game_screen.buttons[x + dx, y + dy].background_color != "#000000":
                            self.uncover_neighbors(x + dx, y + dy, processed)
                        else:
                            self.game_screen.buttons[x + dx, y + dy].text = str(board[x + dx, y + dy])
                            self.game_screen.buttons[x + dx, y + dy].background_color = "#000000"
                            self.game_screen.buttons[x + dx, y + dy].set_color()


    def set_color(self):
        self.color = {
                    1: [0, 0, 1, 1],  # Blue
                    2: [0, 0.5, 0, 1],  # Green
                    3: [1, 0, 0, 1],  # Red
                    4: [0, 0, 0.5, 1],  # Dark Blue
                    5: [0.5, 0, 0, 1],  # Maroon
                    6: [0, 1, 1, 1],  # Turquoise
                    7: [0, 0, 0, 1],  # Black
                    8: [0.5, 0.5, 0.5, 1]  # Gray
                }.get(board[self.grid_pos])


class BuscaMinas(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(GameScreen(name='game'))
        return sm


def reset_board(x, y, diff):
    global board, x_board, y_board, remaining_mines
    x_board = x - 1
    y_board = y - 1
    board = np.zeros((x, y), dtype=int)
    if diff <= 1:
        mines = round(x * y * 0.1)
    elif diff == 2:
        mines = round(x * y * 0.2)
    elif diff >= 3:
        mines = round(x * y * 0.25)
    grid_size = np.arange(x * y)
    rand_mines = np.random.choice(grid_size, mines, replace=False)
    print(rand_mines)
    bomb_positions = [(pos // y, pos % y) for pos in rand_mines]
    print(bomb_positions)
    for pos in bomb_positions:
        board[pos] = 9
    for i in range(x):
        for j in range(y):
            if board[i, j] != 9:
                board[i, j] = find_neighbor(i, j)
    remaining_mines = mines
    print(board)
    print(f'mines: {remaining_mines}')


def find_neighbor(x, y):
    bombs = 0
    # Parte central
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == dy == 0:
                continue
            else:
                if 0 <= x + dx <= x_board and 0 <= y + dy <= y_board:
                    if board[(x + dx, y + dy)] == 9:
                        bombs += 1
    return bombs




def loose():
    print('KABOOM!!! has perdido!')


remaining_mines = 0
if __name__ == "__main__":
    BuscaMinas().run()
