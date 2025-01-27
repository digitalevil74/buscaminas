"""
BuscaMinas 2024

@author(s): Felipe Gaete R.
@year(s): 2024-
@First version: 0.7
@Current version: 0.7
@Pylint grading: TBA
@Usage: python main.py
@Licence: GPL 3.0

Update log

- 24.7.24 -FGa - First version
"""

from datetime import datetime
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
from kivy.uix.popup import Popup
from kivy.clock import Clock


class IntroScreen(Screen):
    def __init__(self, **kwargs):
        super(IntroScreen, self).__init__(**kwargs)
        main_layout = BoxLayout(orientation='vertical')
        hor_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        game_logo = Image(source='img/bm.webp')
        self.add_widget(main_layout)
        main_layout.add_widget(hor_layout)
        button_text = {0: 'Facil 8x8', 1: 'Medio 16x16', 2: 'Dificil 24x24', 3: 'Brigido 30x24'}
        for i in range(4):
            self.dif_button = Button(text=button_text[i], size_hint=(None, None), size=(200, 100), font_name='Gabriola', font_size=42)
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
        self.label1 = Label(text=str(remaining_mines), font_name='Gabriola', font_size=36, color=[1, 0, 0, 1])
        self.uncovered = Label(text=f'Despejado: 0', font_name='Gabriola', font_size=36)
        self.time_label = Label(text='Tiempo: 00:00', font_name='Gabriola', font_size=36)
        self.add_widget(self.main_layout)
        self.main_layout.add_widget(self.top_info)
        self.top_info.add_widget(self.label1)
        self.top_info.add_widget(self.uncovered)
        self.top_info.add_widget(self.time_label)
        self.main_layout.add_widget(self.bombs_layout)
        self.buttons = {}  # Dictionary to store buttons
        self.x_board, self.y_board = (0,0)
        self.first_move = True
        self.elapsed = 0

    def on_pre_enter(self):
        self.update_mines()

    def update_mines(self):
        self.label1.text = str(remaining_mines)

    def update_time(self, *args):
        global start_time
        new_time = datetime.now()
        elapsed = new_time - start_time
        minutos, segundos = divmod(elapsed.total_seconds(), 60)
        if segundos < 10:
            segundos = str('0' + str(int(segundos)))
        else:
            segundos = int(segundos)
        if minutos < 10:
            minutos = str('0' + str(int(minutos)))
        else:
            minutos = int(minutos)
        self.elapsed = round(elapsed.total_seconds())
        self.time_label.text = f"Tiempo: {minutos}:{segundos}"

    def update_uncover(self):
        uncover = 0
        for i in range(self.x_board):
            for j in range(self.y_board):
                if (self.buttons[(i,j)].background_color == [0.0, 0.0, 0.0, 1.0] or
                        self.buttons[(i,j)].background_normal == 'img/flag.png' or
                        self.buttons[(i,j)].background_normal == 'img/gem.png'):
                    uncover +=1
        self.uncovered.text = f'Despejado: {uncover}'
        return uncover

    def start_game(self, dif):
        if dif == 0:
            self.x_board, self.y_board = (8, 8)
        elif dif == 1:
            self.x_board, self.y_board = (16, 16)
        elif dif == 2:
            self.x_board, self.y_board = (24, 24)
        elif dif == 3:
            self.x_board, self.y_board = (30, 24)
        Window.size = (32 * self.x_board, 32 * self.y_board + self.top_info.height)
        Window.resizable = False
        Window.minimum_width = 32*self.x_board
        Window.minimum_height = 32 * self.y_board + self.top_info.height
        reset_board(self.x_board, self.y_board, dif)
        self.bombs_layout.cols = self.x_board
        self.create_grid(dif)

    def check_win(self):
        global mines
        win = True
        counter = 0
        for i in range(self.x_board):
            for j in range(self.y_board):
                if self.buttons[(i,j)].background_normal == 'img/flag.png':
                    if board[(i,j)] != 9:
                        win = False
                    counter += 1
        if win and counter == mines and self.update_uncover() == self.x_board * self.y_board:
            return True
        return False

    def create_grid(self, dif):
        # grid populates lr-tb
        for i in range(self.y_board):
            for j in range(self.x_board):
                button = MinesweeperButton(grid_pos=(j, i), game_screen=self, text='', size_hint=(None, None), size=(32, 32))
                self.buttons[(j, i)] = button
                self.bombs_layout.add_widget(button)

    def loose(self):
        print('KABOOM!!! has perdido!')
        print(f'Total seconds: {self.elapsed}')
        self.ticking.cancel()
        self.show_all_mines()
        popup = RestartPopup(parent_screen=self)
        popup.open()

    def win(self):
        print('WOW has ganado!!')
        print(f'GEM time: {self.gem_time}')
        print(f'Total seconds: {self.elapsed}')
        score = self.get_score(self.elapsed, self.gem_time)
        score_chile = f'{score:,}'.replace(',', '.')
        print(f'SCORE: {score_chile}')
        self.ticking.cancel()
        self.manager.current = 'scores'

    def show_all_mines(self):
        for i in range(self.x_board):
            for j in range(self.y_board):
                if board[(i,j)] == 9:
                    self.buttons[(i,j)].background_normal = 'img/bomb.png'

    def get_score(self, total_time, gem_time):
        base = 10000 * self.x_board * self.y_board
        gem = max(0, base - (gem_time * 106666))
        score = int(base + gem - (total_time * 10000))
        print(f'base {base} gem {gem} score {score}')
        return  max(0, score)

    def reset_game(self):
        self.main_layout.clear_widgets()  # Clear the main layout
        self.bombs_layout.clear_widgets()  # Clear the bombs layout
        self.top_info.clear_widgets()  # Clear the top info layout

        # Reinitialize the widgets
        self.label1 = Label(text=str(remaining_mines), font_name='Gabriola', font_size=36, color=[1, 0, 0, 1])
        self.uncovered = Label(text=f'Despejado: 0', font_name='Gabriola', font_size=36)
        self.time_label = Label(text='Tiempo: 00:00', font_name='Gabriola', font_size=36)
        self.main_layout.add_widget(self.top_info)
        self.top_info.add_widget(self.label1)
        self.top_info.add_widget(self.uncovered)
        self.top_info.add_widget(self.time_label)
        self.main_layout.add_widget(self.bombs_layout)
        self.buttons = {}  # Reset buttons dictionary
        self.first_move = True
        self.elapsed = 0
        # Set the window size
        Window.size = (800, 558)
        Window.minimum_width = 800
        Window.minimum_height = 558
        Window.resizable = False


