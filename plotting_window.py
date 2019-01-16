'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import os
import cv2
import numpy as np
import utilities as ut
import threading
from functools import partial
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from timer_thread import TimerThread

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class PlottingWindow(QScrollArea):

    def __init__(self):
        super(PlottingWindow, self).__init__()
        self.plotting_content = PlottingContent()
        self.setWidget(self.plotting_content)

class PlottingContent(QMainWindow):

    # Defining Initialization Functions
    def __init__(self):
        super(PlottingContent, self).__init__()
        self.initUI()
    def initUI(self):
        self.get_main_window_attributes()
        self.initialize_layout()
        self.initialize_class_variables()
        self.add_preview_frame_window()
        self.add_frame_window_slider()
        self.add_preview_frame_number_textbox()
        self.add_video_time_textbox()
        self.add_frame_change_buttons()
        self.add_video_playback_buttons()
        self.add_interactive_frame_buttons()
        self.add_data_plot_window()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.resize(self.plotting_content_size[0], self.plotting_content_size[1])
    def initialize_layout(self):
        self.font_title = QFont()
        self.font_text = QFont()
        self.font_colour_parameters = QFont()

        if self.main_window_width == 1920 and self.main_window_height == 1020:
            self.font_title.setPointSize(14)
            self.font_text.setPointSize(8)
            self.font_colour_parameters.setPointSize(7)
            self.plotting_content_size = (1910, 920)
            self.main_window_x_offset = 10
            self.main_window_y_offset = 15
            self.main_window_spacing = 10
            self.preview_frame_window_size = (800, 800)
            self.preview_frame_window_x_offset = 30
            self.preview_frame_window_y_offset = 30
            self.preview_frame_window_label_size = (self.preview_frame_window_size[0] - self.preview_frame_window_x_offset, self.preview_frame_window_size[1] - self.preview_frame_window_y_offset)
            self.plotting_window_size = (1455, 1240)
            self.preview_frame_window_slider_height = 20
            self.preview_frame_number_textbox_y_spacing = 10
            self.preview_frame_number_textbox_label_size = (160, 25)
            self.preview_frame_number_textbox_size = (120, 25)
            self.video_time_textbox_y_spacing = 10
            self.video_time_textbox_label_size = (160, 25)
            self.video_time_textbox_size = (120, 25)
            self.frame_change_button_size = (50, 50)
            self.frame_change_button_x_offset = 30
            self.frame_change_button_x_spacing = 5
            self.frame_change_button_icon_size = (60, 60)
            self.interactive_frame_button_size = (50, 50)
            self.interactive_frame_button_icon_size = (45, 45)
            self.interactive_frame_button_x_offset = 30
            self.interactive_frame_button_x_spacing = 5
            self.video_playback_button_size = (50, 50)
            self.video_playback_button_x_offset = 30
            self.video_playback_button_x_spacing = 5
            self.video_playback_button_icon_size = (60, 60)
        else:
            self.font_title.setPointSize(18)
            self.font_text.setPointSize(10)
            self.font_colour_parameters.setPointSize(10)
            self.plotting_content_size = (2550, 1320)
            self.main_window_x_offset = 10
            self.main_window_y_offset = 10
            self.main_window_spacing = 10
            self.preview_frame_window_size = (1000, 1000)
            self.preview_frame_window_x_offset = 30
            self.preview_frame_window_y_offset = 30
            self.preview_frame_window_label_size = (self.preview_frame_window_size[0] - self.preview_frame_window_x_offset, self.preview_frame_window_size[1] - self.preview_frame_window_y_offset)
            self.plotting_window_size = (1060, 1000)
            self.preview_frame_window_slider_height = 20
            self.preview_frame_number_textbox_y_spacing = 10
            self.preview_frame_number_textbox_label_size = (100, 25)
            self.preview_frame_number_textbox_size = (120, 25)
            self.video_time_textbox_y_spacing = 10
            self.video_time_textbox_label_size = (100, 25)
            self.video_time_textbox_size = (120, 25)
            self.frame_change_button_size = (50, 50)
            self.frame_change_button_x_offset = 10
            self.frame_change_button_x_spacing = 5
            self.frame_change_button_icon_size = (46, 46)
            self.interactive_frame_button_size = (50, 50)
            self.interactive_frame_button_icon_size = (40, 40)
            self.interactive_frame_button_x_offset = 10
            self.interactive_frame_button_x_spacing = 5
            self.video_playback_button_size = (50, 50)
            self.video_playback_button_x_offset = 30
            self.video_playback_button_x_spacing = 5
            self.video_playback_button_icon_size = (60, 60)
    def initialize_class_variables(self):
        self.frame_number = 1
        self.video_path = None
        self.previous_preview_frame_window_horizontal_scroll_bar_max = None
        self.previous_preview_frame_window_vertical_scroll_bar_max = None
        self.magnify_frame = False
        self.pan_frame = False
        self.play_video_slow_speed = False
        self.play_video_medium_speed = False
        self.play_video_max_speed = False
        self.data_plot = None
        self.video_playback_thread = None

    def get_main_window_attributes(self):
        self.main_window_width = QDesktopWidget().availableGeometry().width()
        self.main_window_height = QDesktopWidget().availableGeometry().height()
    def get_video_attributes(self):
        self.video_path_folder = os.path.dirname(self.video_path)
        self.video_path_basename = os.path.basename(self.video_path)
        self.video_n_frames = ut.get_total_frame_number_from_video(self.video_path)
        self.video_fps = ut.get_fps_from_video(self.video_path)
        self.video_frame_width, self.video_frame_height = ut.get_frame_size_from_video(self.video_path)

    def add_preview_frame_window(self):
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height

        self.preview_frame_window = QScrollArea(self)
        self.preview_frame_window.setFrameShape(QFrame.StyledPanel)
        # self.preview_frame_window.setFrameShadow(QFrame.Sunken)
        # self.preview_frame_window.setLineWidth(5)
        self.preview_frame_window.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_frame_window.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview_frame_window.move(new_x, new_y)
        self.preview_frame_window.resize(self.preview_frame_window_size[0], self.preview_frame_window_size[1])
        self.preview_frame_window.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.preview_frame_window_label = QLabel(self)
        self.preview_frame_window_label.move(new_x, new_y)
        self.preview_frame_window_label.resize(self.preview_frame_window_label_size[0], self.preview_frame_window_label_size[1])
        self.preview_frame_window_label.setText('Preview Frame Window')
        self.preview_frame_window_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.preview_frame_window_label.setFont(self.font_title)
        self.preview_frame_window_label.mousePressEvent = self.event_preview_frame_window_label_mouse_clicked
        self.preview_frame_window_label.mouseMoveEvent = self.event_preview_frame_window_label_mouse_moved
        self.preview_frame_window.setWidget(self.preview_frame_window_label)
    def add_frame_window_slider(self):
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing) / 1400) * self.main_window_height
        new_height = (self.preview_frame_window_slider_height / 1400) * self.main_window_height

        self.frame_window_slider = QSlider(Qt.Horizontal, self)
        self.frame_window_slider.setToolTip('Move slider to change preview frame number.')
        self.frame_window_slider.move(new_x, new_y)
        self.frame_window_slider.resize(self.preview_frame_window_size[0], new_height)
        self.frame_window_slider.setEnabled(False)
        self.frame_window_slider.setTickInterval(0)
        self.frame_window_slider.setSingleStep(0)
        self.frame_window_slider.sliderMoved.connect(self.check_frame_window_slider_moved)
        self.update_frame_window_slider(inactivate = True)
    def add_preview_frame_number_textbox(self):
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing) / 1400) * self.main_window_height

        self.preview_frame_number_textbox_label = QLabel(self)
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        self.preview_frame_number_textbox_label.move(new_x, new_y)
        new_width = (self.preview_frame_number_textbox_label_size[0] / 2560) * self.main_window_width
        new_height = (self.preview_frame_number_textbox_label_size[1] / 1400) * self.main_window_height
        self.preview_frame_number_textbox_label.resize(new_width, new_height)
        self.preview_frame_number_textbox_label.setText('Frame Number: ')
        self.preview_frame_number_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.preview_frame_number_textbox_label.setFont(self.font_text)
        self.preview_frame_number_textbox = QLineEdit(self)
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0]) / 2560) * self.main_window_width
        self.preview_frame_number_textbox.move(new_x, new_y)
        new_width = (self.preview_frame_number_textbox_size[0] / 2560) * self.main_window_width
        new_height = (self.preview_frame_number_textbox_size[1] / 1400) * self.main_window_height
        self.preview_frame_number_textbox.resize(new_width, new_height)
        self.preview_frame_number_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_frame_number_textbox.setFont(self.font_text)
        self.preview_frame_number_textbox.returnPressed.connect(self.check_preview_frame_number_textbox)
        self.update_preview_frame_number_textbox(inactivate = True)
    def add_video_time_textbox(self):
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing + self.preview_frame_number_textbox_label_size[1] + self.video_time_textbox_y_spacing) / 1400) * self.main_window_height

        self.video_time_textbox_label = QLabel(self)
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        self.video_time_textbox_label.move(new_x, new_y)
        new_width = (self.preview_frame_number_textbox_label_size[0] / 2560) * self.main_window_width
        new_height = (self.preview_frame_number_textbox_label_size[1] / 1400) * self.main_window_height
        self.video_time_textbox_label.resize(new_width, new_height)
        self.video_time_textbox_label.setText('Time (seconds): ')
        self.video_time_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.video_time_textbox_label.setFont(self.font_text)
        self.video_time_textbox = QLineEdit(self)
        new_x = ((self.main_window_x_offset + self.video_time_textbox_label_size[0]) / 2560) * self.main_window_width
        self.video_time_textbox.move(new_x, new_y)
        new_width = (self.video_time_textbox_size[0] / 2560) * self.main_window_width
        new_height = (self.video_time_textbox_size[1] / 1400) * self.main_window_height
        self.video_time_textbox.resize(new_width, new_height)
        self.video_time_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.video_time_textbox.setFont(self.font_text)
        self.video_time_textbox.returnPressed.connect(self.check_video_time_textbox)
        self.update_video_time_textbox(inactivate = True)
    def add_video_playback_buttons(self):
        new_icon_width = ((self.video_playback_button_size[0] / 2560) * self.main_window_width) - (self.video_playback_button_size[0] - self.video_playback_button_icon_size[0])
        new_icon_height = ((self.video_playback_button_size[1] / 1400) * self.main_window_height) - (self.video_playback_button_size[1] - self.video_playback_button_icon_size[1])
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing) / 1400) * self.main_window_height
        new_width = (self.video_playback_button_size[0] / 2560) * self.main_window_width
        new_height = (self.video_playback_button_size[1] / 1400) * self.main_window_height

        self.pause_video_button = QPushButton(self)
        self.pause_video_button.setIcon(QIcon('icons\\button_icon_7.png'))
        self.pause_video_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (0 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]))) / 2560) * self.main_window_width
        self.pause_video_button.move(new_x, new_y)
        self.pause_video_button.resize(new_width, new_height)
        self.pause_video_button.clicked.connect(self.check_pause_video_button)
        self.pause_video_button.setCheckable(True)

        self.play_video_slow_speed_button = QPushButton(self)
        self.play_video_slow_speed_button.setIcon(QIcon('icons\\button_icon_8.png'))
        self.play_video_slow_speed_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (1 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]))) / 2560) * self.main_window_width
        self.play_video_slow_speed_button.move(new_x, new_y)
        self.play_video_slow_speed_button.resize(new_width, new_height)
        self.play_video_slow_speed_button.clicked.connect(self.check_play_video_slow_speed_button)
        self.play_video_slow_speed_button.setCheckable(True)

        self.play_video_medium_speed_button = QPushButton(self)
        self.play_video_medium_speed_button.setIcon(QIcon('icons\\button_icon_9.png'))
        self.play_video_medium_speed_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (2 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]))) / 2560) * self.main_window_width
        self.play_video_medium_speed_button.move(new_x, new_y)
        self.play_video_medium_speed_button.resize(new_width, new_height)
        self.play_video_medium_speed_button.clicked.connect(self.check_play_video_medium_speed_button)
        self.play_video_medium_speed_button.setCheckable(True)

        self.play_video_max_speed_button = QPushButton(self)
        self.play_video_max_speed_button.setIcon(QIcon('icons\\button_icon_10.png'))
        self.play_video_max_speed_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]))) / 2560) * self.main_window_width
        self.play_video_max_speed_button.move(new_x, new_y)
        self.play_video_max_speed_button.resize(new_width, new_height)
        self.play_video_max_speed_button.clicked.connect(self.check_play_video_max_speed_button)
        self.play_video_max_speed_button.setCheckable(True)
        self.update_video_playback_buttons(inactivate = True)
    def add_frame_change_buttons(self):
        new_icon_width = ((self.frame_change_button_size[0] / 2560) * self.main_window_width) - (self.frame_change_button_size[0] - self.frame_change_button_icon_size[0])
        new_icon_height = ((self.frame_change_button_size[1] / 1400) * self.main_window_height) - (self.frame_change_button_size[1] - self.frame_change_button_icon_size[1])
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing) / 1400) * self.main_window_height
        new_width = (self.frame_change_button_size[0] / 2560) * self.main_window_width
        new_height = (self.frame_change_button_size[1] / 1400) * self.main_window_height

        self.large_frame_decrease_button = QPushButton(self)
        self.large_frame_decrease_button.setIcon(QIcon('icons\\button_icon_1.png'))
        self.large_frame_decrease_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (0 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.large_frame_decrease_button.move(new_x, new_y)
        self.large_frame_decrease_button.resize(new_width, new_height)
        self.large_frame_decrease_button.clicked.connect(self.check_large_frame_decrease_button)

        self.medium_frame_decrease_button = QPushButton(self)
        self.medium_frame_decrease_button.setIcon(QIcon('icons\\button_icon_2.png'))
        self.medium_frame_decrease_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (1 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.medium_frame_decrease_button.move(new_x, new_y)
        self.medium_frame_decrease_button.resize(new_width, new_height)
        self.medium_frame_decrease_button.clicked.connect(self.check_medium_frame_decrease_button)

        self.small_frame_decrease_button = QPushButton(self)
        self.small_frame_decrease_button.setIcon(QIcon('icons\\button_icon_3.png'))
        self.small_frame_decrease_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (2 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.small_frame_decrease_button.move(new_x, new_y)
        self.small_frame_decrease_button.resize(new_width, new_height)
        self.small_frame_decrease_button.clicked.connect(self.check_small_frame_decrease_button)

        self.small_frame_increase_button = QPushButton(self)
        self.small_frame_increase_button.setIcon(QIcon('icons\\button_icon_4.png'))
        self.small_frame_increase_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (3 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.small_frame_increase_button.move(new_x, new_y)
        self.small_frame_increase_button.resize(new_width, new_height)
        self.small_frame_increase_button.clicked.connect(self.check_small_frame_increase_button)

        self.medium_frame_increase_button = QPushButton(self)
        self.medium_frame_increase_button.setIcon(QIcon('icons\\button_icon_5.png'))
        self.medium_frame_increase_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (4 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.medium_frame_increase_button.move(new_x, new_y)
        self.medium_frame_increase_button.resize(new_width, new_height)
        self.medium_frame_increase_button.clicked.connect(self.check_medium_frame_increase_button)

        self.large_frame_increase_button = QPushButton(self)
        self.large_frame_increase_button.setIcon(QIcon('icons\\button_icon_6.png'))
        self.large_frame_increase_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (5 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]))) / 2560) * self.main_window_width
        self.large_frame_increase_button.move(new_x, new_y)
        self.large_frame_increase_button.resize(new_width, new_height)
        self.large_frame_increase_button.clicked.connect(self.check_large_frame_increase_button)
        self.update_frame_change_buttons(inactivate = True)
    def add_interactive_frame_buttons(self):
        new_icon_width = ((self.interactive_frame_button_size[0] / 2560) * self.main_window_width) - (self.interactive_frame_button_size[0] - self.interactive_frame_button_icon_size[0])
        new_icon_height = ((self.interactive_frame_button_size[1] / 1400) * self.main_window_height) - (self.interactive_frame_button_size[1] - self.interactive_frame_button_icon_size[1])
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing) / 1400) * self.main_window_height
        new_width = (self.interactive_frame_button_size[0] / 2560) * self.main_window_width
        new_height = (self.interactive_frame_button_size[1] / 1400) * self.main_window_height

        self.magnify_frame_button = QPushButton(self)
        self.magnify_frame_button.setIcon(QIcon('icons\\button_icon_11.png'))
        self.magnify_frame_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (5 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]) + self.frame_change_button_size[0]) + self.interactive_frame_button_x_offset + (0 * (self.interactive_frame_button_x_spacing + self.interactive_frame_button_size[0]))) / 2560) * self.main_window_width
        self.magnify_frame_button.move(new_x, new_y)
        self.magnify_frame_button.resize(new_width, new_height)
        self.magnify_frame_button.clicked.connect(self.check_magnify_frame_button)
        self.magnify_frame_button.setCheckable(True)

        self.pan_frame_button = QPushButton(self)
        self.pan_frame_button.setIcon(QIcon('icons\\button_icon_12.png'))
        self.pan_frame_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (5 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]) + self.frame_change_button_size[0]) + self.interactive_frame_button_x_offset + (1 * (self.interactive_frame_button_x_spacing + self.interactive_frame_button_size[0]))) / 2560) * self.main_window_width
        self.pan_frame_button.move(new_x, new_y)
        self.pan_frame_button.resize(new_width, new_height)
        self.pan_frame_button.clicked.connect(self.check_pan_frame_button)
        self.pan_frame_button.setCheckable(True)

        self.update_interactive_frame_buttons(inactivate = True)
    def add_data_plot_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height
        new_width = (self.plotting_window_size[0] / 2560) * self.main_window_width
        new_height = (self.plotting_window_size[1] / 1400) * self.main_window_height

        self.data_plot_window = QScrollArea(self)
        self.data_plot_window.move(new_x, new_y)
        self.data_plot_window.resize(new_width, new_height)
        self.data_plot_window.setFrameShape(QFrame.StyledPanel)

    def update_preview_frame(self, frame, frame_width, frame_height, scaled_width = None, grayscale = False):
        if grayscale:
            format = QImage.Format_Indexed8
        else:
            format = QImage.Format_RGB888
        if scaled_width is None:
            scaled_width = int(self.video_frame_width / 100) * 100
        else:
            scaled_width = int(scaled_width / 100) * 100
        self.preview_frame = QImage(frame.data, frame_width, frame_height, format)
        self.preview_frame = self.preview_frame.scaledToWidth(scaled_width)
        frame = cv2.resize(frame, dsize=(self.preview_frame.width(), self.preview_frame.height()), interpolation=cv2.INTER_CUBIC).copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.preview_frame = QImage(frame.data, self.preview_frame.width(), self.preview_frame.height(), format)
    def update_preview_frame_window(self, clear = False):
        if not clear:
            self.preview_frame_window_label.setPixmap(QPixmap.fromImage(self.preview_frame))
            self.preview_frame_window_label_size = (self.preview_frame.width(), self.preview_frame.height())
            self.preview_frame_window_label.resize(self.preview_frame_window_label_size[0], self.preview_frame_window_label_size[1])
        else:
            self.preview_frame_window_label.clear()
            self.preview_frame_window_label.setText('Preview Frame Window')
            self.preview_frame_window_label_size = (self.preview_frame_window_size[0] - self.preview_frame_window_x_offset, self.preview_frame_window_size[1] - self.preview_frame_window_y_offset)
            self.preview_frame_window_label.resize(self.preview_frame_window_label_size[0], self.preview_frame_window_label_size[1])
    def update_data_plot_window(self, clear = False):
        if not clear:
            self.data_plot_window.setWidget(self.data_plot)
        else:
            if self.data_plot is not None:
                self.data_plot.update_plots(clear = True)
                self.data_plot.deleteLater()
                self.data_plot = None
    def update_frame_window_slider(self, activate = False, inactivate = False):
        if activate:
            if not self.frame_window_slider.isEnabled():
                self.frame_window_slider.setEnabled(True)
                self.frame_window_slider.setTickPosition(QSlider.TicksBelow)
        if inactivate:
            if self.frame_window_slider.isEnabled():
                self.frame_window_slider.setEnabled(False)
                self.frame_window_slider.setTickPosition(QSlider.NoTicks)
        if self.frame_window_slider.isEnabled():
            self.frame_window_slider.setMinimum(1)
            self.frame_window_slider.setMaximum(self.video_n_frames)
            self.frame_window_slider.setValue(self.frame_number)
        else:
            self.frame_window_slider.setMinimum(0)
            self.frame_window_slider.setMaximum(0)
            self.frame_window_slider.setValue(0)
    def update_preview_frame_number_textbox(self, activate = False, inactivate = False):
        if activate:
            if not self.preview_frame_number_textbox.isEnabled():
                self.preview_frame_number_textbox.setEnabled(True)
        if inactivate:
            if self.preview_frame_number_textbox.isEnabled():
                self.preview_frame_number_textbox.setEnabled(False)
        if self.preview_frame_number_textbox.isEnabled():
            self.preview_frame_number_textbox.setText('{0}'.format(self.frame_number))
        else:
            self.preview_frame_number_textbox.setText('{0}'.format(0))
    def update_frame_change_buttons(self, activate = False, inactivate = False):
        if activate:
            if not self.large_frame_decrease_button.isEnabled():
                self.large_frame_decrease_button.setEnabled(True)
            if not self.medium_frame_decrease_button.isEnabled():
                self.medium_frame_decrease_button.setEnabled(True)
            if not self.small_frame_decrease_button.isEnabled():
                self.small_frame_decrease_button.setEnabled(True)
            if not self.small_frame_increase_button.isEnabled():
                self.small_frame_increase_button.setEnabled(True)
            if not self.medium_frame_increase_button.isEnabled():
                self.medium_frame_increase_button.setEnabled(True)
            if not self.large_frame_increase_button.isEnabled():
                self.large_frame_increase_button.setEnabled(True)
        if inactivate:
            if self.large_frame_decrease_button.isEnabled():
                self.large_frame_decrease_button.setEnabled(False)
            if self.medium_frame_decrease_button.isEnabled():
                self.medium_frame_decrease_button.setEnabled(False)
            if self.small_frame_decrease_button.isEnabled():
                self.small_frame_decrease_button.setEnabled(False)
            if self.small_frame_increase_button.isEnabled():
                self.small_frame_increase_button.setEnabled(False)
            if self.medium_frame_increase_button.isEnabled():
                self.medium_frame_increase_button.setEnabled(False)
            if self.large_frame_increase_button.isEnabled():
                self.large_frame_increase_button.setEnabled(False)
    def update_interactive_frame_buttons(self, activate = False, inactivate = False):
        if activate:
            if not self.magnify_frame_button.isEnabled():
                self.magnify_frame_button.setEnabled(True)
            if not self.pan_frame_button.isEnabled():
                self.pan_frame_button.setEnabled(True)
        if inactivate:
            if self.magnify_frame_button.isEnabled():
                self.magnify_frame_button.setEnabled(False)
                if self.magnify_frame_button.isChecked():
                    self.magnify_frame_button.setChecked(False)
            if self.pan_frame_button.isEnabled():
                self.pan_frame_button.setEnabled(False)
                if self.pan_frame_button.isChecked():
                    self.pan_frame_button.setChecked(False)
        if self.magnify_frame_button.isEnabled():
            if self.magnify_frame:
                self.magnify_frame_button.setChecked(True)
            else:
                self.magnify_frame_button.setChecked(False)
        if self.pan_frame_button.isEnabled():
            if self.pan_frame:
                self.pan_frame_button.setChecked(True)
            else:
                self.pan_frame_button.setChecked(False)
    def update_frame_window_slider_position(self):
        self.frame_window_slider.setValue(self.frame_number)
    def update_preview_frame_window_scroll_bars(self):
        if self.preview_frame_window_label_size[0] > self.preview_frame_window_size[0]:
            self.preview_frame_window.horizontalScrollBar().setValue(self.preview_frame_window.horizontalScrollBar().maximum() / 2)
        if self.preview_frame_window_label_size[1] > self.preview_frame_window_size[1]:
            self.preview_frame_window.verticalScrollBar().setValue(self.preview_frame_window.verticalScrollBar().maximum() / 2)
    def update_video_playback_buttons(self, activate = False, inactivate = False, activate_pause_video_button = False):
        if activate:
            if not self.pause_video_button.isEnabled():
                self.pause_video_button.setEnabled(True)
            if not self.play_video_slow_speed_button.isEnabled():
                self.play_video_slow_speed_button.setEnabled(True)
            if not self.play_video_medium_speed_button.isEnabled():
                self.play_video_medium_speed_button.setEnabled(True)
            if not self.play_video_max_speed_button.isEnabled():
                self.play_video_max_speed_button.setEnabled(True)
        if inactivate:
            if self.pause_video_button.isEnabled():
                self.pause_video_button.setEnabled(False)
            if self.play_video_slow_speed_button.isEnabled():
                self.play_video_slow_speed_button.setEnabled(False)
            if self.play_video_medium_speed_button.isEnabled():
                self.play_video_medium_speed_button.setEnabled(False)
            if self.play_video_max_speed_button.isEnabled():
                self.play_video_max_speed_button.setEnabled(False)
        if activate_pause_video_button:
            if not self.pause_video_button.isChecked():
                self.pause_video_button.setChecked(True)
    def update_video_time_textbox(self, activate = False, inactivate = False):
        if activate:
            if not self.video_time_textbox.isEnabled():
                self.video_time_textbox.setEnabled(True)
        if inactivate:
            if self.video_time_textbox.isEnabled():
                self.video_time_textbox.setEnabled(False)
        if self.video_time_textbox.isEnabled():
            self.video_time_textbox.setText('{0}'.format(round(self.frame_number / self.video_fps, 2)))
        else:
            self.video_time_textbox.setText('{0}'.format(0))

    def trigger_open_video(self):
        self.video_path, _ = QFileDialog.getOpenFileName(self,"Open Video File", "","Video Files (*.avi; *.mp4)", options=QFileDialog.Options())
        if self.video_path:
            self.get_video_attributes()
            success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1, convert_to_grayscale = False)
            if success and self.frame is not None:
                self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height)
                self.update_preview_frame_window()
                self.update_preview_frame_window_scroll_bars()
                self.update_frame_window_slider(activate = True)
                self.update_preview_frame_number_textbox(activate = True)
                self.update_video_time_textbox(activate = True)
                self.update_video_playback_buttons(activate = True, activate_pause_video_button = True)
                self.update_frame_change_buttons(activate = True)
                self.update_interactive_frame_buttons(activate = True)
    def trigger_update_preview(self, magnify = False, demagnify = False):
        if self.video_path is not None:
            success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1, convert_to_grayscale = False)
            if success and self.frame is not None:
                if magnify:
                    self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] + 100)
                if demagnify:
                    self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] - 100)
                if not magnify and not demagnify:
                    self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0])
                self.update_preview_frame_window()
                self.update_frame_window_slider(activate = True)
                self.update_preview_frame_number_textbox(activate = True)
                self.update_video_time_textbox(activate = True)
                self.update_video_playback_buttons(activate = True)
                self.update_frame_change_buttons(activate = True)
                self.update_interactive_frame_buttons(activate = True)
        else:
            self.update_preview_frame_window(clear = True)
    def trigger_load_tracking_results(self):
        self.tracking_data_path, _ = QFileDialog.getOpenFileName(self, "Open Tracking Data", "","Tracking Data (*.npy)", options = QFileDialog.Options())
        if self.tracking_data_path:
            # try:
            data = np.load(self.tracking_data_path).item()
            self.data_plot = DataPlot()
            self.data_plot.initialize_class_variables(data = data)
            self.data_plot.calculate_variables()
            self.data_plot.update_plots()
            self.update_data_plot_window()
            # except:
            #     print('Error! Could not load tracking data.')
    def trigger_unload_all_plotting(self):
        self.update_data_plot_window(clear = True)
        self.initialize_class_variables()
        self.update_preview_frame_window(clear = True)
        self.update_preview_frame_number_textbox(inactivate = True)
        self.update_frame_window_slider(inactivate = True)
        self.update_video_time_textbox(inactivate = True)
        self.update_frame_change_buttons(inactivate = True)
        self.update_video_playback_buttons(inactivate = True)
        self.update_frame_window_slider_position()
    def trigger_pause_video(self):
        if self.video_playback_thread is not None:
            self.video_playback_thread.close()
            self.video_playback_thread.wait()
            self.video_playback_thread = None
        if self.play_video_slow_speed:
            self.play_video_slow_speed = False
        if self.play_video_medium_speed:
            self.play_video_medium_speed = False
        if self.play_video_max_speed:
            self.play_video_max_speed = False
    def trigger_play_video_slow_speed(self):
        if self.play_video_slow_speed:
            self.frame_number += 1
            if self.frame_number <= self.video_n_frames:
                self.trigger_update_preview()
            else:
                self.frame_number = 1
                self.trigger_update_preview()
    def trigger_play_video_medium_speed(self):
        if self.play_video_medium_speed:
            self.frame_number += int(self.video_fps / 10)
            if self.frame_number <= self.video_n_frames:
                self.trigger_update_preview()
            else:
                self.frame_number = 1
                self.trigger_update_preview()
    def trigger_play_video_max_speed(self):
        if self.play_video_max_speed:
            self.frame_number += int(self.video_fps)
            if self.frame_number <= self.video_n_frames:
                self.trigger_update_preview()
            else:
                self.frame_number = 1
                self.trigger_update_preview()

    def check_preview_frame_number_textbox(self):
        if self.preview_frame_number_textbox.text().isdigit():
            if int(self.preview_frame_number_textbox.text()) > self.video_n_frames:
                self.frame_number = self.video_n_frames
            else:
                if int(self.preview_frame_number_textbox.text()) != 0:
                    self.frame_number = int(self.preview_frame_number_textbox.text())
                else:
                    self.frame_number = 1
        self.trigger_update_preview()
    def check_frame_window_slider_moved(self):
        self.frame_number = int(self.frame_window_slider.sliderPosition())
        self.trigger_update_preview()
    def check_large_frame_decrease_button(self):
        self.frame_number -= 100
        if self.frame_number < 1:
            self.frame_number = 1
        self.trigger_update_preview()
    def check_medium_frame_decrease_button(self):
        self.frame_number -= 10
        if self.frame_number < 1:
            self.frame_number = 1
        self.trigger_update_preview()
    def check_small_frame_decrease_button(self):
        self.frame_number -= 1
        if self.frame_number < 1:
            self.frame_number = 1
        self.trigger_update_preview()
    def check_small_frame_increase_button(self):
        self.frame_number += 1
        if self.frame_number > self.video_n_frames:
            self.frame_number = self.video_n_frames
        self.trigger_update_preview()
    def check_medium_frame_increase_button(self):
        self.frame_number += 10
        if self.frame_number > self.video_n_frames:
            self.frame_number = self.video_n_frames
        self.trigger_update_preview()
    def check_large_frame_increase_button(self):
        self.frame_number += 100
        if self.frame_number > self.video_n_frames:
            self.frame_number = self.video_n_frames
        self.trigger_update_preview()
    def check_magnify_frame_button(self):
        if self.magnify_frame_button.isChecked():
            self.magnify_frame = True
            if self.pan_frame_button.isChecked():
                self.pan_frame = False
                self.pan_frame_button.setChecked(False)
        else:
            self.magnify_frame = False
    def check_pan_frame_button(self):
        if self.pan_frame_button.isChecked():
            self.pan_frame = True
            if self.magnify_frame_button.isChecked():
                self.magnify_frame = False
                self.magnify_frame_button.setChecked(False)
        else:
            self.pan_frame = False
    def check_pause_video_button(self):
        if not self.play_video_slow_speed and not self.play_video_medium_speed and not self.play_video_max_speed:
            self.pause_video_button.setChecked(True)
        if self.play_video_slow_speed_button.isChecked():
            self.play_video_slow_speed_button.setChecked(False)
        if self.play_video_medium_speed_button.isChecked():
            self.play_video_medium_speed_button.setChecked(False)
        if self.play_video_max_speed_button.isChecked():
            self.play_video_max_speed_button.setChecked(False)
        self.trigger_pause_video()
    def check_play_video_slow_speed_button(self):
        if not self.play_video_slow_speed:
            if self.pause_video_button.isChecked():
                self.pause_video_button.setChecked(False)
            if self.play_video_medium_speed:
                self.play_video_medium_speed = False
                self.play_video_medium_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.play_video_max_speed:
                self.play_video_max_speed = False
                self.play_video_max_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.video_playback_thread is None:
                self.video_playback_thread = TimerThread(sleep_time = 0.1)
                self.video_playback_thread.start()
            self.video_playback_thread.time_signal.connect(self.trigger_play_video_slow_speed)
            self.play_video_slow_speed = True
        else:
            self.play_video_slow_speed = False
            self.pause_video_button.setChecked(True)
            self.trigger_pause_video()
    def check_play_video_medium_speed_button(self):
        if not self.play_video_medium_speed:
            if self.pause_video_button.isChecked():
                self.pause_video_button.setChecked(False)
            if self.play_video_slow_speed:
                self.play_video_slow_speed = False
                self.play_video_slow_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.play_video_max_speed:
                self.play_video_max_speed = False
                self.play_video_max_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.video_playback_thread is None:
                self.video_playback_thread = TimerThread(sleep_time = 0.1)
                self.video_playback_thread.start()
            self.video_playback_thread.time_signal.connect(self.trigger_play_video_medium_speed)
            self.play_video_medium_speed = True
        else:
            self.play_video_medium_speed = False
            self.pause_video_button.setChecked(True)
            self.trigger_pause_video()
    def check_play_video_max_speed_button(self):
        if not self.play_video_max_speed:
            if self.pause_video_button.isChecked():
                self.pause_video_button.setChecked(False)
            if self.play_video_slow_speed:
                self.play_video_slow_speed = False
                self.play_video_slow_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.play_video_medium_speed:
                self.play_video_medium_speed = False
                self.play_video_medium_speed_button.setChecked(False)
                if self.video_playback_thread is not None:
                    self.video_playback_thread.close()
                    self.video_playback_thread.wait()
                    self.video_playback_thread = None
            if self.video_playback_thread is None:
                self.video_playback_thread = TimerThread(sleep_time = 0.1)
                self.video_playback_thread.start()
            self.video_playback_thread.time_signal.connect(self.trigger_play_video_max_speed)
            self.play_video_max_speed = True
        else:
            self.play_video_max_speed = False
            self.pause_video_button.setChecked(True)
            self.trigger_pause_video()
    def check_video_time_textbox(self):
        try:
            time = float(self.video_time_textbox.text())
            if time > self.video_n_frames / self.video_fps:
                self.frame_number = self.video_n_frames
            else:
                if time > 0:
                    self.frame_number = int(time * self.video_fps)
                else:
                    self.frame_number = 1
        except:
            pass
        self.trigger_update_preview()

    # Defining Event Functions
    def event_preview_frame_window_label_mouse_clicked(self, event):
        self.initial_mouse_position = (event.x(), event.y())
        if self.magnify_frame:
            if qApp.mouseButtons() & Qt.LeftButton:
                self.trigger_update_preview(magnify = True)
            else:
                if self.preview_frame_window_label_size[0] > 100 and self.preview_frame_window_label_size[1] > 100:
                    self.trigger_update_preview(demagnify = True)
            if self.preview_frame_window_label_size[0] > self.preview_frame_window_size[0]:
                current_midpoint_x = (self.preview_frame_window.horizontalScrollBar().pageStep() / 2) + self.preview_frame_window.horizontalScrollBar().value()
                new_x = self.initial_mouse_position[0] - current_midpoint_x + self.preview_frame_window.horizontalScrollBar().value()
                self.preview_frame_window.horizontalScrollBar().setValue(new_x)
            if self.preview_frame_window_label_size[1] > self.preview_frame_window_size[1]:
                current_midpoint_y = (self.preview_frame_window.verticalScrollBar().pageStep() / 2) + self.preview_frame_window.verticalScrollBar().value()
                new_y = self.initial_mouse_position[1] - current_midpoint_y + self.preview_frame_window.verticalScrollBar().value()
                self.preview_frame_window.verticalScrollBar().setValue(new_y)
        event.accept()
    def event_preview_frame_window_label_mouse_moved(self, event):
        if self.pan_frame:
            if qApp.mouseButtons() & Qt.LeftButton:
                new_frame_pos = (event.x() - self.initial_mouse_position[0], event.y() - self.initial_mouse_position[1])
                if self.preview_frame is not None:
                    if self.preview_frame_window_label_size[0] > self.preview_frame_window_size[0]:
                        self.preview_frame_window.horizontalScrollBar().setValue(self.preview_frame_window.horizontalScrollBar().value() - new_frame_pos[0])
                    if self.preview_frame_window_label_size[1] > self.preview_frame_window_size[1]:
                        self.preview_frame_window.verticalScrollBar().setValue(self.preview_frame_window.verticalScrollBar().value() - new_frame_pos[1])
        event.accept()

