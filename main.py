from random import randint

from kivy.config import Config

Config.set('graphics', 'width', '1500')
Config.set('graphics', 'height', '700')


from kivy import platform
from kivy.app import App
from kivy.graphics import Color, Line, Quad, Triangle
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.lang import Builder
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout

Builder.load_file('menu.kv')


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_down, on_touch_up

    menu_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    VERT_NUMBERS_LINES = 12
    VERT_LINES_SPACING = .4
    vertical_lines = []

    HOR_NUMBERS_LINES = 10
    HOR_LINES_SPACING = .1
    horizontal_lines = []

    SPEED = .7
    current_offset_y = 0
    current_y_loop = 0

    SPEED_X = 3
    current_speed_x = 0
    current_offset_x = 0

    NUMBER_OF_TILES = 10
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = 0.1
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    game_over_state = False
    start_game_state = False

    menu_title = StringProperty("H   O   R   I   Z   O   N")
    menu_button_title = StringProperty("START")

    score_txt = StringProperty("0")
    high_score_int = 0
    high_score_txt = StringProperty(f"HIGH - SCORE: {str(high_score_int)}")

    sound_begin = None
    sound_galaxy = None
    sound_game_over_impact = None
    sound_game_over_voice = None
    sound_music = None
    sound_restart = None

    dif_level = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_audio()
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()

        if self.is_desktop():
            self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
            self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1/60)
        self.sound_galaxy.play()

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_game_over_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_game_over_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music.volume = 1
        self.sound_galaxy.volume = .25
        self.sound_game_over_impact.volume = .6
        self.sound_game_over_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_begin.volume = .25

    def set_difficulty_level(self):
        if not self.dif_level:
            self.dif_level = 'medium'

        if self.dif_level == 'easy':
            self.SPEED = .5
        elif self.dif_level == 'medium':
            self.SPEED = .7
        elif self.dif_level == 'hard':
            self.SPEED = 1.2

    def reset_game(self):
        self.current_offset_y = 0
        self.current_y_loop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.score_txt = f"SCORE: {str(self.current_y_loop)}"
        self.set_difficulty_level()

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.game_over_state = False

    @staticmethod
    def is_desktop():
        if platform in ('linux', 'win', 'macosx'):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0, 0, 0)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.height * self.SHIP_HEIGHT

        self.ship_coordinates[0] = (center_x - ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, ship_height + base_y)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_y_loop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        x_min, y_min = self.get_tile_coordinates(ti_x, ti_y)
        x_max, y_max = self.get_tile_coordinates(ti_x+1, ti_y+1)

        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if x_min <= px <= x_max and y_min <= py <= y_max:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.NUMBER_OF_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_y = 0
        last_x = 0

        for i in range(len(self.tiles_coordinates)-1, -1, -1):
            if self.tiles_coordinates[i][1] < self.current_y_loop:
                del self.tiles_coordinates[i]

        if self.tiles_coordinates:
            last_x = self.tiles_coordinates[-1][0]
            last_y = self.tiles_coordinates[-1][1] + 1

        for i in range(len(self.tiles_coordinates), self.NUMBER_OF_TILES):
            r = randint(0, 2)

            start_index = -int(self.VERT_NUMBERS_LINES / 2) + 1
            end_index = start_index + self.VERT_NUMBERS_LINES - 2
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2
            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            last_y += 1

    def init_vertical_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.VERT_NUMBERS_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.VERT_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_y_loop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def get_line_y_from_index(self, index):
        spacing_y = self.HOR_LINES_SPACING * self.height
        line_y = index * spacing_y - self.current_offset_y
        return line_y

    def update_tiles(self):
        for i in range(0, self.NUMBER_OF_TILES):
            tile = self.tiles[i]
            tile_x, tile_y = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_x, tile_y)
            xmax, ymax = self.get_tile_coordinates(tile_x+1, tile_y+1)

            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        start_index = -int(self.VERT_NUMBERS_LINES/2) + 1
        end_index = start_index + self.VERT_NUMBERS_LINES

        for i in range(start_index, end_index):
            line_x = self.get_line_x_from_index(i)
            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(1, 1, 1)
            for i in range(0, self.HOR_NUMBERS_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.VERT_NUMBERS_LINES/2) + 1
        end_index = start_index + self.VERT_NUMBERS_LINES - 1

        x_min = self.get_line_x_from_index(start_index)
        x_max = self.get_line_x_from_index(end_index)

        for i in range(0, self.HOR_NUMBERS_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(x_min, line_y)
            x2, y2 = self.transform(x_max, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()

        if not self.game_over_state and self.start_game_state:
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.HOR_LINES_SPACING * self.height
            while self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_y_loop += 1
                self.score_txt = f"SCORE: {str(self.current_y_loop)}"
                self.generate_tiles_coordinates()

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.game_over_state:
            if int(self.high_score_int) <= self.current_y_loop:
                self.high_score_int = self.current_y_loop
                self.high_score_txt = f"HIGH - SCORE: {str(self.high_score_int)}"

            self.game_over_state = True
            self.menu_widget.opacity = 1
            self.menu_title = " G  A  M  E     O  V  E  R"
            self.menu_button_title = "RESTART"
            self.sound_music.stop()
            self.sound_game_over_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 2)

    def play_game_over_voice_sound(self, dt):
        if self.game_over_state:
            self.sound_game_over_voice.play()

    def on_menu_button_press(self):
        if self.start_game_state:
            self.sound_restart.play()
        else:
            self.sound_begin.play()
        self.sound_music.play()

        self.reset_game()
        self.menu_widget.opacity = 0
        self.start_game_state = True

    def on_difficulty_level_button_press(self, dif_level):
        self.dif_level = dif_level


class HorizonApp(App):
    pass


HorizonApp().run()