class Scores(Screen):
    def __init__(self, **kwargs):
        super(Scores, self).__init__(**kwargs)
        self.main_layout = GridLayout(cols=1)
        self.top_info = BoxLayout(orientation='horizontal', size_hint_y=None, height=100)
        self.top_info2 = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, pos_hint={'left': 1})
        self.label1 = Label(text='Hall of Fame', font_name='Gabriola', font_size=36, color=[1, 0, 0, 1])
        self.name_label = Label(text='Enter your name:', font_name='Gabriola', font_size=36)
        self.input = TextInput(font_name='Gabriola', font_size=36, write_tab=False, multiline=False,
                               on_text_validate=self.send_score, size_hint=(None, None), size=(200,50))
        dummy=Label(text='')
        self.add_widget(self.main_layout)
        self.main_layout.add_widget(self.top_info)
        self.top_info.add_widget(self.label1)
        self.main_layout.add_widget(self.top_info2)
        self.top_info2.add_widget(self.name_label)
        self.top_info2.add_widget(self.input)
        self.top_info2.add_widget(dummy)

    def send_score(self, instance):
        print(f'Sending Scores name: {instance.text}')
        self.input.disabled = True


class MinesweeperButton(Button):
    def __init__(self, grid_pos, game_screen, **kwargs):
        super(MinesweeperButton, self).__init__(**kwargs)
        self.grid_pos = grid_pos
        self.long_press_time = 0.5
        self.long_press_event = None
        self.game_screen = game_screen
        self.font_name = 'Roboto-Bold'
        self.long_press_detected = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.long_press_event = Clock.schedule_once(self.trigger_long_press, self.long_press_time)
            self.long_press_detected = False
            return True
        return super(MinesweeperButton, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.long_press_event:
                self.long_press_event.cancel()
                self.long_press_event = None
                if not self.long_press_detected:
                    self.handle_short_press()
            return True
        return super(MinesweeperButton, self).on_touch_up(touch)

    def trigger_long_press(self, dt):
        self.long_press_detected = True
        self.handle_long_press()

    def handle_short_press(self):
        global start_time
        if self.game_screen.first_move:
            start_time = datetime.now()
            self.game_screen.ticking = Clock.schedule_interval(self.game_screen.update_time, 1)
            self.game_screen.first_move = False
        print(f"Button at {self.grid_pos} short pressed")
        if board[self.grid_pos] == 9:
            self.background_normal = 'img/bomb.png'
            self.game_screen.loose()
        elif board[self.grid_pos] == 0:
            self.uncover_neighbors(*self.grid_pos, set())
        elif board[self.grid_pos] == 10:
            self.background_normal = 'img/gem.png'
            self.game_screen.gem_time = self.game_screen.elapsed
        else:
            self.text = str(board[self.grid_pos])
            self.background_color = "#000000"
            self.set_color()
        self.game_screen.update_uncover()
        if self.game_screen.check_win():
            self.game_screen.win()

    def handle_long_press(self):
        global remaining_mines
        print(f"Button at {self.grid_pos} long pressed")
        # cannot long press on an uncovered button
        if self.background_color != [0, 0, 0, 1]:
            if self.background_normal == 'atlas://data/images/defaulttheme/button':
                self.background_normal = 'img/flag.png'
                remaining_mines -= 1
            elif self.background_normal == 'img/flag.png':
                self.background_normal = 'img/question.png'
                remaining_mines += 1
            elif self.background_normal == 'img/question.png':
                self.background_normal = 'atlas://data/images/defaulttheme/button'
            self.game_screen.update_mines()
            self.game_screen.update_uncover()
            if self.game_screen.check_win():
                self.game_screen.win()

    def uncover_neighbors(self, x, y, processed):
        if (x, y) in processed:
            return
        processed.add((x, y))
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0:
                    self.game_screen.buttons[(x + dx, y + dy)].text = ''
                    self.game_screen.buttons[(x + dx, y + dy)].background_color = "#000000"
                else:
                    if 0 <= x + dx <= x_board and 0 <= y + dy <= y_board:
                        if board[(x + dx, y + dy)] == 0:
                            self.uncover_neighbors(x + dx, y + dy, processed)
                        elif board[(x + dx, y + dy)] == 10:
                            continue
                        else:
                            if self.game_screen.buttons[(x + dx, y + dy)].background_color != "#000000":
                                self.game_screen.buttons[(x + dx, y + dy)].text = str(board[x + dx, y + dy])
                                self.game_screen.buttons[(x + dx, y + dy)].background_color = "#000000"
                                self.game_screen.buttons[(x + dx, y + dy)].set_color()

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


class RestartPopup(Popup):
    def __init__(self, parent_screen, **kwargs):
        super(RestartPopup, self).__init__(**kwargs)
        self.parent_screen = parent_screen
        self.title = 'Perdiste!'
        self.size_hint = (0.6, 0.4)

        # Create a BoxLayout for the content
        content = BoxLayout(orientation='vertical')

        # Add a label
        content.add_widget(Label(text='Jugar de nuevo?', size_hint_y=0.6))

        # Create a BoxLayout for the buttons
        button_layout = BoxLayout(size_hint_y=0.4)

        # Create Yes button
        yes_button = Button(text='Si')
        yes_button.bind(on_release=self.on_yes)
        button_layout.add_widget(yes_button)

        # Create No button
        no_button = Button(text='No')
        no_button.bind(on_release=self.on_no)
        button_layout.add_widget(no_button)

        # Add button_layout to the content
        content.add_widget(button_layout)

        self.add_widget(content)

    def on_yes(self, instance):
        self.dismiss()
        self.parent_screen.reset_game()  # Reset the game screen
        self.parent_screen.manager.current = 'intro'

    def on_no(self, instance):
        self.dismiss()
        sys.exit()


class BuscaMinas(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(IntroScreen(name='intro'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(Scores(name='scores'))
        return sm


def reset_board(x, y, diff):
    global board, x_board, y_board, remaining_mines, mines
    if 'board' in globals():
        del board
    x_board = x - 1
    y_board = y - 1
    board = np.zeros((x, y), dtype=int)
    if diff <= 1:
        mines = round(x * y * 0.1)
    elif diff == 2:
        mines = round(x * y * 0.15)
    elif diff >= 3:
        mines = round(x * y * 0.20)
    grid_size = np.arange(x * y)
    rand_mines = np.random.choice(grid_size, mines, replace=False)
    mask = np.isin(grid_size, rand_mines, invert=True)
    new_array = grid_size[mask]
    rand_gem = np.random.choice(new_array, 1)
    print(rand_gem)
    bomb_positions = [(pos // y, pos % y) for pos in rand_mines]
    gem_position = (rand_gem // y, rand_gem % y)
    print(bomb_positions)
    for pos in bomb_positions:
        board[pos] = 9
    board[gem_position] = 10
    for i in range(x):
        for j in range(y):
            if board[i, j] < 9:
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


global remaining_mines
remaining_mines = 0
if __name__ == "__main__":
    BuscaMinas().run()