class DataPlot(QMainWindow):

    def __init__(self):
        super(DataPlot, self).__init__()
        self.initUI()

    def initUI(self):
        self.data_plots = QWidget()
        self.setCentralWidget(self.data_plots)
        layout = QVBoxLayout(self.data_plots)

        self.tail_angle_plot = FigureCanvas(Figure(figsize=(9, 5)))
        self.tail_angle_plot_toolbar = NavigationToolbar(self.tail_angle_plot, self.tail_angle_plot)
        layout.addWidget(self.tail_angle_plot)

        self.heading_angle_plot = FigureCanvas(Figure(figsize=(9, 5)))
        self.heading_angle_plot_toolbar = NavigationToolbar(self.heading_angle_plot, self.heading_angle_plot)
        layout.addWidget(self.heading_angle_plot)

        self.eye_angles_plot = FigureCanvas(Figure(figsize=(9, 5)))
        self.eye_angles_plot_toolbar = NavigationToolbar(self.eye_angles_plot, self.eye_angles_plot)
        layout.addWidget(self.eye_angles_plot)
    def initialize_class_variables(self, data):
        self.heading_angle_array = data['heading_angle_array']
        self.tail_coord_array = data['tail_coord_array']
        self.body_coord_array = data['body_coord_array']
        self.eye_angle_array = data['eye_angle_array']
        self.video_n_frames = data['video_n_frames']
        self.video_fps = data['video_fps']
        self.colours = data['colours']
        self.colours = [[self.colours[i][2]/255, self.colours[i][1]/255, self.colours[i][0]/255] for i in range(len(self.colours))]
        self.dist_tail_points = data['dist_tail_points']
        self.dist_eyes = data['dist_eyes']
        self.dist_swim_bladder = data['dist_swim_bladder']
        self.eyes_threshold = data['eyes_threshold']
        self.pixel_threshold = data['pixel_threshold']
        self.frame_change_threshold = data['frame_change_threshold']

    def calculate_variables(self):
        self.smoothing_factor = 3

        self.body_tail_angles = [np.arctan2(self.tail_coord_array[j][0][0] - self.body_coord_array[j][0], self.tail_coord_array[j][0][1] - self.body_coord_array[j][1]) for j in range(len(self.tail_coord_array))]
        self.new_tail_coords = [[[self.tail_coord_array[j][i][0] - self.body_coord_array[j][0], self.tail_coord_array[j][i][1] - self.body_coord_array[j][1]] for i in range(len(self.tail_coord_array[0]))] for j in range(len(self.tail_coord_array))]
        self.new_tail_coords = [[[self.new_tail_coords[j][i][0] * np.cos(self.body_tail_angles[j]) - self.new_tail_coords[j][i][1] * np.sin(self.body_tail_angles[j]), self.new_tail_coords[j][i][0] * np.sin(self.body_tail_angles[j]) + self.new_tail_coords[j][i][1] * np.cos(self.body_tail_angles[j])] for i in range(len(self.new_tail_coords[0]))] for j in range(len(self.new_tail_coords))]
        self.tail_angles = [[np.arctan2(self.new_tail_coords[j][i + 1][0] - self.new_tail_coords[j][i][0], self.new_tail_coords[j][i + 1][1] - self.new_tail_coords[j][i][1]) for i in range(len(self.new_tail_coords[0]) - 1)] for j in range(len(self.new_tail_coords))]
        self.tail_angles = [np.array([self.tail_angles[i][j] for i in range(len(self.tail_angles))]) for j in range(len(self.tail_angles[0]))]
        for i in range(1, len(self.tail_angles)):
            for j in range(len(self.tail_angles[i])):
                if self.tail_angles[i][j] - self.tail_angles[i - 1][j] > np.pi:
                    self.tail_angles[i][j] -= np.pi * 2
                elif self.tail_angles[i][j] - self.tail_angles[i - 1][j] < -np.pi:
                    self.tail_angles[i][j] += np.pi * 2

        self.sum_tail_angles = [np.sum([abs(self.tail_angles[i][j]) for i in range(len(self.tail_angles))]) for j in range(len(self.tail_angles[0]))]
        self.tail_angle_frames = np.where([self.sum_tail_angles[i] == self.sum_tail_angles[i + 1] == self.sum_tail_angles[i + 2] for i in range(len(self.sum_tail_angles) - 2)])[0]
        self.tail_angle_frames = np.where([self.sum_tail_angles[i] == self.sum_tail_angles[i + 1] for i in range(len(self.sum_tail_angles) - 1)])[0]

        # for i in range(1, len(self.tail_angle_frames)):
        #     if self.tail_angle_frames[i] - self.tail_angle_frames[i - 1] == 2:
        #         self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 1)
        #     elif self.tail_angle_frames[i] - self.tail_angle_frames[i - 1] == 3:
        #         self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 1)
        #         self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 2)

        # for i in range(len(self.tail_angles)):
        #     for j in self.tail_angle_frames:
        #         self.tail_angles[i][j] = 0.0
        self.smoothed_tail_angles = [np.convolve(self.tail_angles[i], np.ones(self.smoothing_factor)/self.smoothing_factor, mode = 'same') for i in range(len(self.tail_angles))]

        if np.isnan(self.heading_angle_array[0]):
            j = 0
            while np.isnan(self.heading_angle_array[0]):
                if not np.isnan(self.heading_angle_array[j]):
                    self.heading_angle_array[0] = self.heading_angle_array[j]
                j += 1

        self.heading_angles = np.array([self.heading_angle_array[i] - self.heading_angle_array[0] for i in range(len(self.heading_angle_array))])

        # i = 0
        # for j in range(len(self.heading_angles)):
        #     if j not in self.tail_angle_frames:
        #         i = j
        #     else:
        #         self.heading_angles[j] = self.heading_angles[i]

        for i in range(1, len(self.heading_angles)):
            if self.heading_angles[i] - self.heading_angles[i - 1] > np.pi:
                self.heading_angles[i:] -= np.pi * 2
            elif self.heading_angles[i] - self.heading_angles[i - 1] < -np.pi:
                self.heading_angles[i:] += np.pi * 2

        self.smoothed_heading_angles = np.convolve(self.heading_angles, np.ones(self.smoothing_factor)/self.smoothing_factor, mode = 'same')

        self.eye_angles = [[self.eye_angle_array[i][j] - self.heading_angle_array[i] for i in range(len(self.eye_angle_array))] for j in range(len(self.eye_angle_array[0]))]

        # i = 0
        # for k in range(len(self.eye_angles)):
        #     for j in range(len(self.eye_angles[k])):
        #         if j not in self.tail_angle_frames:
        #             i = j
        #         else:
        #             self.eye_angles[k][j] = self.eye_angles[k][i]

        # self.eye_angles = [[self.eye_angles[i][j] - np.pi * 2 if self.eye_angles[i][j] - self.eye_angles[i][j - 1] > np.pi else self.eye_angles[i][j] + np.pi * 2 if self.eye_angles[i][j] - self.eye_angles[i][j - 1] < -np.pi else self.eye_angles[i][j] for j in range(len(self.eye_angles[i]))] for i in range(len(self.eye_angles))]
        for i in range(1, len(self.eye_angles)):
            for j in range(len(self.eye_angles[i])):
                if self.eye_angles[i][j] - self.eye_angles[i - 1][j] > np.pi:
                    self.eye_angles[i][j] -= np.pi * 2
                elif self.eye_angles[i][j] - self.eye_angles[i - 1][j] < -np.pi:
                    self.eye_angles[i][j] += np.pi * 2

        self.smoothed_eye_angles = [np.convolve(self.eye_angles[i], np.ones(self.smoothing_factor)/self.smoothing_factor, mode = 'same') for i in range(len(self.eye_angles))]

        self.timepoints = np.linspace(0, self.video_n_frames / self.video_fps, self.video_n_frames)

    def update_plots(self, clear = False):

        if not clear:
            self.tail_angle_plot_axis = self.tail_angle_plot.figure.subplots()
            [self.tail_angle_plot_axis.plot(self.timepoints, self.smoothed_tail_angles[i], color = self.colours[i], lw = 1) for i in range(len(self.smoothed_tail_angles))]
            self.tail_angle_plot_axis.set_xlabel('Time (s)')
            self.tail_angle_plot_axis.set_ylabel('Angle (radians)')
            self.tail_angle_plot_axis.set_title('Tail Kinematics Over Time')

            self.heading_angle_plot_axis = self.heading_angle_plot.figure.subplots()
            self.heading_angle_plot_axis.plot(self.timepoints, self.smoothed_heading_angles, color = self.colours[-1], lw = 1)
            self.heading_angle_plot_axis.set_xlabel('Time (s)')
            self.heading_angle_plot_axis.set_ylabel('Angle (radians)')
            self.heading_angle_plot_axis.set_title('Heading Angle Over Time')

            self.eye_angles_plot_axis = self.eye_angles_plot.figure.subplots()
            [self.eye_angles_plot_axis.plot(self.timepoints, self.smoothed_eye_angles[i], color = self.colours[i - 3], lw = 1) for i in range(len(self.smoothed_eye_angles))]
            self.eye_angles_plot_axis.set_xlabel('Time (s)')
            self.eye_angles_plot_axis.set_ylabel('Angle (radians)')
            self.eye_angles_plot_axis.set_title('Eye Angles Over Time')

        else:
            self.tail_angle_plot_axis.cla()
            self.heading_angle_plot_axis.cla()
            self.eye_angles_plot_axis.cla()
