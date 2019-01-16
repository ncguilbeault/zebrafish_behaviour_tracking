'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import os
import cv2
import numpy as np
import utilities as ut
import matplotlib.cm as cm
from functools import partial
from track_video_thread import TrackVideoProgressWindow
from track_all_videos_thread import TrackAllVideosProgressWindow
from background_calculation_thread import CalculateBackgroundProgressWindow
from timer_thread import TimerThread
import yaml

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TrackingWindow(QScrollArea):

    def __init__(self, main_window_width, main_window_height):
        super(TrackingWindow, self).__init__()
        self.main_window_width = main_window_width
        self.main_window_height = main_window_height
        self.tracking_content = TrackingContent(self.main_window_width, self.main_window_height)
        self.setWidget(self.tracking_content)
        self.setFrameStyle(QFrame.NoFrame)

class TrackingContent(QMainWindow):

    # Defining Initialization Functions
    def __init__(self, main_window_width, main_window_height):
        super(TrackingContent, self).__init__()
        self.main_window_width = main_window_width
        self.main_window_height = main_window_height
        self.initUI()
    def initUI(self):
        self.initialize_layout()
        self.initialize_class_variables()
        self.add_preview_frame_window()
        self.add_loaded_videos_window()
        self.add_loaded_videos_listbox_to_window()
        self.add_loaded_videos_buttons()
        self.add_descriptors_window()
        self.add_descriptors_to_window()
        self.add_frame_window_slider()
        self.add_preview_frame_number_textbox()
        self.add_video_playback_buttons()
        self.add_frame_change_buttons()
        self.add_interactive_frame_buttons()
        self.add_preview_parameters_window()
        self.add_preview_parameters_to_window()
        self.add_tracking_parameters_window()
        self.add_tracking_parameters_to_window()
        self.add_tracking_parameters_buttons()
        self.add_colour_parameters_window()
        self.add_colour_parameters_to_window()
        self.add_colour_parameters_buttons()
        self.add_video_time_textbox()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.resize(self.tracking_content_size[0], self.tracking_content_size[1])
    def initialize_layout(self):
        self.font_title = QFont()
        self.font_text = QFont()
        self.font_colour_parameters = QFont()
        self.font_loaded_videos_buttons = QFont()
        self.font_loaded_videos_buttons_2 = QFont()

        if self.main_window_width == 1920 and self.main_window_height == 1020:
            self.font_title.setPointSize(14)
            self.font_text.setPointSize(8)
            self.font_colour_parameters.setPointSize(7)
            self.font_loaded_videos_buttons.setPointSize(7)
            self.font_loaded_videos_buttons_2.setPointSize(6)
            self.tracking_content_size = (1910, 920)
            self.main_window_x_offset = 10
            self.main_window_y_offset = 15
            self.main_window_spacing = 10
            self.preview_frame_window_size = (800, 800)
            self.preview_frame_window_x_offset = 30
            self.preview_frame_window_y_offset = 30
            self.preview_frame_window_label_size = (self.preview_frame_window_size[0] - self.preview_frame_window_x_offset, self.preview_frame_window_size[1] - self.preview_frame_window_y_offset)
            self.loaded_videos_window_size = (845, 490)
            self.loaded_videos_x_offset = 20
            self.loaded_videos_y_offset = 70
            self.loaded_videos_y_spacing = 10
            self.loaded_videos_x_spacing = 12.5
            self.loaded_videos_listbox_size = (805, 220)
            self.loaded_videos_button_size = (260, 50)
            self.loaded_videos_button_size_2 = (396.25, 50)
            self.loaded_videos_button_size_3 = (191.875, 50)
            self.descriptors_window_size = (845, 400)
            self.descriptors_x_offset = 10
            self.descriptors_y_offset = 75
            self.descriptors_height = 30
            self.descriptors_y_spacing = 10
            self.status_window_size = (845, 390)
            self.statuses_x_offset = 20
            self.statuses_y_offset = 75
            self.status_bars_height = 30
            self.statuses_button_size = (400, 50)
            self.statuses_y_spacing = 10
            self.statuses_x_spacing = 10
            self.status_buttons_y_spacing = 10
            self.preview_frame_window_slider_height = 20
            self.preview_frame_number_textbox_y_spacing = 10
            self.preview_frame_number_textbox_label_size = (160, 25)
            self.preview_frame_number_textbox_size = (120, 25)
            self.video_time_textbox_y_spacing = 10
            self.video_time_textbox_label_size = (160, 25)
            self.video_time_textbox_size = (120, 25)
            self.frame_change_button_size = (50, 50)
            self.frame_change_button_x_offset = 10
            self.frame_change_button_x_spacing = 5
            self.frame_change_button_icon_size = (60, 60)
            self.interactive_frame_button_size = (50, 50)
            self.interactive_frame_button_icon_size = (45, 45)
            self.interactive_frame_button_x_offset = 10
            self.interactive_frame_button_x_spacing = 5
            self.crop_frame_button_x_spacing = 3
            self.crop_frame_button_size = (30, 30)
            self.crop_frame_button_icon_size = (25, 25)
            self.video_playback_button_size = (50, 50)
            self.video_playback_button_x_offset = 10
            self.video_playback_button_x_spacing = 5
            self.video_playback_button_icon_size = (60, 60)
            self.preview_parameters_window_size = (450, 330)
            self.preview_parameters_x_offset = 10
            self.preview_parameters_y_offset = 75
            self.preview_parameters_height = 28
            self.preview_parameters_x_spacing = 20
            self.preview_parameters_y_spacing = 5
            self.preview_parameters_checkbox_size = (15, 15)
            self.tracking_parameters_window_size = (600, 900)
            self.tracking_parameters_label_width = 420
            self.tracking_parameters_x_offset = 10
            self.tracking_parameters_y_offset = 70
            self.tracking_parameters_height = 22
            self.tracking_parameters_box_width = 100
            self.tracking_parameters_y_spacing = 17
            self.tracking_parameters_button_size = (500, 50)
            self.colour_parameters_window_size = (995, 330)
            self.colour_parameters_button_size = (220, 60)
            self.colour_parameters_x_offset = 0
            self.colour_parameters_y_offset = 80
            self.colour_parameters_height = 30
            self.colour_parameters_label_width = 130
            self.colour_parameters_textbox_width = 0
            self.colour_parameters_icon_size = (18, 18)
            self.colour_parameters_width = 200
            self.colour_parameters_x_spacing = 20
            self.colour_parameters_y_spacing = 10
            self.colour_parameters_button_y_spacing = 20
            self.colour_select_button_x_spacing = 0
            self.colour_parameters_button_x_offset = 10
        else:
            self.font_title.setPointSize(18)
            self.font_text.setPointSize(10)
            self.font_colour_parameters.setPointSize(10)
            self.font_loaded_videos_buttons.setPointSize(10)
            self.font_loaded_videos_buttons_2.setPointSize(10)
            self.tracking_content_size = (2550, 1320)
            self.main_window_x_offset = 10
            self.main_window_y_offset = 10
            self.main_window_spacing = 10
            self.preview_frame_window_size = (1000, 1000)
            self.preview_frame_window_x_offset = 30
            self.preview_frame_window_y_offset = 30
            self.preview_frame_window_label_size = (self.preview_frame_window_size[0] - self.preview_frame_window_x_offset, self.preview_frame_window_size[1] - self.preview_frame_window_y_offset)
            self.loaded_videos_window_size = (1060, 540)
            self.loaded_videos_x_offset = 20
            self.loaded_videos_y_offset = 60
            self.loaded_videos_y_spacing = 10
            self.loaded_videos_x_spacing = 10
            self.loaded_videos_listbox_size = (1020, 290)
            self.loaded_videos_button_size = (333.33, 50)
            self.loaded_videos_button_size_2 = (505, 50)
            self.loaded_videos_button_size_3 = (247.5, 50)
            self.descriptors_window_size = (1060, 450)
            self.descriptors_x_offset = 10
            self.descriptors_y_offset = 60
            self.descriptors_height = 30
            self.descriptors_y_spacing = 10
            self.status_window_size = (845, 390)
            self.statuses_x_offset = 20
            self.statuses_y_offset = 75
            self.status_bars_height = 30
            self.statuses_button_size = (400, 50)
            self.statuses_y_spacing = 10
            self.statuses_x_spacing = 10
            self.status_buttons_y_spacing = 10
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
            self.crop_frame_button_x_spacing = 3
            self.crop_frame_button_size = (30, 30)
            self.crop_frame_button_icon_size = (25, 25)
            self.video_playback_button_size = (50, 50)
            self.video_playback_button_x_offset = 10
            self.video_playback_button_x_spacing = 5
            self.video_playback_button_icon_size = (60, 60)
            self.preview_parameters_window_size = (400, 295)
            self.preview_parameters_x_offset = 10
            self.preview_parameters_y_offset = 60
            self.preview_parameters_height = 18
            self.preview_parameters_x_spacing = 5
            self.preview_parameters_y_spacing = 5
            self.preview_parameters_checkbox_size = (15, 15)
            self.tracking_parameters_window_size = (450, 1000)
            self.tracking_parameters_label_width = 280
            self.tracking_parameters_x_offset = 10
            self.tracking_parameters_y_offset = 50
            self.tracking_parameters_height = 22
            self.tracking_parameters_box_width = 100
            self.tracking_parameters_y_spacing = 17
            self.tracking_parameters_button_size = (400, 80)
            self.colour_parameters_window_size = (1110, 295)
            self.colour_parameters_button_size = (300, 60)
            self.colour_parameters_x_offset = 20
            self.colour_parameters_y_offset = 60
            self.colour_parameters_height = 20
            self.colour_parameters_label_width = 100
            self.colour_parameters_textbox_width = 100
            self.colour_parameters_icon_size = (18, 18)
            self.colour_parameters_width = 220
            self.colour_parameters_x_spacing = 50
            self.colour_parameters_y_spacing = 18
            self.colour_parameters_button_y_spacing = 15
            self.colour_select_button_x_spacing = 5
            self.colour_parameters_button_x_offset = 10
    def initialize_class_variables(self):
        self.video_path = None
        self.video_path_basename = None
        self.video_path_folder = None
        self.video_n_frames = 0
        self.video_fps = 0
        self.video_frame_width = 0
        self.video_frame_height = 0
        self.frame_number = 1
        self.background = None
        self.background_path = None
        self.background_path_basename = None
        self.save_path = None
        self.preview_background = False
        self.preview_background_subtracted_frame = False
        self.preview_tracking_results = False
        self.preview_eyes_threshold = False
        self.tracking_method = None
        self.n_tail_points = 0
        self.dist_tail_points = 0
        self.dist_eyes = 0
        self.dist_swim_bladder = 0
        self.starting_frame = 0
        self.n_frames = None
        self.heading_line_length = 0
        self.pixel_threshold = 0
        self.frame_change_threshold = 0
        self.eyes_threshold = 0
        self.eyes_line_length = 0
        self.preview_frame = None
        self.colours = []
        self.save_video = False
        self.extended_eyes_calculation = False
        self.track_video_thread = None
        self.calculate_background_thread = None
        self.previous_preview_frame_window_horizontal_scroll_bar_max = None
        self.previous_preview_frame_window_vertical_scroll_bar_max = None
        self.magnify_frame = False
        self.pan_frame = False
        self.elliptical_crop_frame = False
        self.rectangular_crop_frame = False
        self.pan_crop = False
        self.mask = None
        self.play_video_slow_speed = False
        self.play_video_medium_speed = False
        self.play_video_max_speed = False
        self.video_playback_thread = None
        self.median_blur = 0
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = 0
        self.background_calculation_frame_chunk_height = 0
        self.background_calculation_frames_to_skip = 0
        self.initial_pixel_search = None
        self.invert_threshold = None
        self.range_angles = None
        self.loaded_videos_and_parameters_dict = {}
        self.tracking_parameters_dict = {}
        self.descriptors_dict = {}
        self.track_all_videos_progress_window = None
        self.track_video_progress_window = None
        self.calculate_background_progress_window = None
        self.save_background = None

    # Defining Get Functions
    def get_video_attributes(self):
        self.video_path_folder = os.path.dirname(self.video_path)
        self.video_path_basename = os.path.basename(self.video_path)
        self.video_n_frames = ut.get_total_frame_number_from_video(self.video_path)
        self.video_fps = ut.get_fps_from_video(self.video_path)
        self.video_frame_width, self.video_frame_height = ut.get_frame_size_from_video(self.video_path)
    def get_background_attributes(self):
        self.background_path_basename = os.path.basename(self.background_path)
        self.background_height, self.background_width = self.background.shape

    # Defining Add Functions
    def add_preview_frame_window(self):
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height

        self.preview_frame_window = QScrollArea(self)
        self.preview_frame_window.setFrameShape(QFrame.StyledPanel)
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
        self.preview_frame_window.wheelEvent = self.event_preview_frame_window_wheel_scrolled
        self.preview_frame_window.setWidget(self.preview_frame_window_label)
    def add_loaded_videos_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height
        new_width = (self.loaded_videos_window_size[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_window_size[1] / 1400) * self.main_window_height

        self.loaded_videos_window = QLabel(self)
        self.loaded_videos_window.setFrameShape(QFrame.StyledPanel)
        self.loaded_videos_window.move(new_x, new_y)
        self.loaded_videos_window.resize(new_width, new_height)
        self.loaded_videos_window.setText('Loaded Videos')
        self.loaded_videos_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.loaded_videos_window.setFont(self.font_title)
    def add_loaded_videos_listbox_to_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_y_offset) / 1400) * self.main_window_height
        new_width = (self.loaded_videos_listbox_size[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_listbox_size[1] / 1400) * self.main_window_height

        self.loaded_videos_listbox = QListWidget(self)
        self.loaded_videos_listbox.setFrameShape(QFrame.StyledPanel)
        self.loaded_videos_listbox.move(new_x, new_y)
        self.loaded_videos_listbox.resize(new_width, new_height)
        self.setStyleSheet( """QListWidget{background-color: rgb(240, 240, 240);}""")
        self.loaded_videos_listbox.itemClicked.connect(self.check_loaded_videos_listbox_item_clicked)
    def add_loaded_videos_buttons(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (0 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_y_offset + self.loaded_videos_listbox_size[1] + (0 * (self.loaded_videos_y_spacing + self.loaded_videos_button_size_3[1])) + self.loaded_videos_y_spacing) / 1400) * self.main_window_height
        new_width = (self.loaded_videos_button_size_3[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_button_size_3[1] / 1400) * self.main_window_height

        self.add_video_button = QPushButton('Add Video', self)
        self.add_video_button.move(new_x, new_y)
        self.add_video_button.resize(new_width, new_height)
        self.add_video_button.setFont(self.font_loaded_videos_buttons_2)
        self.add_video_button.clicked.connect(self.check_add_video_button)

        self.add_videos_from_folder_button = QPushButton('Add Videos from Folder', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (1 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.add_videos_from_folder_button.move(new_x, new_y)
        self.add_videos_from_folder_button.resize(new_width, new_height)
        self.add_videos_from_folder_button.setFont(self.font_loaded_videos_buttons_2)
        self.add_videos_from_folder_button.clicked.connect(self.check_add_videos_from_folder_button)

        self.remove_selected_video_button = QPushButton('Remove Selected Video', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (2 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.remove_selected_video_button.move(new_x, new_y)
        self.remove_selected_video_button.resize(new_width, new_height)
        self.remove_selected_video_button.setFont(self.font_loaded_videos_buttons_2)
        self.remove_selected_video_button.clicked.connect(self.check_remove_selected_video_button)

        self.remove_all_videos_button = QPushButton('Remove All Videos', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (3 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.remove_all_videos_button.move(new_x, new_y)
        self.remove_all_videos_button.resize(new_width, new_height)
        self.remove_all_videos_button.setFont(self.font_loaded_videos_buttons_2)
        self.remove_all_videos_button.clicked.connect(self.check_remove_all_videos_button)

        new_width = (self.loaded_videos_button_size_3[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_button_size_3[1] / 1400) * self.main_window_height

        self.load_background_button = QPushButton('Load Background', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (0 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_y_offset + self.loaded_videos_listbox_size[1] + (1 * (self.loaded_videos_y_spacing + self.loaded_videos_button_size_3[1])) + self.loaded_videos_y_spacing) / 1400) * self.main_window_height
        self.load_background_button.move(new_x, new_y)
        self.load_background_button.resize(new_width, new_height)
        self.load_background_button.setFont(self.font_loaded_videos_buttons)
        self.load_background_button.clicked.connect(self.trigger_load_background)

        self.calculate_background_button = QPushButton('Calculate Background', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (1 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.calculate_background_button.move(new_x, new_y)
        self.calculate_background_button.resize(new_width, new_height)
        self.calculate_background_button.setFont(self.font_loaded_videos_buttons)
        self.calculate_background_button.clicked.connect(self.trigger_calculate_background)

        self.update_parameters_button = QPushButton('Update Parameters', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (2 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.update_parameters_button.move(new_x, new_y)
        self.update_parameters_button.resize(new_width, new_height)
        self.update_parameters_button.setFont(self.font_loaded_videos_buttons)
        self.update_parameters_button.clicked.connect(self.check_update_parameters_button)

        self.reload_parameters_button = QPushButton('Reload Parameters', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (3 * (self.loaded_videos_button_size_3[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.reload_parameters_button.move(new_x, new_y)
        self.reload_parameters_button.resize(new_width, new_height)
        self.reload_parameters_button.setFont(self.font_loaded_videos_buttons)
        self.reload_parameters_button.clicked.connect(self.check_reload_parameters_button)

        new_width = (self.loaded_videos_button_size_2[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_button_size_2[1] / 1400) * self.main_window_height

        self.track_selected_video_button = QPushButton('Track Selected Video', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (0 * (self.loaded_videos_button_size_2[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_y_offset + self.loaded_videos_listbox_size[1] + (2 * (self.loaded_videos_y_spacing + self.loaded_videos_button_size_2[1])) + self.loaded_videos_y_spacing) / 1400) * self.main_window_height
        self.track_selected_video_button.move(new_x, new_y)
        self.track_selected_video_button.resize(new_width, new_height)
        self.track_selected_video_button.setFont(self.font_loaded_videos_buttons)
        self.track_selected_video_button.clicked.connect(self.check_track_selected_video_button)

        self.track_all_videos_button = QPushButton('Track All Videos', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (1 * (self.loaded_videos_button_size_2[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.track_all_videos_button.move(new_x, new_y)
        self.track_all_videos_button.resize(new_width, new_height)
        self.track_all_videos_button.setFont(self.font_loaded_videos_buttons)
        self.track_all_videos_button.clicked.connect(self.check_track_all_videos_button)

        self.update_loaded_videos_buttons(inactivate = True)
    def add_descriptors_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing) / 1400) * self.main_window_height
        new_width = (self.descriptors_window_size[0] / 2560) * self.main_window_width
        new_height = (self.descriptors_window_size[1] / 1400) * self.main_window_height

        self.descriptors_window = QLabel(self)
        self.descriptors_window.setFrameShape(QFrame.StyledPanel)
        # self.descriptors_window.setFrameShadow(QFrame.Sunken)
        # self.descriptors_window.setLineWidth(5)
        self.descriptors_window.move(new_x, new_y)
        self.descriptors_window.resize(new_width, new_height)
        self.descriptors_window.setText('Descriptors')
        self.descriptors_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.descriptors_window.setFont(self.font_title)
    def add_descriptors_to_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.descriptors_x_offset) / 2560) * self.main_window_width
        new_width = ((self.descriptors_window_size[0] - (2 * self.descriptors_x_offset)) / 2560) * self.main_window_width
        new_height = (self.descriptors_height / 1400) * self.main_window_height

        self.video_path_basename_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (0 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.video_path_basename_descriptor.move(new_x, new_y)
        self.video_path_basename_descriptor.resize(new_width, new_height)
        self.video_path_basename_descriptor.setText('Video Filename: {0}'.format(self.video_path_basename))
        self.video_path_basename_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.video_path_basename_descriptor.setFont(self.font_text)

        self.video_path_folder_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (1 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.video_path_folder_descriptor.move(new_x, new_y)
        self.video_path_folder_descriptor.resize(new_width, new_height)
        self.video_path_folder_descriptor.setText('Video Folder: {0}'.format(self.video_path_folder))
        self.video_path_folder_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.video_path_folder_descriptor.setFont(self.font_text)

        self.video_n_frames_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (2 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.video_n_frames_descriptor.move(new_x, new_y)
        self.video_n_frames_descriptor.resize(new_width, new_height)
        self.video_n_frames_descriptor.setText('Video Total Frames: {0}'.format(self.video_n_frames))
        self.video_n_frames_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.video_n_frames_descriptor.setFont(self.font_text)

        self.video_fps_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (3 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.video_fps_descriptor.move(new_x, new_y)
        self.video_fps_descriptor.resize(new_width, new_height)
        self.video_fps_descriptor.setText('Video FPS: {0}'.format(self.video_fps))
        self.video_fps_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.video_fps_descriptor.setFont(self.font_text)

        self.frame_width_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (4 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.frame_width_descriptor.move(new_x, new_y)
        self.frame_width_descriptor.resize(new_width, new_height)
        self.frame_width_descriptor.setText('Frame Width: {0}'.format(self.video_frame_width))
        self.frame_width_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.frame_width_descriptor.setFont(self.font_text)

        self.frame_height_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (5 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.frame_height_descriptor.move(new_x, new_y)
        self.frame_height_descriptor.resize(new_width, new_height)
        self.frame_height_descriptor.setText('Frame Height: {0}'.format(self.video_frame_height))
        self.frame_height_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.frame_height_descriptor.setFont(self.font_text)

        self.background_path_basename_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (6 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.background_path_basename_descriptor.move(new_x, new_y)
        self.background_path_basename_descriptor.resize(new_width, new_height)
        self.background_path_basename_descriptor.setText('Background Filename: {0}'.format(self.background_path_basename))
        self.background_path_basename_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.background_path_basename_descriptor.setFont(self.font_text)

        self.save_path_descriptor = QLabel(self)
        new_y = ((self.main_window_y_offset + self.loaded_videos_window_size[1] + self.main_window_spacing + self.descriptors_y_offset + (7 * (self.descriptors_height + self.descriptors_y_spacing))) / 1400) * self.main_window_height
        self.save_path_descriptor.move(new_x, new_y)
        self.save_path_descriptor.resize(new_width, new_height)
        self.save_path_descriptor.setText('Save Path: {0}'.format(self.save_path))
        self.save_path_descriptor.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.save_path_descriptor.setFont(self.font_text)
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

        # new_icon_width = ((self.crop_frame_button_size[0] / 2560) * self.main_window_width) - (self.crop_frame_button_size[0] - self.crop_frame_button_icon_size[0])
        # new_icon_height = ((self.crop_frame_button_size[1] / 1400) * self.main_window_height) - (self.crop_frame_button_size[1] - self.crop_frame_button_icon_size[1])
        # new_width = (self.crop_frame_button_size[0] / 2560) * self.main_window_width
        # new_height = (self.crop_frame_button_size[1] / 1400) * self.main_window_height

        self.elliptical_crop_frame_button = QPushButton(self)
        self.elliptical_crop_frame_button.setIcon(QIcon('icons\\button_icon_14.png'))
        self.elliptical_crop_frame_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (5 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]) + self.frame_change_button_size[0]) + self.interactive_frame_button_x_offset + (2 * (self.interactive_frame_button_x_spacing + self.interactive_frame_button_size[0]))) / 2560) * self.main_window_width
        self.elliptical_crop_frame_button.move(new_x, new_y)
        self.elliptical_crop_frame_button.resize(new_width, new_height)
        self.elliptical_crop_frame_button.clicked.connect(self.check_elliptical_crop_frame_button)
        self.elliptical_crop_frame_button.setCheckable(True)

        self.rectangular_crop_frame_button = QPushButton(self)
        self.rectangular_crop_frame_button.setIcon(QIcon('icons\\button_icon_15.png'))
        self.rectangular_crop_frame_button.setIconSize(QSize(new_icon_width, new_icon_height))
        new_x = ((self.main_window_x_offset + self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0] + self.video_playback_button_x_offset + (3 * (self.video_playback_button_x_spacing + self.video_playback_button_size[0]) + self.video_playback_button_size[0]) + self.frame_change_button_x_offset + (5 * (self.frame_change_button_x_spacing + self.frame_change_button_size[0]) + self.frame_change_button_size[0]) + self.interactive_frame_button_x_offset + (3 * (self.interactive_frame_button_x_spacing + self.interactive_frame_button_size[0]))) / 2560) * self.main_window_width
        self.rectangular_crop_frame_button.move(new_x, new_y)
        self.rectangular_crop_frame_button.resize(new_width, new_height)
        self.rectangular_crop_frame_button.clicked.connect(self.check_rectangular_crop_frame_button)
        self.rectangular_crop_frame_button.setCheckable(True)

        self.update_interactive_frame_buttons(inactivate = True)
    def add_preview_parameters_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing) / 1400) * self.main_window_height
        new_width = (self.preview_parameters_window_size[0] / 2560) * self.main_window_width
        new_height = (self.preview_parameters_window_size[1] / 1400) * self.main_window_height

        self.preview_parameters_window = QLabel(self)
        self.preview_parameters_window.setFrameShape(QFrame.StyledPanel)
        self.preview_parameters_window.move(new_x, new_y)
        self.preview_parameters_window.resize(new_width, new_height)
        self.preview_parameters_window.setText('Preview Parameters')
        self.preview_parameters_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.preview_parameters_window.setFont(self.font_title)
    def add_preview_parameters_to_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.preview_parameters_x_offset) / 2560) * self.main_window_width
        new_label_width = ((self.preview_parameters_window_size[0] - (2 * self.preview_parameters_x_offset) - self.preview_parameters_checkbox_size[0] - self.preview_parameters_x_spacing) / 2560) * self.main_window_width
        new_label_height = (self.preview_parameters_height / 1400) * self.main_window_height
        new_label_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.preview_parameters_x_offset + self.preview_parameters_checkbox_size[0] + self.preview_parameters_x_spacing) / 2560) * self.main_window_width

        self.preview_background_checkbox = QCheckBox(self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + (0 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_background_checkbox.move(new_x, new_y)
        self.preview_background_checkbox.stateChanged.connect(self.check_preview_background_checkbox)
        self.preview_background_checkbox_label = QLabel(self)
        new_label_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + self.preview_parameters_y_spacing + (0 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_background_checkbox_label.move(new_label_x, new_label_y)
        self.preview_background_checkbox_label.resize(new_label_width, new_label_height)
        self.preview_background_checkbox_label.setText('Preview Background')
        self.preview_background_checkbox_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_background_checkbox_label.setFont(self.font_text)

        self.preview_background_subtracted_frame_checkbox = QCheckBox(self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + (1 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_background_subtracted_frame_checkbox.move(new_x, new_y)
        self.preview_background_subtracted_frame_checkbox.stateChanged.connect(self.check_preview_background_subtracted_frame_checkbox)
        self.preview_background_subtracted_frame_checkbox_label = QLabel(self)
        new_label_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + self.preview_parameters_y_spacing + (1 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_background_subtracted_frame_checkbox_label.move(new_label_x, new_label_y)
        self.preview_background_subtracted_frame_checkbox_label.resize(new_label_width, new_label_height)
        self.preview_background_subtracted_frame_checkbox_label.setText('Preview Background Subtracted Frames')
        self.preview_background_subtracted_frame_checkbox_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_background_subtracted_frame_checkbox_label.setFont(self.font_text)

        self.preview_tracking_results_checkbox = QCheckBox(self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + (2 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_tracking_results_checkbox.move(new_x, new_y)
        self.preview_tracking_results_checkbox.stateChanged.connect(self.check_preview_tracking_results_checkbox)
        self.preview_tracking_results_checkbox_label = QLabel(self)
        new_label_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + self.preview_parameters_y_spacing + (2 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_tracking_results_checkbox_label.move(new_label_x, new_label_y)
        self.preview_tracking_results_checkbox_label.resize(new_label_width, new_label_height)
        self.preview_tracking_results_checkbox_label.setText('Preview Tracking Results')
        self.preview_tracking_results_checkbox_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_tracking_results_checkbox_label.setFont(self.font_text)

        self.preview_eyes_threshold_checkbox = QCheckBox(self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + (3 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_eyes_threshold_checkbox.move(new_x, new_y)
        self.preview_eyes_threshold_checkbox.stateChanged.connect(self.check_preview_eyes_threshold_checkbox)
        self.preview_eyes_threshold_checkbox_label = QLabel(self)
        new_label_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.preview_parameters_y_offset + self.preview_parameters_y_spacing + (3 * 2 * self.preview_parameters_height)) / 1400) * self.main_window_height
        self.preview_eyes_threshold_checkbox_label.move(new_label_x, new_label_y)
        self.preview_eyes_threshold_checkbox_label.resize(new_label_width, new_label_height)
        self.preview_eyes_threshold_checkbox_label.setText('Preview Eyes Threshold')
        self.preview_eyes_threshold_checkbox_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.preview_eyes_threshold_checkbox_label.setFont(self.font_text)
        self.update_preview_parameters(inactivate = True)
    def add_tracking_parameters_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.descriptors_window_size[0]) / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height
        new_width = (self.tracking_parameters_window_size[0] / 2560) * self.main_window_width
        new_height = (self.tracking_parameters_window_size[1] / 1400) * self.main_window_height

        self.tracking_parameters_window = QLabel(self)
        self.tracking_parameters_window.setFrameShape(QFrame.StyledPanel)
        self.tracking_parameters_window.move(new_x, new_y)
        self.tracking_parameters_window.resize(new_width, new_height)
        self.tracking_parameters_window.setText('Tracking Parameters')
        self.tracking_parameters_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.tracking_parameters_window.setFont(self.font_title)

        self.tracking_parameters_scroll_area = QScrollArea(self)
        self.tracking_parameters_scroll_area.setFrameStyle(QFrame.NoFrame)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.descriptors_window_size[0] + self.tracking_parameters_x_offset) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.tracking_parameters_y_offset + (0 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height
        self.tracking_parameters_scroll_area.move(new_x, new_y)
        new_width = ((self.tracking_parameters_window_size[0] - (2 * self.tracking_parameters_x_offset)) / 2560) * self.main_window_width
        new_height = (((self.main_window_y_offset + self.tracking_parameters_y_offset + (13 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + self.tracking_parameters_height) / 1400) * self.main_window_height) - (((self.main_window_y_offset + self.tracking_parameters_y_offset + (0 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height)
        self.tracking_parameters_scroll_area.resize(new_width, new_height)

        new_width = (self.tracking_parameters_window_size[0] - (4 * self.tracking_parameters_x_offset))
        new_height = (self.main_window_y_offset + self.tracking_parameters_y_offset + (13 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + self.tracking_parameters_height)
        self.tracking_parameters_widget = QWidget(self)
        self.tracking_parameters_widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.tracking_parameters_widget.resize(new_width, new_height)
        self.tracking_parameters_scroll_area.setWidget(self.tracking_parameters_widget)
    def add_tracking_parameters_to_window(self):
        self.grid_layout = QGridLayout()
        self.tracking_parameters_widget.setLayout(self.grid_layout)

        self.background_calculation_method_combobox_label = QLabel(self)
        self.background_calculation_method_combobox_label.setText('Background Calculation Method: ')
        self.background_calculation_method_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.background_calculation_method_combobox_label.setFont(self.font_text)
        self.background_calculation_method_combobox = QComboBox(self)
        self.background_calculation_method_combobox.addItem('Brightest')
        self.background_calculation_method_combobox.addItem('Darkest')
        self.background_calculation_method_combobox.addItem('Mode')
        self.background_calculation_method_combobox.setCurrentIndex(0)
        self.background_calculation_method_combobox.currentIndexChanged.connect(self.check_background_calculation_method_combobox)
        self.grid_layout.addWidget(self.background_calculation_method_combobox_label, 1, 1)
        self.grid_layout.addWidget(self.background_calculation_method_combobox, 1, 2)

        self.background_calculation_frame_chunk_width_textbox_label = QLabel(self)
        self.background_calculation_frame_chunk_width_textbox_label.setText('Background Calculation Frame Chunk Width: ')
        self.background_calculation_frame_chunk_width_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.background_calculation_frame_chunk_width_textbox_label.setFont(self.font_text)
        self.background_calculation_frame_chunk_width_textbox = QLineEdit(self)
        self.background_calculation_frame_chunk_width_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_width))
        self.background_calculation_frame_chunk_width_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.background_calculation_frame_chunk_width_textbox.setFont(self.font_text)
        self.background_calculation_frame_chunk_width_textbox.returnPressed.connect(self.check_background_calculation_frame_chunk_width_textbox)
        self.grid_layout.addWidget(self.background_calculation_frame_chunk_width_textbox_label, 2, 1)
        self.grid_layout.addWidget(self.background_calculation_frame_chunk_width_textbox, 2, 2)

        self.background_calculation_frame_chunk_height_textbox_label = QLabel(self)
        self.background_calculation_frame_chunk_height_textbox_label.setText('Background Calculation Frame Chunk Height: ')
        self.background_calculation_frame_chunk_height_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.background_calculation_frame_chunk_height_textbox_label.setFont(self.font_text)
        self.background_calculation_frame_chunk_height_textbox = QLineEdit(self)
        self.background_calculation_frame_chunk_height_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_height))
        self.background_calculation_frame_chunk_height_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.background_calculation_frame_chunk_height_textbox.setFont(self.font_text)
        self.background_calculation_frame_chunk_height_textbox.returnPressed.connect(self.check_background_calculation_frame_chunk_height_textbox)
        self.grid_layout.addWidget(self.background_calculation_frame_chunk_height_textbox_label, 3, 1)
        self.grid_layout.addWidget(self.background_calculation_frame_chunk_height_textbox, 3, 2)

        self.background_calculation_frames_to_skip_textbox_label = QLabel(self)
        self.background_calculation_frames_to_skip_textbox_label.setText('Background Calculation Frames To Skip: ')
        self.background_calculation_frames_to_skip_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.background_calculation_frames_to_skip_textbox_label.setFont(self.font_text)
        self.background_calculation_frames_to_skip_textbox = QLineEdit(self)
        self.background_calculation_frames_to_skip_textbox.setText('{0}'.format(self.background_calculation_frames_to_skip))
        self.background_calculation_frames_to_skip_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.background_calculation_frames_to_skip_textbox.setFont(self.font_text)
        self.background_calculation_frames_to_skip_textbox.returnPressed.connect(self.check_background_calculation_frames_to_skip_textbox)
        self.grid_layout.addWidget(self.background_calculation_frames_to_skip_textbox_label, 4, 1)
        self.grid_layout.addWidget(self.background_calculation_frames_to_skip_textbox, 4, 2)

        self.save_background_combobox_label = QLabel(self)
        self.save_background_combobox_label.setText('Save Background: ')
        self.save_background_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.save_background_combobox_label.setFont(self.font_text)
        self.save_background_combobox = QComboBox(self)
        self.save_background_combobox.addItem('True')
        self.save_background_combobox.addItem('False')
        self.save_background_combobox.setCurrentIndex(0)
        self.save_background_combobox.currentIndexChanged.connect(self.check_save_background_combobox)
        self.grid_layout.addWidget(self.save_background_combobox_label, 5, 1)
        self.grid_layout.addWidget(self.save_background_combobox, 5, 2)

        self.tracking_method_combobox_label = QLabel(self)
        self.tracking_method_combobox_label.setText('Tracking Method: ')
        self.tracking_method_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_method_combobox_label.setFont(self.font_text)
        self.tracking_method_combobox = QComboBox(self)
        self.tracking_method_combobox.addItem('Free Swimming')
        self.tracking_method_combobox.addItem('Head Fixed Type 1')
        self.tracking_method_combobox.addItem('Head Fixed Type 2')
        self.tracking_method_combobox.setCurrentIndex(0)
        self.tracking_method_combobox.currentIndexChanged.connect(self.check_tracking_method_combobox)
        self.grid_layout.addWidget(self.tracking_method_combobox_label, 6, 1)
        self.grid_layout.addWidget(self.tracking_method_combobox, 6, 2)

        # Initial Pixel Search
        self.initial_pixel_search_combobox_label = QLabel(self)
        self.initial_pixel_search_combobox_label.setText('Pixel Search: ')
        self.initial_pixel_search_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.initial_pixel_search_combobox_label.setFont(self.font_text)
        self.initial_pixel_search_combobox = QComboBox(self)
        self.initial_pixel_search_combobox.addItem('Brightest')
        self.initial_pixel_search_combobox.addItem('Darkest')
        self.initial_pixel_search_combobox.setCurrentIndex(0)
        self.initial_pixel_search_combobox.currentIndexChanged.connect(self.check_initial_pixel_search_combobox)
        self.grid_layout.addWidget(self.initial_pixel_search_combobox_label, 7, 1)
        self.grid_layout.addWidget(self.initial_pixel_search_combobox, 7, 2)

        self.tracking_n_tail_points_textbox_label = QLabel(self)
        self.tracking_n_tail_points_textbox_label.setText('Number of Tail Points: ')
        self.tracking_n_tail_points_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_n_tail_points_textbox_label.setFont(self.font_text)
        self.tracking_n_tail_points_textbox = QLineEdit(self)
        self.tracking_n_tail_points_textbox.setText('{0}'.format(self.n_tail_points))
        self.tracking_n_tail_points_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_n_tail_points_textbox.setFont(self.font_text)
        self.tracking_n_tail_points_textbox.returnPressed.connect(self.check_tracking_n_tail_points_textbox)
        self.grid_layout.addWidget(self.tracking_n_tail_points_textbox_label, 8, 1)
        self.grid_layout.addWidget(self.tracking_n_tail_points_textbox, 8, 2)

        self.tracking_dist_tail_points_textbox_label = QLabel(self)
        self.tracking_dist_tail_points_textbox_label.setText('Distance Between Tail Points: ')
        self.tracking_dist_tail_points_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_tail_points_textbox_label.setFont(self.font_text)
        self.tracking_dist_tail_points_textbox = QLineEdit(self)
        self.tracking_dist_tail_points_textbox.setText('{0}'.format(self.dist_tail_points))
        self.tracking_dist_tail_points_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_tail_points_textbox.setFont(self.font_text)
        self.tracking_dist_tail_points_textbox.returnPressed.connect(self.check_tracking_dist_tail_points_textbox)
        self.grid_layout.addWidget(self.tracking_dist_tail_points_textbox_label, 9, 1)
        self.grid_layout.addWidget(self.tracking_dist_tail_points_textbox, 9, 2)

        self.tracking_dist_eyes_textbox_label = QLabel(self)
        self.tracking_dist_eyes_textbox_label.setText('Distance Between Eyes: ')
        self.tracking_dist_eyes_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_eyes_textbox_label.setFont(self.font_text)
        self.tracking_dist_eyes_textbox = QLineEdit(self)
        self.tracking_dist_eyes_textbox.setText('{0}'.format(self.dist_eyes))
        self.tracking_dist_eyes_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_eyes_textbox.setFont(self.font_text)
        self.tracking_dist_eyes_textbox.returnPressed.connect(self.check_tracking_dist_eyes_textbox)
        self.grid_layout.addWidget(self.tracking_dist_eyes_textbox_label, 10, 1)
        self.grid_layout.addWidget(self.tracking_dist_eyes_textbox, 10, 2)

        self.tracking_dist_swim_bladder_textbox_label = QLabel(self)
        self.tracking_dist_swim_bladder_textbox_label.setText('Distance Between Eyes and Swim Bladder: ')
        self.tracking_dist_swim_bladder_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_swim_bladder_textbox_label.setFont(self.font_text)
        self.tracking_dist_swim_bladder_textbox = QLineEdit(self)
        self.tracking_dist_swim_bladder_textbox.setText('{0}'.format(self.dist_swim_bladder))
        self.tracking_dist_swim_bladder_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_swim_bladder_textbox.setFont(self.font_text)
        self.tracking_dist_swim_bladder_textbox.returnPressed.connect(self.check_tracking_dist_swim_bladder_textbox)
        self.grid_layout.addWidget(self.tracking_dist_swim_bladder_textbox_label, 11, 1)
        self.grid_layout.addWidget(self.tracking_dist_swim_bladder_textbox, 11, 2)

        # Range of Search Angles
        self.range_angles_textbox_label = QLabel(self)
        self.range_angles_textbox_label.setText('Range of Angles for Tail Calculation: ')
        self.range_angles_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.range_angles_textbox_label.setFont(self.font_text)
        self.range_angles_textbox = QLineEdit(self)
        self.range_angles_textbox.setText('{0}'.format(self.range_angles))
        self.range_angles_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.range_angles_textbox.setFont(self.font_text)
        self.range_angles_textbox.returnPressed.connect(self.check_range_angles_textbox)
        self.grid_layout.addWidget(self.range_angles_textbox_label, 12, 1)
        self.grid_layout.addWidget(self.range_angles_textbox, 12, 2)

        # Median Blur
        self.median_blur_textbox_label = QLabel(self)
        self.median_blur_textbox_label.setText('Median Blur Value: ')
        self.median_blur_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.median_blur_textbox_label.setFont(self.font_text)
        self.median_blur_textbox = QLineEdit(self)
        self.median_blur_textbox.setText('{0}'.format(self.median_blur))
        self.median_blur_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.median_blur_textbox.setFont(self.font_text)
        self.median_blur_textbox.returnPressed.connect(self.check_median_blur_textbox)
        self.grid_layout.addWidget(self.median_blur_textbox_label, 13, 1)
        self.grid_layout.addWidget(self.median_blur_textbox, 13, 2)

        # Pixel Threshold
        self.tracking_pixel_threshold_textbox_label = QLabel(self)
        self.tracking_pixel_threshold_textbox_label.setText('Pixel Threshold: ')
        self.tracking_pixel_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_pixel_threshold_textbox_label.setFont(self.font_text)
        self.tracking_pixel_threshold_textbox = QLineEdit(self)
        self.tracking_pixel_threshold_textbox.setText('{0}'.format(self.pixel_threshold))
        self.tracking_pixel_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_pixel_threshold_textbox.setFont(self.font_text)
        self.tracking_pixel_threshold_textbox.returnPressed.connect(self.check_tracking_pixel_threshold_textbox)
        self.grid_layout.addWidget(self.tracking_pixel_threshold_textbox_label, 14, 1)
        self.grid_layout.addWidget(self.tracking_pixel_threshold_textbox, 14, 2)

        # Frame Change Threshold
        self.tracking_frame_change_threshold_textbox_label = QLabel(self)
        self.tracking_frame_change_threshold_textbox_label.setText('Frame Change Threshold: ')
        self.tracking_frame_change_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_frame_change_threshold_textbox_label.setFont(self.font_text)
        self.tracking_frame_change_threshold_textbox = QLineEdit(self)
        self.tracking_frame_change_threshold_textbox.setText('{0}'.format(self.frame_change_threshold))
        self.tracking_frame_change_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_frame_change_threshold_textbox.setFont(self.font_text)
        self.tracking_frame_change_threshold_textbox.returnPressed.connect(self.check_tracking_frame_change_threshold_textbox)
        self.grid_layout.addWidget(self.tracking_frame_change_threshold_textbox_label, 15, 1)
        self.grid_layout.addWidget(self.tracking_frame_change_threshold_textbox, 15, 2)

        # Heading Line Length
        self.tracking_line_length_textbox_label = QLabel(self)
        self.tracking_line_length_textbox_label.setText('Heading Line Length: ')
        self.tracking_line_length_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_line_length_textbox_label.setFont(self.font_text)
        self.tracking_line_length_textbox = QLineEdit(self)
        self.tracking_line_length_textbox.setText('{0}'.format(self.heading_line_length))
        self.tracking_line_length_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_line_length_textbox.setFont(self.font_text)
        self.tracking_line_length_textbox.returnPressed.connect(self.check_tracking_line_length_textbox)
        self.grid_layout.addWidget(self.tracking_line_length_textbox_label, 16, 1)
        self.grid_layout.addWidget(self.tracking_line_length_textbox, 16, 2)

        # Extended Eyes Calculation
        self.extended_eyes_calculation_combobox_label = QLabel(self)
        self.extended_eyes_calculation_combobox_label.setText('Extended Eyes Calculation: ')
        self.extended_eyes_calculation_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.extended_eyes_calculation_combobox_label.setFont(self.font_text)
        self.extended_eyes_calculation_combobox = QComboBox(self)
        self.extended_eyes_calculation_combobox.addItem('True')
        self.extended_eyes_calculation_combobox.addItem('False')
        self.extended_eyes_calculation_combobox.setCurrentIndex(1)
        self.extended_eyes_calculation_combobox.currentIndexChanged.connect(self.check_extended_eyes_calculation_combobox)
        self.grid_layout.addWidget(self.extended_eyes_calculation_combobox_label, 17, 1)
        self.grid_layout.addWidget(self.extended_eyes_calculation_combobox, 17, 2)

        # Eyes Threshold
        self.eyes_threshold_textbox_label = QLabel(self)
        self.eyes_threshold_textbox_label.setText('Eyes Threshold: ')
        self.eyes_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.eyes_threshold_textbox_label.setFont(self.font_text)
        self.eyes_threshold_textbox = QLineEdit(self)
        self.eyes_threshold_textbox.setText('{0}'.format(self.eyes_threshold))
        self.eyes_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.eyes_threshold_textbox.setFont(self.font_text)
        self.eyes_threshold_textbox.returnPressed.connect(self.check_eyes_threshold_textbox)
        self.grid_layout.addWidget(self.eyes_threshold_textbox_label, 18, 1)
        self.grid_layout.addWidget(self.eyes_threshold_textbox, 18, 2)

        # Eyes Line Length
        self.eyes_line_length_textbox_label = QLabel(self)
        self.eyes_line_length_textbox_label.setText('Eyes Line Length: ')
        self.eyes_line_length_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.eyes_line_length_textbox_label.setFont(self.font_text)
        self.eyes_line_length_textbox = QLineEdit(self)
        self.eyes_line_length_textbox.setText('{0}'.format(self.eyes_threshold))
        self.eyes_line_length_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.eyes_line_length_textbox.setFont(self.font_text)
        self.eyes_line_length_textbox.returnPressed.connect(self.check_eyes_line_length_textbox)
        self.grid_layout.addWidget(self.eyes_line_length_textbox_label, 19, 1)
        self.grid_layout.addWidget(self.eyes_line_length_textbox, 19, 2)

        # Invert Eyes Threshold
        self.invert_threshold_combobox_label = QLabel(self)
        self.invert_threshold_combobox_label.setText('Invert Eyes Treshold: ')
        self.invert_threshold_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.invert_threshold_combobox_label.setFont(self.font_text)
        self.invert_threshold_combobox = QComboBox(self)
        self.invert_threshold_combobox.addItem('True')
        self.invert_threshold_combobox.addItem('False')
        self.invert_threshold_combobox.setCurrentIndex(0)
        self.invert_threshold_combobox.currentIndexChanged.connect(self.check_invert_threshold_combobox)
        self.grid_layout.addWidget(self.invert_threshold_combobox_label, 20, 1)
        self.grid_layout.addWidget(self.invert_threshold_combobox, 20, 2)

        # Save Video
        self.save_tracked_video_combobox_label = QLabel(self)
        self.save_tracked_video_combobox_label.setText('Save Tracked Video: ')
        self.save_tracked_video_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.save_tracked_video_combobox_label.setFont(self.font_text)
        self.save_tracked_video_combobox = QComboBox(self)
        self.save_tracked_video_combobox.addItem('True')
        self.save_tracked_video_combobox.addItem('False')
        self.save_tracked_video_combobox.setCurrentIndex(1)
        self.save_tracked_video_combobox.currentIndexChanged.connect(self.check_save_tracked_video_combobox)
        self.grid_layout.addWidget(self.save_tracked_video_combobox_label, 21, 1)
        self.grid_layout.addWidget(self.save_tracked_video_combobox, 21, 2)

        # Starting Frame
        self.tracking_starting_frame_textbox_label = QLabel(self)
        self.tracking_starting_frame_textbox_label.setText('Starting Frame: ')
        self.tracking_starting_frame_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_starting_frame_textbox_label.setFont(self.font_text)
        self.tracking_starting_frame_textbox = QLineEdit(self)
        self.tracking_starting_frame_textbox.setText('{0}'.format(self.starting_frame))
        self.tracking_starting_frame_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_starting_frame_textbox.setFont(self.font_text)
        self.tracking_starting_frame_textbox.returnPressed.connect(self.check_tracking_starting_frame_textbox)
        self.grid_layout.addWidget(self.tracking_starting_frame_textbox_label, 22, 1)
        self.grid_layout.addWidget(self.tracking_starting_frame_textbox, 22, 2)

        # Tracking Frames
        self.tracking_n_frames_textbox_label = QLabel(self)
        self.tracking_n_frames_textbox_label.setText('Number of Frames to Track: ')
        self.tracking_n_frames_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_n_frames_textbox_label.setFont(self.font_text)
        self.tracking_n_frames_textbox = QLineEdit(self)
        self.tracking_n_frames_textbox.setText('{0}'.format(self.n_frames))
        self.tracking_n_frames_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_n_frames_textbox.setFont(self.font_text)
        self.tracking_n_frames_textbox.returnPressed.connect(self.check_tracking_n_frames_textbox)
        self.grid_layout.addWidget(self.tracking_n_frames_textbox_label, 23, 1)
        self.grid_layout.addWidget(self.tracking_n_frames_textbox, 23, 2)

        self.trigger_load_default_tracking_parameters()
        self.trigger_load_default_colours()
        self.update_tracking_parameters(inactivate = True)
    def add_tracking_parameters_buttons(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.descriptors_window_size[0] + ((self.tracking_parameters_window_size[0] - self.tracking_parameters_button_size[0]) / 2)) / 2560) * self.main_window_width
        new_width = (self.tracking_parameters_button_size[0] / 2560) * self.main_window_width
        new_height = (self.tracking_parameters_button_size[1] / 1400) * self.main_window_height

        self.load_default_tracking_parameters_button = QPushButton('Load Default Tracking Parameters', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_y_offset + (14 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + (0 * (self.tracking_parameters_button_size[1] + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height
        self.load_default_tracking_parameters_button.move(new_x, new_y)
        self.load_default_tracking_parameters_button.resize(new_width, new_height)
        self.load_default_tracking_parameters_button.setFont(self.font_text)
        self.load_default_tracking_parameters_button.clicked.connect(self.check_load_default_tracking_parameters_button)

        self.load_previous_tracking_parameters_button = QPushButton('Load Previous Tracking Parameters', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_y_offset + (14 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + (1 * (self.tracking_parameters_button_size[1] + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height
        self.load_previous_tracking_parameters_button.move(new_x, new_y)
        self.load_previous_tracking_parameters_button.resize(new_width, new_height)
        self.load_previous_tracking_parameters_button.setFont(self.font_text)
        self.load_previous_tracking_parameters_button.clicked.connect(self.trigger_load_previous_tracking_parameters)

        self.save_current_tracking_parameters_button = QPushButton('Save Current Tracking Parameters', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_y_offset + (14 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + (2 * (self.tracking_parameters_button_size[1] + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height
        self.save_current_tracking_parameters_button.move(new_x, new_y)
        self.save_current_tracking_parameters_button.resize(new_width, new_height)
        self.save_current_tracking_parameters_button.setFont(self.font_text)
        self.save_current_tracking_parameters_button.clicked.connect(self.trigger_save_current_tracking_parameters)

        self.track_video_button = QPushButton('Track Video', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_y_offset + (14 * (self.tracking_parameters_height + self.tracking_parameters_y_spacing)) + (3 * (self.tracking_parameters_button_size[1] + self.tracking_parameters_y_spacing))) / 1400) * self.main_window_height
        self.track_video_button.move(new_x, new_y)
        self.track_video_button.resize(new_width, new_height)
        self.track_video_button.setFont(self.font_text)
        self.track_video_button.clicked.connect(self.trigger_track_video)
        self.update_tracking_parameters_buttons(inactivate = True)
    def add_colour_parameters_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.preview_parameters_window_size[0]) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing) / 1400) * self.main_window_height
        new_width = (self.colour_parameters_window_size[0] / 2560) * self.main_window_width
        new_height = (self.colour_parameters_window_size[1] / 1400) * self.main_window_height

        self.colour_parameters_window = QLabel(self)
        self.colour_parameters_window.setFrameShape(QFrame.StyledPanel)
        # self.colour_parameters_window.setFrameShadow(QFrame.Sunken)
        # self.colour_parameters_window.setLineWidth(5)
        self.colour_parameters_window.move(new_x, new_y)
        self.colour_parameters_window.resize(new_width, new_height)
        self.colour_parameters_window.setText('Colour Parameters')
        self.colour_parameters_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.colour_parameters_window.setFont(self.font_title)
    def add_colour_parameters_to_window(self):
        self.colour_label_list = []
        self.colour_textbox_list = []
        self.colour_button_list = []
        new_label_width = (self.colour_parameters_label_width / 2560) * self.main_window_width
        new_height = (self.colour_parameters_height / 1400) * self.main_window_height
        new_textbox_width = (self.colour_parameters_textbox_width / 2560) * self.main_window_width
        new_icon_height = new_height - 4
        for i in range(len(self.colours)):
            count = int(i / 6)
            colour_label = QLabel(self)
            if i == len(self.colours) - 1:
                colour_label.setText('Heading Angle: ')
            if i == len(self.colours) - 2:
                colour_label.setText('First Eye: ')
            if i == len(self.colours) - 3:
                colour_label.setText('Second Eye: ')
            if i < len(self.colours) - 3 :
                colour_label.setText('Tail Point {0}: '.format(i + 1))
            new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.colour_parameters_x_offset + self.preview_parameters_window_size[0] + (count * (self.colour_parameters_width + self.colour_parameters_x_spacing))) / 2560) * self.main_window_width
            new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.colour_parameters_y_offset + (i * (self.colour_parameters_height + self.colour_parameters_y_spacing)) - (count * 6 * (self.colour_parameters_height + self.colour_parameters_y_spacing))) / 1400) * self.main_window_height
            colour_label.move(new_x, new_y)
            colour_label.resize(new_label_width, new_height)
            colour_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            colour_label.setFont(self.font_colour_parameters)
            self.colour_label_list.append(colour_label)
            colour_textbox = QLineEdit(self)
            colour_textbox.setText('{0}'.format(self.colours[i]))
            new_x = new_x + new_label_width
            colour_textbox.move(new_x, new_y)
            colour_textbox.resize(new_textbox_width, new_height)
            colour_textbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            colour_textbox.setFont(self.font_colour_parameters)
            colour_textbox.setEnabled(False)
            self.colour_textbox_list.append(colour_textbox)
            colour_button = QPushButton(self)
            colour_button.setIcon(QIcon('icons\\button_icon_13.png'))
            colour_button.setIconSize(QSize(new_icon_height, new_icon_height))
            new_x = new_x + new_textbox_width + self.colour_select_button_x_spacing
            colour_button.move(new_x, new_y)
            colour_button.resize(new_height, new_height)
            colour_button.clicked.connect(partial(self.trigger_update_single_colour, i))
            self.colour_button_list.append(colour_button)
        self.update_colour_parameters(inactivate = True)
        self.update_colours()
    def add_colour_parameters_buttons(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.preview_parameters_window_size[0] + self.colour_parameters_window_size[0] - (self.colour_parameters_button_x_offset + self.colour_parameters_button_size[0])) / 2560) * self.main_window_width
        new_width = (self.colour_parameters_button_size[0] / 2560) * self.main_window_width
        new_height = (self.colour_parameters_button_size[1] / 1400) * self.main_window_height

        self.load_default_colours_button = QPushButton('Load Default Colours', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.colour_parameters_y_offset + (0 * (self.colour_parameters_button_size[1] + self.colour_parameters_button_y_spacing))) / 1400) * self.main_window_height
        self.load_default_colours_button.move(new_x, new_y)
        self.load_default_colours_button.resize(new_width, new_height)
        self.load_default_colours_button.setFont(self.font_colour_parameters)
        self.load_default_colours_button.clicked.connect(self.check_load_default_colours_button)

        self.load_previous_colours_button = QPushButton('Load Previous Colours', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.colour_parameters_y_offset + (1 * (self.colour_parameters_button_size[1] + self.colour_parameters_button_y_spacing))) / 1400) * self.main_window_height
        self.load_previous_colours_button.move(new_x, new_y)
        self.load_previous_colours_button.resize(new_width, new_height)
        self.load_previous_colours_button.setFont(self.font_colour_parameters)
        self.load_previous_colours_button.clicked.connect(self.trigger_load_previous_colours)

        self.save_current_colours_button = QPushButton('Save Current Colours', self)
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.colour_parameters_y_offset + (2 * (self.colour_parameters_button_size[1] + self.colour_parameters_button_y_spacing))) / 1400) * self.main_window_height
        self.save_current_colours_button.move(new_x, new_y)
        self.save_current_colours_button.resize(new_width, new_height)
        self.save_current_colours_button.setFont(self.font_colour_parameters)
        self.save_current_colours_button.clicked.connect(self.trigger_save_current_colours)
        self.update_colour_parameters_buttons(inactivate = True)
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
    def add_status_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.descriptors_window_size[1] + self.main_window_spacing) / 1400) * self.main_window_height
        new_width = (self.status_window_size[0] / 2560) * self.main_window_width
        new_height = (self.status_window_size[1] / 1400) * self.main_window_height

        self.status_window = QLabel(self)
        self.status_window.setFrameShape(QFrame.StyledPanel)
        # self.status_window.setFrameShadow(QFrame.Sunken)
        # self.status_window.setLineWidth(5)
        self.status_window.move(new_x, new_y)
        self.status_window.resize(new_width, new_height)
        self.status_window.setText('Status')
        self.status_window.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.status_window.setFont(self.font_title)
    def add_statuses_to_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.statuses_x_offset) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.descriptors_window_size[1] + self.statuses_y_offset) / 1400) * self.main_window_height

        self.status_label = QLabel(self)
        self.status_label.move(new_x, new_y)
        self.status_label.resize(100, 50)
        self.status_label.setText('Ready.')

        # self.calculate_background_button = QPushButton('Calculate Background', self)
        # self.calculate_background_button.move(new_x, new_y)
        # new_width = (self.statuses_button_size[0] / 2560) * self.main_window_width
        # new_height = (self.statuses_button_size[1] / 1400) * self.main_window_height
        # self.calculate_background_button.resize(new_width, new_height)
        # self.calculate_background_button.setFont(self.font_text)
        # self.calculate_background_button.clicked.connect(self.trigger_calculate_background)
        self.calculate_background_progress_bar = QProgressBar(self)
        new_y = ((self.main_window_y_offset + self.descriptors_window_size[1] + self.statuses_y_offset + self.statuses_button_size[1]) / 1400) * self.main_window_height
        self.calculate_background_progress_bar.move(new_x, new_y)
        new_width = (self.status_window_size[0] / 2560) * self.main_window_width
        # new_width = self.preview_frame_window_size[0]
        new_height = (self.status_bars_height / 1400) * self.main_window_height
        self.calculate_background_progress_bar.resize(new_width, new_height)

        self.calculate_background_button = QPushButton('Calculate Background', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.statuses_x_offset + (self.status_window_size[0] / 4)) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.descriptors_window_size[1] + self.statuses_y_offset + self.statuses_button_size[1] + self.status_bars_height + self.status_buttons_y_spacing) / 1400) * self.main_window_height
        self.calculate_background_button.move(new_x, new_y)
        new_width = (self.statuses_button_size[0] / 2560) * self.main_window_width
        new_height = (self.statuses_button_size[1] / 1400) * self.main_window_height
        self.calculate_background_button.resize(new_width, new_height)
        self.calculate_background_button.setFont(self.font_text)
        self.calculate_background_button.clicked.connect(self.trigger_calculate_background)

    # Defining Update Functions
    def update_statusbar_message(self):
        if self.statusbar.currentMessage() == '':
            self.statusbar.showMessage(self.statusbar_message)
    def update_descriptors(self):
        self.video_path_folder_descriptor.setText('Video Folder: {0}'.format(self.video_path_folder))
        self.video_path_basename_descriptor.setText('Video Filename: {0}'.format(self.video_path_basename))
        self.video_n_frames_descriptor.setText('Video Total Frames: {0}'.format(self.video_n_frames))
        self.video_fps_descriptor.setText('Video FPS: {0}'.format(self.video_fps))
        self.frame_width_descriptor.setText('Frame Width: {0}'.format(self.video_frame_width))
        self.frame_height_descriptor.setText('Frame Height: {0}'.format(self.video_frame_height))
        self.background_path_basename_descriptor.setText('Background Filename: {0}'.format(self.background_path_basename))
        self.save_path_descriptor.setText('Save Path: {0}'.format(self.save_path))
    def update_preview_frame(self, frame, frame_width, frame_height, scaled_width = None, grayscale = True, preview_crop = None):
        if grayscale:
            format = QImage.Format_Indexed8
        else:
            format = QImage.Format_RGB888
        if scaled_width is None:
            scaled_width = int(self.video_frame_width / 100) * 100
        else:
            scaled_width = int(scaled_width / 100) * 100
        if self.mask:
            format = QImage.Format_RGB888
            if frame_width > frame_height:
                center_x = (self.mask[0] / self.preview_frame_window_size[0]) * frame_width
                center_y = (self.mask[1] / int((frame_height / frame_width) * self.preview_frame_window_size[1])) * frame_height
                width = (self.mask[2] / self.preview_frame_window_size[0]) * frame_width
                height = (self.mask[3] / int((frame_height / frame_width) * self.preview_frame_window_size[1])) * frame_height
            else:
                center_x = (self.mask[0] / int((frame_width / frame_height) * self.preview_frame_window_size[0])) * frame_width
                center_y = (self.mask[1] / self.preview_frame_window_size[1]) * frame_height
                width = (self.mask[2] / int((frame_width / frame_height) * self.preview_frame_window_size[0])) * frame_width
                height = (self.mask[3] / self.preview_frame_window_size[1]) * frame_height
            if self.mask[4] == 'ellipse':
                frame = ut.apply_elliptical_mask_to_frame(frame, center_x, center_y, width, height)
            if self.mask[4] == 'rectangle':
                frame = ut.apply_rectangular_mask_to_frame(frame, center_x, center_y, width, height)
        if preview_crop:
            if frame_width > frame_height:
                new_width = int(self.preview_frame_window_size[0])
                new_height = int((frame_height / frame_width) * self.preview_frame_window_size[1])
            else:
                new_width = int((frame_width / frame_height) * self.preview_frame_window_size[0])
                new_height = int(self.preview_frame_window_size[1])
        else:
            new_width = scaled_width
            new_height = int((frame_height / frame_width) * scaled_width)
        frame = cv2.resize(frame, dsize=(new_width, new_height), interpolation=cv2.INTER_CUBIC).copy()
        self.preview_frame = QImage(frame.data, frame.shape[1], frame.shape[0], int(frame.nbytes / frame.shape[0]), format)
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
    def update_preview_parameters(self, activate = False, inactivate = False, activate_preview_background = False):
        if activate_preview_background:
            if not self.preview_background_checkbox.isEnabled():
                self.preview_background_checkbox.setEnabled(True)
        if activate:
            if not self.preview_background_checkbox.isEnabled():
                self.preview_background_checkbox.setEnabled(True)
            if not self.preview_background_subtracted_frame_checkbox.isEnabled():
                self.preview_background_subtracted_frame_checkbox.setEnabled(True)
            if not self.preview_tracking_results_checkbox.isEnabled():
                self.preview_tracking_results_checkbox.setEnabled(True)
            if not self.preview_eyes_threshold_checkbox.isEnabled():
                self.preview_eyes_threshold_checkbox.setEnabled(True)
        if inactivate:
            if self.preview_background_checkbox.isEnabled():
                self.preview_background_checkbox.setEnabled(False)
            if self.preview_background_subtracted_frame_checkbox.isEnabled():
                self.preview_background_subtracted_frame_checkbox.setEnabled(False)
            if self.preview_tracking_results_checkbox.isEnabled():
                self.preview_tracking_results_checkbox.setEnabled(False)
            if self.preview_eyes_threshold_checkbox.isEnabled():
                self.preview_eyes_threshold_checkbox.setEnabled(False)
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
            if not self.elliptical_crop_frame_button.isEnabled():
                self.elliptical_crop_frame_button.setEnabled(True)
            if not self.rectangular_crop_frame_button.isEnabled():
                self.rectangular_crop_frame_button.setEnabled(True)
        if inactivate:
            if self.magnify_frame_button.isEnabled():
                self.magnify_frame_button.setEnabled(False)
                if self.magnify_frame_button.isChecked():
                    self.magnify_frame_button.setChecked(False)
            if self.pan_frame_button.isEnabled():
                self.pan_frame_button.setEnabled(False)
                if self.pan_frame_button.isChecked():
                    self.pan_frame_button.setChecked(False)
            if self.elliptical_crop_frame_button.isEnabled():
                self.elliptical_crop_frame_button.setEnabled(False)
            if self.rectangular_crop_frame_button.isEnabled():
                self.rectangular_crop_frame_button.setEnabled(False)
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
        if self.elliptical_crop_frame_button.isEnabled():
            if self.elliptical_crop_frame:
                self.elliptical_crop_frame_button.setChecked(True)
            else:
                self.elliptical_crop_frame_button.setChecked(False)
        if self.rectangular_crop_frame_button.isEnabled():
            if self.rectangular_crop_frame:
                self.rectangular_crop_frame_button.setChecked(True)
            else:
                self.rectangular_crop_frame_button.setChecked(False)
    def update_frame_window_slider_position(self):
        self.frame_window_slider.setValue(self.frame_number)
    def update_tracking_parameters(self, activate = False, inactivate = False):
        if activate:
            if not self.background_calculation_method_combobox.isEnabled():
                self.background_calculation_method_combobox.setEnabled(True)
            if not self.background_calculation_frame_chunk_width_textbox.isEnabled():
                self.background_calculation_frame_chunk_width_textbox.setEnabled(True)
            if not self.background_calculation_frame_chunk_height_textbox.isEnabled():
                self.background_calculation_frame_chunk_height_textbox.setEnabled(True)
            if not self.background_calculation_frames_to_skip_textbox.isEnabled():
                self.background_calculation_frames_to_skip_textbox.setEnabled(True)
            if not self.save_background_combobox.isEnabled():
                self.save_background_combobox.setEnabled(True)
            if not self.tracking_method_combobox.isEnabled():
                self.tracking_method_combobox.setEnabled(True)
            if not self.tracking_n_tail_points_textbox.isEnabled():
                self.tracking_n_tail_points_textbox.setEnabled(True)
            if not self.tracking_dist_tail_points_textbox.isEnabled():
                self.tracking_dist_tail_points_textbox.setEnabled(True)
            if not self.tracking_dist_eyes_textbox.isEnabled():
                self.tracking_dist_eyes_textbox.setEnabled(True)
            if not self.tracking_dist_swim_bladder_textbox.isEnabled():
                self.tracking_dist_swim_bladder_textbox.setEnabled(True)
            if not self.tracking_starting_frame_textbox.isEnabled():
                self.tracking_starting_frame_textbox.setEnabled(True)
            if not self.tracking_n_frames_textbox.isEnabled():
                self.tracking_n_frames_textbox.setEnabled(True)
            if not self.tracking_line_length_textbox.isEnabled():
                self.tracking_line_length_textbox.setEnabled(True)
            if not self.tracking_pixel_threshold_textbox.isEnabled():
                self.tracking_pixel_threshold_textbox.setEnabled(True)
            if not self.tracking_frame_change_threshold_textbox.isEnabled():
                self.tracking_frame_change_threshold_textbox.setEnabled(True)
            if not self.eyes_threshold_textbox.isEnabled():
                self.eyes_threshold_textbox.setEnabled(True)
            if not self.eyes_line_length_textbox.isEnabled():
                self.eyes_line_length_textbox.setEnabled(True)
            if not self.save_tracked_video_combobox.isEnabled():
                self.save_tracked_video_combobox.setEnabled(True)
            if not self.extended_eyes_calculation_combobox.isEnabled():
                self.extended_eyes_calculation_combobox.setEnabled(True)
            if not self.median_blur_textbox.isEnabled():
                self.median_blur_textbox.setEnabled(True)
            if not self.initial_pixel_search_combobox.isEnabled():
                self.initial_pixel_search_combobox.setEnabled(True)
            if not self.invert_threshold_combobox.isEnabled():
                self.invert_threshold_combobox.setEnabled(True)
            if not self.range_angles_textbox.isEnabled():
                self.range_angles_textbox.setEnabled(True)
        if inactivate:
            if self.background_calculation_method_combobox.isEnabled():
                self.background_calculation_method_combobox.setEnabled(False)
            if self.background_calculation_frame_chunk_width_textbox.isEnabled():
                self.background_calculation_frame_chunk_width_textbox.setEnabled(False)
            if self.background_calculation_frame_chunk_height_textbox.isEnabled():
                self.background_calculation_frame_chunk_height_textbox.setEnabled(False)
            if self.background_calculation_frames_to_skip_textbox.isEnabled():
                self.background_calculation_frames_to_skip_textbox.setEnabled(False)
            if self.save_background_combobox.isEnabled():
                self.save_background_combobox.setEnabled(False)
            if self.tracking_method_combobox.isEnabled():
                self.tracking_method_combobox.setEnabled(False)
            if self.tracking_n_tail_points_textbox.isEnabled():
                self.tracking_n_tail_points_textbox.setEnabled(False)
            if self.tracking_dist_tail_points_textbox.isEnabled():
                self.tracking_dist_tail_points_textbox.setEnabled(False)
            if self.tracking_dist_eyes_textbox.isEnabled():
                self.tracking_dist_eyes_textbox.setEnabled(False)
            if self.tracking_dist_swim_bladder_textbox.isEnabled():
                self.tracking_dist_swim_bladder_textbox.setEnabled(False)
            if self.tracking_starting_frame_textbox.isEnabled():
                self.tracking_starting_frame_textbox.setEnabled(False)
            if self.tracking_n_frames_textbox.isEnabled():
                self.tracking_n_frames_textbox.setEnabled(False)
            if self.tracking_line_length_textbox.isEnabled():
                self.tracking_line_length_textbox.setEnabled(False)
            if self.tracking_pixel_threshold_textbox.isEnabled():
                self.tracking_pixel_threshold_textbox.setEnabled(False)
            if self.tracking_frame_change_threshold_textbox.isEnabled():
                self.tracking_frame_change_threshold_textbox.setEnabled(False)
            if self.eyes_threshold_textbox.isEnabled():
                self.eyes_threshold_textbox.setEnabled(False)
            if self.eyes_line_length_textbox.isEnabled():
                self.eyes_line_length_textbox.setEnabled(False)
            if self.save_tracked_video_combobox.isEnabled():
                self.save_tracked_video_combobox.setEnabled(False)
            if self.extended_eyes_calculation_combobox.isEnabled():
                self.extended_eyes_calculation_combobox.setEnabled(False)
            if self.median_blur_textbox.isEnabled():
                self.median_blur_textbox.setEnabled(False)
            if self.initial_pixel_search_combobox.isEnabled():
                self.initial_pixel_search_combobox.setEnabled(False)
            if self.invert_threshold_combobox.isEnabled():
                self.invert_threshold_combobox.setEnabled(False)
            if self.range_angles_textbox.isEnabled():
                self.range_angles_textbox.setEnabled(False)
        if self.background_calculation_method_combobox.isEnabled():
            if self.background_calculation_method == 'brightest':
                self.background_calculation_method_combobox.setCurrentIndex(0)
            elif self.background_calculation_method == 'darkest':
                self.background_calculation_method_combobox.setCurrentIndex(1)
            else:
                self.background_calculation_method_combobox.setCurrentIndex(2)
        if self.background_calculation_frame_chunk_width_textbox.isEnabled():
            self.background_calculation_frame_chunk_width_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_width))
        if self.background_calculation_frame_chunk_height_textbox.isEnabled():
            self.background_calculation_frame_chunk_height_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_height))
        if self.background_calculation_frames_to_skip_textbox.isEnabled():
            self.background_calculation_frames_to_skip_textbox.setText('{0}'.format(self.background_calculation_frames_to_skip))
        if self.save_background_combobox.isEnabled():
            if self.save_background:
                self.save_background_combobox.setCurrentIndex(0)
            else:
                self.save_background_combobox.setCurrentIndex(1)
        if self.tracking_method_combobox.isEnabled():
            if self.tracking_method == 'free_swimming':
                self.tracking_method_combobox.setCurrentIndex(0)
            else:
                self.tracking_method_combobox.setCurrentIndex(1)
        if self.tracking_n_tail_points_textbox.isEnabled():
            self.tracking_n_tail_points_textbox.setText('{0}'.format(self.n_tail_points))
        if self.tracking_dist_tail_points_textbox.isEnabled():
            self.tracking_dist_tail_points_textbox.setText('{0}'.format(self.dist_tail_points))
        if self.tracking_dist_eyes_textbox.isEnabled():
            self.tracking_dist_eyes_textbox.setText('{0}'.format(self.dist_eyes))
        if self.tracking_dist_swim_bladder_textbox.isEnabled():
            self.tracking_dist_swim_bladder_textbox.setText('{0}'.format(self.dist_swim_bladder))
        if self.tracking_starting_frame_textbox.isEnabled():
            self.tracking_starting_frame_textbox.setText('{0}'.format(self.starting_frame))
        if self.tracking_n_frames_textbox.isEnabled():
            self.tracking_n_frames_textbox.setText('{0}'.format(self.n_frames))
        if self.tracking_line_length_textbox.isEnabled():
            self.tracking_line_length_textbox.setText('{0}'.format(self.heading_line_length))
        if self.tracking_pixel_threshold_textbox.isEnabled():
            self.tracking_pixel_threshold_textbox.setText('{0}'.format(self.pixel_threshold))
        if self.tracking_frame_change_threshold_textbox.isEnabled():
            self.tracking_frame_change_threshold_textbox.setText('{0}'.format(self.frame_change_threshold))
        if self.eyes_threshold_textbox.isEnabled():
            self.eyes_threshold_textbox.setText('{0}'.format(self.eyes_threshold))
        if self.eyes_line_length_textbox.isEnabled():
            self.eyes_line_length_textbox.setText('{0}'.format(self.eyes_line_length))
        if self.save_tracked_video_combobox.isEnabled():
            if self.save_video:
                self.save_tracked_video_combobox.setCurrentIndex(0)
            else:
                self.save_tracked_video_combobox.setCurrentIndex(1)
        if self.extended_eyes_calculation_combobox.isEnabled():
            if self.extended_eyes_calculation:
                self.extended_eyes_calculation_combobox.setCurrentIndex(0)
            else:
                self.extended_eyes_calculation_combobox.setCurrentIndex(1)
        if self.median_blur_textbox.isEnabled():
            self.median_blur_textbox.setText('{0}'.format(self.median_blur))
        if self.background_calculation_method_combobox.isEnabled():
            if self.background_calculation_method == 'brightest':
                self.background_calculation_method_combobox.setCurrentIndex(0)
            elif self.background_calculation_method == 'darkest':
                self.background_calculation_method_combobox.setCurrentIndex(1)
            else:
                self.background_calculation_method_combobox.setCurrentIndex(2)
        if self.background_calculation_frame_chunk_width_textbox.isEnabled():
            self.background_calculation_frame_chunk_width_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_width))
        if self.background_calculation_frame_chunk_height_textbox.isEnabled():
            self.background_calculation_frame_chunk_height_textbox.setText('{0}'.format(self.background_calculation_frame_chunk_height))
        if self.background_calculation_frames_to_skip_textbox.isEnabled():
            self.background_calculation_frames_to_skip_textbox.setText('{0}'.format(self.background_calculation_frames_to_skip))
        if self.initial_pixel_search_combobox.isEnabled():
            if self.initial_pixel_search == 'brightest':
                self.initial_pixel_search_combobox.setCurrentIndex(0)
            if self.initial_pixel_search == 'darkest':
                self.initial_pixel_search_combobox.setCurrentIndex(1)
        if self.invert_threshold_combobox.isEnabled():
            if self.invert_threshold:
                self.invert_threshold_combobox.setCurrentIndex(0)
            else:
                self.invert_threshold_combobox.setCurrentIndex(1)
        if self.range_angles_textbox.isEnabled():
            self.range_angles_textbox.setText('{0}'.format(self.range_angles))
    def update_tracking_parameters_buttons(self, activate = False, inactivate = False):
        if activate:
            if not self.load_default_tracking_parameters_button.isEnabled():
                self.load_default_tracking_parameters_button.setEnabled(True)
            if not self.load_previous_tracking_parameters_button.isEnabled():
                self.load_previous_tracking_parameters_button.setEnabled(True)
            if not self.save_current_tracking_parameters_button.isEnabled():
                self.save_current_tracking_parameters_button.setEnabled(True)
            if not self.track_video_button.isEnabled():
                self.track_video_button.setEnabled(True)
        if inactivate:
            if self.load_default_tracking_parameters_button.isEnabled():
                self.load_default_tracking_parameters_button.setEnabled(False)
            if self.load_previous_tracking_parameters_button.isEnabled():
                self.load_previous_tracking_parameters_button.setEnabled(False)
            if self.save_current_tracking_parameters_button.isEnabled():
                self.save_current_tracking_parameters_button.setEnabled(False)
            if self.track_video_button.isEnabled():
                self.track_video_button.setEnabled(False)
    def update_colour_parameters(self, activate = False, inactivate = False):
        if inactivate:
            for i in range(len(self.colour_button_list)):
                if self.colour_button_list[i].isEnabled():
                    self.colour_button_list[i].setEnabled(False)
        if activate:
            for i in range(len(self.colour_button_list)):
                if not self.colour_button_list[i].isEnabled():
                    self.colour_button_list[i].setEnabled(True)
    def update_colour_parameters_buttons(self, activate = False, inactivate = False):
        if activate:
            if not self.load_default_colours_button.isEnabled():
                self.load_default_colours_button.setEnabled(True)
            if not self.load_previous_colours_button.isEnabled():
                self.load_previous_colours_button.setEnabled(True)
            if not self.save_current_colours_button.isEnabled():
                self.save_current_colours_button.setEnabled(True)
        if inactivate:
            if self.load_default_colours_button.isEnabled():
                self.load_default_colours_button.setEnabled(False)
            if self.load_previous_colours_button.isEnabled():
                self.load_previous_colours_button.setEnabled(False)
            if self.save_current_colours_button.isEnabled():
                self.save_current_colours_button.setEnabled(False)
    def update_colours(self):
        if self.n_tail_points < len(self.colours) - 3 and len(self.colours) == len(self.colour_label_list):
            for i in range(len(self.colours) - 3 - self.n_tail_points):
                self.colour_label_list[len(self.colour_label_list) - 1].deleteLater()
                self.colour_textbox_list[len(self.colour_textbox_list) - 1].deleteLater()
                self.colour_button_list[len(self.colour_button_list) - 1].deleteLater()
                del(self.colour_label_list[len(self.colour_label_list) - 1])
                del(self.colour_textbox_list[len(self.colour_textbox_list) - 1])
                del(self.colour_button_list[len(self.colour_button_list) - 1])
                del(self.colours[self.n_tail_points])
            for i in range(len(self.colours)):
                if i == len(self.colours) - 1:
                    self.colour_label_list[i].setText('Heading Angle: ')
                if i == len(self.colours) - 2:
                    self.colour_label_list[i].setText('First Eye: ')
                if i == len(self.colours) - 3:
                    self.colour_label_list[i].setText('Second Eye: ')
                if i < len(self.colours) - 3 :
                    self.colour_label_list[i].setText('Tail Point {0}: '.format(i + 1))
                self.colour_textbox_list[i].setText('{0}'.format(self.colours[i]))
        elif self.n_tail_points > len(self.colours) - 3 and len(self.colours) == len(self.colour_label_list):
            new_label_width = (self.colour_parameters_label_width / 2560) * self.main_window_width
            new_height = (self.colour_parameters_height / 1400) * self.main_window_height
            new_textbox_width = (self.colour_parameters_textbox_width / 2560) * self.main_window_width
            new_icon_height = new_height - 4
            for i in range(self.n_tail_points + 3 - len(self.colours)):
                self.colours.insert(i + self.n_tail_points - 1, (0, 0, 0))
                count = int((len(self.colours) - 1) / 6)
                colour_label = QLabel(self)
                new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + (2 * self.main_window_spacing) + self.colour_parameters_x_offset + self.preview_parameters_window_size[0] + (count * (self.colour_parameters_width + self.colour_parameters_x_spacing))) / 2560) * self.main_window_width
                new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing + self.colour_parameters_y_offset + ((len(self.colours) - 1) * (self.colour_parameters_height + self.colour_parameters_y_spacing)) - (count * 6 * (self.colour_parameters_height + self.colour_parameters_y_spacing))) / 1400) * self.main_window_height
                colour_label.move(new_x, new_y)
                colour_label.resize(new_label_width, new_height)
                colour_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                colour_label.setFont(self.font_colour_parameters)
                colour_label.show()
                self.colour_label_list.append(colour_label)
                colour_textbox = QLineEdit(self)
                new_x = new_x + new_label_width
                colour_textbox.move(new_x, new_y)
                colour_textbox.resize(new_textbox_width, new_height)
                colour_textbox.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                colour_textbox.setFont(self.font_colour_parameters)
                colour_textbox.setEnabled(False)
                colour_textbox.show()
                self.colour_textbox_list.append(colour_textbox)
                colour_button = QPushButton(self)
                colour_button.setIcon(QIcon('icons\\button_icon_13.png'))
                colour_button.setIconSize(QSize(new_icon_height, new_icon_height))
                new_x = new_x + new_textbox_width + self.colour_select_button_x_spacing
                colour_button.move(new_x, new_y)
                colour_button.resize(new_height, new_height)
                colour_button.clicked.connect(partial(self.trigger_update_single_colour, len(self.colours) - 1))
                colour_button.show()
                self.colour_button_list.append(colour_button)
            for i in range(len(self.colours)):
                if i == len(self.colours) - 1:
                    self.colour_label_list[i].setText('Heading Angle: ')
                if i == len(self.colours) - 2:
                    self.colour_label_list[i].setText('First Eye: ')
                if i == len(self.colours) - 3:
                    self.colour_label_list[i].setText('Second Eye: ')
                if i < len(self.colours) - 3 :
                    self.colour_label_list[i].setText('Tail Point {0}: '.format(i + 1))
                self.colour_textbox_list[i].setText('{0}'.format(self.colours[i]))
        else:
            for i in range(len(self.colours)):
                if i == len(self.colours) - 1:
                    self.colour_label_list[i].setText('Heading Angle: ')
                if i == len(self.colours) - 2:
                    self.colour_label_list[i].setText('First Eye: ')
                if i == len(self.colours) - 3:
                    self.colour_label_list[i].setText('Second Eye: ')
                if i < len(self.colours) - 3 :
                    self.colour_label_list[i].setText('Tail Point {0}: '.format(i + 1))
                self.colour_textbox_list[i].setText('{0}'.format(self.colours[i]))
    def update_background_from_thread(self):
        self.background = self.calculate_background_progress_window.background
        self.background_path = 'Background calculated and loaded into memory/Background calculated and loaded into memory'
        self.get_background_attributes()
        self.update_descriptors()
        self.update_preview_parameters(activate = True)
        self.update_tracking_parameters(activate = True)
        self.update_tracking_parameters_buttons(activate = True)
        self.update_colour_parameters(activate = True)
        self.update_colour_parameters_buttons(activate = True)
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
    def update_loaded_videos_buttons(self, activate = False, inactivate = False):
        if activate:
            if not self.remove_selected_video_button.isEnabled():
                self.remove_selected_video_button.setEnabled(True)
            if not self.remove_all_videos_button.isEnabled():
                self.remove_all_videos_button.setEnabled(True)
            if not self.load_background_button.isEnabled():
                self.load_background_button.setEnabled(True)
            if not self.calculate_background_button.isEnabled():
                self.calculate_background_button.setEnabled(True)
            if not self.update_parameters_button.isEnabled():
                self.update_parameters_button.setEnabled(True)
            if not self.reload_parameters_button.isEnabled():
                self.reload_parameters_button.setEnabled(True)
            if not self.track_selected_video_button.isEnabled():
                self.track_selected_video_button.setEnabled(True)
            if not self.track_all_videos_button.isEnabled():
                self.track_all_videos_button.setEnabled(True)
        if inactivate:
            if self.remove_selected_video_button.isEnabled():
                self.remove_selected_video_button.setEnabled(False)
            if self.remove_all_videos_button.isEnabled():
                self.remove_all_videos_button.setEnabled(False)
            if self.load_background_button.isEnabled():
                self.load_background_button.setEnabled(False)
            if self.calculate_background_button.isEnabled():
                self.calculate_background_button.setEnabled(False)
            if self.update_parameters_button.isEnabled():
                self.update_parameters_button.setEnabled(False)
            if self.reload_parameters_button.isEnabled():
                self.reload_parameters_button.setEnabled(False)
            if self.track_selected_video_button.isEnabled():
                self.track_selected_video_button.setEnabled(False)
            if self.track_all_videos_button.isEnabled():
                self.track_all_videos_button.setEnabled(False)
    def update_track_video_buttons(self):
        if not self.track_selected_video_button.isEnabled():
            self.track_selected_video_button.setEnabled(True)
        if not self.track_all_videos_button.isEnabled():
            self.track_all_videos_button.setEnabled(True)

    # Defining Trigger Functions
    def trigger_save_background(self):
        if self.save_path is not None:
            if self.background is not None and self.background_path == 'Background calculated and loaded into memory/Background calculated and loaded into memory':
                self.background_path = '{0}/{1}_background.tif'.format(self.save_path, self.video_path_basename[:-4])
                ut.save_background_to_file(self.background, self.background_path)
                self.get_background_attributes()
                self.update_descriptors()
        else:
            self.save_path = self.video_path_folder
            self.background_path = '{0}/{1}_background.tif'.format(self.save_path, self.video_path_basename[:-4])
            ut.save_background_to_file(self.background, self.background_path)
            self.get_background_attributes()
            self.update_descriptors()
    def trigger_calculate_background(self):
        self.calculate_background_progress_window = CalculateBackgroundProgressWindow()
        self.calculate_background_progress_window.video_path = self.video_path
        self.calculate_background_progress_window.background_calculation_method = self.background_calculation_method
        self.calculate_background_progress_window.background_calculation_frame_chunk_width = self.background_calculation_frame_chunk_width
        self.calculate_background_progress_window.background_calculation_frame_chunk_height = self.background_calculation_frame_chunk_height
        self.calculate_background_progress_window.background_calculation_frames_to_skip = self.background_calculation_frames_to_skip
        self.calculate_background_progress_window.save_path = self.save_path
        self.calculate_background_progress_window.save_background = self.save_background
        self.calculate_background_progress_window.video_n_frames = self.video_n_frames
        self.calculate_background_progress_window.update_processing_video_label()
        self.calculate_background_progress_window.update_progress_bar_range()
        self.calculate_background_progress_window.show()
        self.calculate_background_progress_window.trigger_calculate_background()
        self.calculate_background_progress_window.background_calculation_completed_signal.connect(self.update_background_from_thread)
    def trigger_select_save_path(self):
        self.save_path = QFileDialog.getExistingDirectory(self, 'Select save path.')
        if self.save_path:
            self.update_descriptors()
    def trigger_load_background(self):
        self.background_path, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","Image Files (*.tif)", options=QFileDialog.Options())
        if self.background_path:
            self.background = ut.load_background_into_memory(self.background_path)
            self.get_background_attributes()
            self.update_descriptors()
            if self.video_path:
                self.update_preview_parameters(activate = True)
                self.update_tracking_parameters(activate = True)
                self.update_tracking_parameters_buttons(activate = True)
                self.update_colour_parameters(activate = True)
                self.update_colour_parameters_buttons(activate = True)
            else:
                self.update_preview_parameters(activate_preview_background = True)
    def trigger_open_video(self):
        self.trigger_update_parameters()
        self.video_path, _ = QFileDialog.getOpenFileName(self,"Open Video File", "","Video Files (*.avi; *.mp4)", options=QFileDialog.Options())
        if self.video_path:
            self.frame_number = 1
            self.background = None
            self.background_path = None
            self.background_path_basename = None
            self.update_preview_parameters(inactivate = True)
            self.trigger_load_default_tracking_parameters()
            self.update_colours()
            self.trigger_load_default_colours()
            self.update_colours()
            self.video_path.replace('/', '\\')
            self.get_video_attributes()
            self.update_descriptors()
            if len(self.loaded_videos_and_parameters_dict) == 0:
                self.loaded_videos_and_parameters_dict[self.video_path] = {     'descriptors'           :   None,
                                                                                'tracking_parameters'   :   None,
                                                                                'colour_parameters'     :   None,
                                                                                'background'            :   None,
                                                                                'mask'                  :   None    }
                self.loaded_videos_listbox.addItem(self.video_path)
                self.loaded_videos_listbox.setCurrentRow(0)
            else:
                if self.video_path not in self.loaded_videos_and_parameters_dict.keys():
                    self.loaded_videos_and_parameters_dict[self.video_path] = { 'descriptors'           :   None,
                                                                                'tracking_parameters'   :   None,
                                                                                'colour_parameters'     :   None,
                                                                                'background'            :   None,
                                                                                'mask'                  :   None    }
                    self.loaded_videos_listbox.addItem(self.video_path)
                    self.loaded_videos_listbox.setCurrentRow(self.loaded_videos_listbox.count() - 1)
                else:
                    self.loaded_videos_listbox.setCurrentRow(list(self.loaded_videos_and_parameters_dict.keys()).index(self.video_path))
            self.trigger_update_parameters()
            success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
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
                self.update_loaded_videos_buttons(activate = True)
                self.update_tracking_parameters(activate = True)
                self.update_tracking_parameters_buttons(activate = True)
                self.update_colour_parameters(activate = True)
                self.update_colour_parameters_buttons(activate = True)
                if self.background_path:
                    self.update_preview_parameters(activate = True)
    def trigger_update_preview(self, magnify = False, demagnify = False, label_size = None, preview_crop = False):
        if label_size is None:
            label_size = self.preview_frame_window_label_size[0]
        if self.preview_background:
            use_grayscale = True
            if magnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = label_size + 100, grayscale = use_grayscale, preview_crop = preview_crop)
            if demagnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = label_size - 100, grayscale = use_grayscale, preview_crop = preview_crop)
            if not magnify and not demagnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = label_size, grayscale = use_grayscale, preview_crop = preview_crop)
            self.update_preview_frame_window()
            self.update_frame_window_slider(inactivate = True)
            self.update_preview_frame_number_textbox(inactivate = True)
            self.update_video_time_textbox(inactivate = True)
            self.update_video_playback_buttons(inactivate = True)
            self.update_frame_change_buttons(inactivate = True)
            self.update_interactive_frame_buttons(activate = True)
        elif self.preview_eyes_threshold:
            if self.video_path is not None:
                success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
                if success and self.frame is not None:
                    use_grayscale = True
                    if self.tracking_method == 'free_swimming':
                        self.frame = ut.apply_threshold_to_frame(ut.apply_median_blur_to_frame(ut.subtract_background_from_frame(self.frame, self.background)), self.eyes_threshold, invert = self.invert_threshold)
                    elif self.tracking_method == 'head_fixed_1' or self.tracking_method == 'head_fixed_2':
                        self.frame = ut.apply_threshold_to_frame(self.frame, self.eyes_threshold, invert = self.invert_threshold)
                    if magnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size + 100, grayscale = use_grayscale, preview_crop = preview_crop)
                    if demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size - 100, grayscale = use_grayscale, preview_crop = preview_crop)
                    if not magnify and not demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size, grayscale = use_grayscale, preview_crop = preview_crop)
                    self.update_preview_frame_window()
                    self.update_frame_window_slider(activate = True)
                    self.update_preview_frame_number_textbox(activate = True)
                    self.update_video_playback_buttons(activate = True, activate_pause_video_button = True)
                    self.update_frame_change_buttons(activate = True)
                    self.update_interactive_frame_buttons(activate = True)
        else:
            if self.video_path is not None:
                success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
                if success and self.frame is not None:
                    use_grayscale = True
                    if self.preview_background_subtracted_frame:
                        if self.preview_tracking_results:
                            results = ut.track_tail_in_frame(self.frame, self.background, success, self.n_tail_points, self.dist_tail_points, self.dist_eyes, self.dist_swim_bladder, self.pixel_threshold, self.extended_eyes_calculation, self.eyes_threshold, self.median_blur, self.tracking_method, self.initial_pixel_search, self.invert_threshold, self.range_angles)
                            self.frame = ut.subtract_background_from_frame(self.frame, self.background)
                            if results is not None:
                                self.frame = ut.annotate_tracking_results_onto_frame(self.frame, results, self.colours, self.heading_line_length, self.extended_eyes_calculation, self.eyes_line_length)
                                use_grayscale = False
                        else:
                            self.frame = ut.subtract_background_from_frame(self.frame, self.background)
                    elif self.preview_tracking_results:
                        results = ut.track_tail_in_frame(self.frame, self.background, success, self.n_tail_points, self.dist_tail_points, self.dist_eyes, self.dist_swim_bladder, self.pixel_threshold, self.extended_eyes_calculation, self.eyes_threshold, self.median_blur, self.tracking_method, self.initial_pixel_search, self.invert_threshold, self.range_angles)
                        if results is not None:
                            self.frame = ut.annotate_tracking_results_onto_frame(self.frame, results, self.colours, self.heading_line_length, self.extended_eyes_calculation, self.eyes_line_length)
                            use_grayscale = False
                    if magnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size + 100, grayscale = use_grayscale, preview_crop = preview_crop)
                    if demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size - 100, grayscale = use_grayscale, preview_crop = preview_crop)
                    if not magnify and not demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = label_size, grayscale = use_grayscale, preview_crop = preview_crop)
                    self.update_preview_frame_window()
                    self.update_frame_window_slider(activate = True)
                    self.update_preview_frame_number_textbox(activate = True)
                    self.update_video_time_textbox(activate = True)
                    self.update_video_playback_buttons(activate = True)
                    self.update_frame_change_buttons(activate = True)
                    self.update_interactive_frame_buttons(activate = True)
            else:
                self.update_preview_frame_window(clear = True)
    def trigger_load_default_tracking_parameters(self):
        self.tracking_method_combobox.setCurrentIndex(0)
        self.tracking_method = 'free_swimming'
        self.n_tail_points = 7
        self.dist_tail_points = 5
        self.dist_eyes = 4
        self.dist_swim_bladder = 12
        self.starting_frame = 0
        self.n_frames = 'All'
        self.heading_line_length = 5
        self.pixel_threshold = 40
        self.frame_change_threshold = 10
        self.eyes_threshold = 100
        self.eyes_line_length = 5
        self.median_blur = 3
        self.save_video = False
        self.extended_eyes_calculation = False
        self.background_calculation_method = 'brightest'
        self.background_calculation_frame_chunk_width = 250
        self.background_calculation_frame_chunk_height = 250
        self.background_calculation_frames_to_skip = 10
        self.initial_pixel_search = 'brightest'
        self.invert_threshold = False
        self.range_angles = 120
        self.save_background = True
        self.update_tracking_parameters()
        if self.preview_frame:
            self.trigger_update_preview()
    def trigger_load_previous_tracking_parameters(self):
        try:
            tracking_parameters = np.load('saved_parameters\\tracking_parameters.npy').item()
            self.tracking_method = tracking_parameters['tracking_method']
            self.n_tail_points = tracking_parameters['n_tail_points']
            self.dist_tail_points = tracking_parameters['dist_tail_points']
            self.dist_eyes = tracking_parameters['dist_eyes']
            self.dist_swim_bladder = tracking_parameters['dist_swim_bladder']
            self.median_blur = tracking_parameters['median_blur']
            self.starting_frame = tracking_parameters['starting_frame']
            self.n_frames = tracking_parameters['n_frames']
            self.heading_line_length = tracking_parameters['line_length']
            self.pixel_threshold = tracking_parameters['pixel_threshold']
            self.frame_change_threshold = tracking_parameters['frame_change_threshold']
            self.eyes_threshold = tracking_parameters['eyes_threshold']
            self.eyes_line_length = tracking_parameters['eyes_line_length']
            self.save_video = tracking_parameters['save_video']
            self.extended_eyes_calculation = tracking_parameters['extended_eyes_calculation']
            self.background_calculation_method = tracking_parameters['background_calculation_method']
            self.background_calculation_frame_chunk_width = tracking_parameters['background_calculation_frame_chunk_width']
            self.background_calculation_frame_chunk_height = tracking_parameters['background_calculation_frame_chunk_height']
            self.background_calculation_frames_to_skip = tracking_parameters['background_calculation_frames_to_skip']
            self.initial_pixel_search = tracking_parameters['initial_pixel_search']
            self.invert_threshold = tracking_parameters['invert_threshold']
            self.save_background = tracking_parameters['save_background']
            self.update_colours()
            self.update_tracking_parameters()
            self.trigger_update_preview()
        except:
            print('Error: tracking parameters not found.')
            self.trigger_load_default_tracking_parameters()
            self.update_colours()
            self.trigger_load_default_colours()
            self.update_colours()
    def trigger_save_current_tracking_parameters(self):
        tracking_parameters = {'tracking_method' : self.tracking_method, 'n_tail_points' : self.n_tail_points,
            'dist_tail_points' : self.dist_tail_points, 'dist_eyes' : self.dist_eyes, 'dist_swim_bladder' : self.dist_swim_bladder,
            'median_blur' : self.median_blur,
            'starting_frame' : self.starting_frame,
            'n_frames' : self.n_frames, 'line_length' : self.heading_line_length,
            'pixel_threshold' : self.pixel_threshold, 'frame_change_threshold' : self.frame_change_threshold,
            'eyes_threshold' : self.eyes_threshold, 'eyes_line_length' : self.eyes_line_length,
            'save_video' : self.save_video, 'extended_eyes_calculation' : self.extended_eyes_calculation,
            'background_calculation_method' : self.background_calculation_method,
            'background_calculation_frame_chunk_width' : self.background_calculation_frame_chunk_width,
            'background_calculation_frame_chunk_height' : self.background_calculation_frame_chunk_height,
            'background_calculation_frames_to_skip' : self.background_calculation_frames_to_skip,
            'initial_pixel_search' : self.initial_pixel_search, 'invert_threshold' : self.invert_threshold,
            'save_background' : self.save_background}
        np.save('saved_parameters\\tracking_parameters.npy', tracking_parameters)
    def trigger_track_video(self):
        if self.track_selected_video_button.isEnabled():
            self.track_selected_video_button.setEnabled(False)
        if self.track_all_videos_button.isEnabled():
            self.track_all_videos_button.setEnabled(False)

        if self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] is None:
            self.descriptors_dict['video_path_basename'] = self.video_path_basename
            self.descriptors_dict['video_path_folder'] = self.video_path_folder
            self.descriptors_dict['video_n_frames'] = self.video_n_frames
            self.descriptors_dict['video_fps'] = self.video_fps
            self.descriptors_dict['video_frame_width'] = self.video_frame_width
            self.descriptors_dict['video_frame_height'] = self.video_frame_height
            self.descriptors_dict['background_path_basename'] = self.background_path_basename
            self.descriptors_dict['save_path'] = self.save_path
            self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] = self.descriptors_dict.copy()

        if self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'] is None:
            self.tracking_parameters_dict['n_tail_points'] = self.n_tail_points
            self.tracking_parameters_dict['dist_tail_points'] = self.dist_tail_points
            self.tracking_parameters_dict['dist_eyes'] = self.dist_eyes
            self.tracking_parameters_dict['dist_swim_bladder'] = self.dist_swim_bladder
            self.tracking_parameters_dict['tracking_method'] = self.tracking_method
            self.tracking_parameters_dict['save_video'] = self.save_video
            self.tracking_parameters_dict['median_blur'] = self.median_blur
            self.tracking_parameters_dict['extended_eyes_calculation'] = self.extended_eyes_calculation
            self.tracking_parameters_dict['n_frames'] = self.n_frames
            self.tracking_parameters_dict['starting_frame'] = self.starting_frame
            self.tracking_parameters_dict['save_path'] = self.save_path
            self.tracking_parameters_dict['background_path'] = self.background_path
            self.tracking_parameters_dict['save_background'] = self.save_background
            self.tracking_parameters_dict['heading_line_length'] = self.heading_line_length
            self.tracking_parameters_dict['video_fps'] = self.video_fps
            self.tracking_parameters_dict['pixel_threshold'] = self.pixel_threshold
            self.tracking_parameters_dict['frame_change_threshold'] = self.frame_change_threshold
            self.tracking_parameters_dict['eyes_threshold'] = self.eyes_threshold
            self.tracking_parameters_dict['initial_pixel_search'] = self.initial_pixel_search
            self.tracking_parameters_dict['invert_threshold'] = self.invert_threshold
            self.tracking_parameters_dict['range_angles'] = self.range_angles
            self.tracking_parameters_dict['background_calculation_method'] = self.background_calculation_method
            self.tracking_parameters_dict['background_calculation_frame_chunk_width'] = self.background_calculation_frame_chunk_width
            self.tracking_parameters_dict['background_calculation_frame_chunk_height'] = self.background_calculation_frame_chunk_height
            self.tracking_parameters_dict['background_calculation_frames_to_skip'] = self.background_calculation_frames_to_skip
            self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'] = self.tracking_parameters_dict.copy()

        if self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'] is None:
            self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'] = self.colours

        if self.loaded_videos_and_parameters_dict[self.video_path]['background'] is None:
            self.loaded_videos_and_parameters_dict[self.video_path]['background'] = self.background

        if self.loaded_videos_and_parameters_dict[self.video_path]['mask'] is None:
            if self.mask is not None:
                if self.video_frame_width > self.video_frame_height:
                    center_x = (self.mask[0] / self.preview_frame_window_size[0]) * self.video_frame_width
                    center_y = (self.mask[1] / int((self.video_frame_height / self.video_frame_width) * self.preview_frame_window_size[1])) * self.video_frame_height
                    width = (self.mask[2] / self.preview_frame_window_size[0]) * self.video_frame_width
                    height = (self.mask[3] / int((self.video_frame_height / self.video_frame_width) * self.preview_frame_window_size[1])) * self.video_frame_height
                else:
                    center_x = (self.mask[0] / int((self.video_frame_width / self.video_frame_height) * self.preview_frame_window_size[0])) * self.video_frame_width
                    center_y = (self.mask[1] / self.preview_frame_window_size[1]) * self.video_frame_height
                    width = (self.mask[2] / int((self.video_frame_width / self.video_frame_height) * self.preview_frame_window_size[0])) * self.video_frame_width
                    height = (self.mask[3] / self.preview_frame_window_size[1]) * self.video_frame_height
                self.loaded_videos_and_parameters_dict[self.video_path]['mask'] = [center_x, center_y, width, height, self.mask[4]]

        self.track_video_progress_window = TrackVideoProgressWindow()
        self.track_video_progress_window.loaded_videos_and_parameters_dict = self.loaded_videos_and_parameters_dict
        self.track_video_progress_window.show()
        self.track_video_progress_window.trigger_track_video()
        self.track_video_progress_window.track_video_progress_finished.connect(self.update_track_video_buttons)
    def trigger_unload_all_tracking(self):
        if self.preview_background_checkbox.isChecked():
            self.preview_background_checkbox.setChecked(False)
        if self.preview_background_subtracted_frame_checkbox.isChecked():
            self.preview_background_subtracted_frame_checkbox.setChecked(False)
        if self.preview_tracking_results_checkbox.isChecked():
            self.preview_tracking_results_checkbox.setChecked(False)
        if self.save_tracked_video_combobox.currentIndex() == 0:
            self.save_tracked_video_combobox.setCurrentIndex(1)
        if self.extended_eyes_calculation_combobox.currentIndex() == 0:
            self.extended_eyes_calculation_combobox.setCurrentIndex(1)
        for i in range(len(self.colours)):
            self.colour_label_list[-1].deleteLater()
            self.colour_textbox_list[-1].deleteLater()
            self.colour_button_list[-1].deleteLater()
            del(self.colour_label_list[-1])
            del(self.colour_textbox_list[-1])
            del(self.colour_button_list[-1])
        self.loaded_videos_listbox.clear()
        self.initialize_class_variables()
        self.trigger_load_default_tracking_parameters()
        self.update_descriptors()
        self.update_preview_frame_window(clear = True)
        self.update_preview_parameters(inactivate = True)
        self.update_frame_window_slider(inactivate = True)
        self.update_preview_frame_number_textbox(inactivate = True)
        self.update_video_time_textbox(inactivate = True)
        self.update_video_playback_buttons(inactivate = True)
        self.update_frame_change_buttons(inactivate = True)
        self.update_interactive_frame_buttons(inactivate = True)
        self.update_frame_window_slider_position()
        self.update_loaded_videos_buttons(inactivate = True)
        self.update_tracking_parameters(inactivate = True)
        self.update_tracking_parameters_buttons(inactivate = True)
        self.update_colour_parameters_buttons(inactivate = True)
        self.update_colours()
        self.trigger_load_default_colours()
        self.update_colours()
        self.update_colour_parameters(inactivate = True)
    def trigger_update_single_colour(self, id):
        colour = QColorDialog.getColor().getRgb()[0:3]
        colour = (colour[0], colour[1], colour[2])
        self.colours[id] = colour
        self.colour_textbox_list[id].setText('{0}'.format(colour))
        self.trigger_update_preview()
    def trigger_load_default_colours(self):
        self.colours = [[] for i in range(self.n_tail_points + 3)]
        colour_map = cm.gnuplot2
        self.colours[-1] = (0, 170, 0)
        self.colours[-2] = (255, 0, 127)
        self.colours[-3] = (255, 0, 127)
        for i in range(self.n_tail_points):
            colour = colour_map(i / (self.n_tail_points - 1))[:3]
            if i == self.n_tail_points - 1:
                colour = (1, 1, 0.5)
            self.colours[i] = (int(colour[2] * 255), int(colour[1] * 255), int(colour[0] * 255))
    def trigger_load_previous_colours(self):
        try:
            colours = np.load('saved_parameters\\colour_parameters.npy').item()
            self.colours = colours['colours']
            self.update_colours()
            if self.preview_frame:
                self.trigger_update_preview()
        except:
            print('Error: colour parameters not found.')
            self.trigger_load_default_colours()
            self.update_colours()
            if self.preview_frame:
                self.trigger_update_preview()
    def trigger_save_current_colours(self):
        colours = {'colours' : self.colours}
        np.save('saved_parameters\\colour_parameters.npy', colours)
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
    def trigger_unload_selected_video(self):
        if len(self.loaded_videos_and_parameters_dict) > 0:
            if len(self.loaded_videos_and_parameters_dict) == 1:
                self.trigger_unload_all_tracking()
            else:
                index = list(self.loaded_videos_and_parameters_dict.keys()).index(self.video_path)
                self.loaded_videos_listbox.takeItem(index)
                if index == self.loaded_videos_listbox.count():
                    index -= 1
                self.loaded_videos_listbox.setCurrentRow(index)
                self.loaded_videos_and_parameters_dict.pop(self.video_path, None)
                self.video_path = self.loaded_videos_listbox.currentItem().text()
                self.get_video_attributes()
                self.update_descriptors()
                success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
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
    def trigger_track_all_videos(self):
        if self.track_selected_video_button.isEnabled():
            self.track_selected_video_button.setEnabled(False)
        if self.track_all_videos_button.isEnabled():
            self.track_all_videos_button.setEnabled(False)

        self.track_all_videos_progress_window = TrackAllVideosProgressWindow()
        self.track_all_videos_progress_window.loaded_videos_and_parameters_dict = self.loaded_videos_and_parameters_dict
        self.track_all_videos_progress_window.track_all_videos_progress_finished.connect(self.update_track_video_buttons)
        self.track_all_videos_progress_window.show()
        self.track_all_videos_progress_window.trigger_track_all_videos()
    def trigger_update_parameters(self):
        if self.video_path is not None and self.video_path != '':
            self.descriptors_dict['video_path_basename'] = self.video_path_basename
            self.descriptors_dict['video_path_folder'] = self.video_path_folder
            self.descriptors_dict['video_n_frames'] = self.video_n_frames
            self.descriptors_dict['video_fps'] = self.video_fps
            self.descriptors_dict['video_frame_width'] = self.video_frame_width
            self.descriptors_dict['video_frame_height'] = self.video_frame_height
            self.descriptors_dict['background_path_basename'] = self.background_path_basename
            self.descriptors_dict['save_path'] = self.save_path

            self.tracking_parameters_dict['n_tail_points'] = self.n_tail_points
            self.tracking_parameters_dict['dist_tail_points'] = self.dist_tail_points
            self.tracking_parameters_dict['dist_eyes'] = self.dist_eyes
            self.tracking_parameters_dict['dist_swim_bladder'] = self.dist_swim_bladder
            self.tracking_parameters_dict['tracking_method'] = self.tracking_method
            self.tracking_parameters_dict['save_video'] = self.save_video
            self.tracking_parameters_dict['extended_eyes_calculation'] = self.extended_eyes_calculation
            self.tracking_parameters_dict['n_frames'] = self.n_frames
            self.tracking_parameters_dict['starting_frame'] = self.starting_frame
            self.tracking_parameters_dict['median_blur'] = self.median_blur
            self.tracking_parameters_dict['save_path'] = self.save_path
            self.tracking_parameters_dict['background_path'] = self.background_path
            self.tracking_parameters_dict['save_background'] = self.save_background
            self.tracking_parameters_dict['heading_line_length'] = self.heading_line_length
            self.tracking_parameters_dict['video_fps'] = self.video_fps
            self.tracking_parameters_dict['pixel_threshold'] = self.pixel_threshold
            self.tracking_parameters_dict['frame_change_threshold'] = self.frame_change_threshold
            self.tracking_parameters_dict['eyes_threshold'] = self.eyes_threshold
            self.tracking_parameters_dict['eyes_line_length'] = self.eyes_line_length
            self.tracking_parameters_dict['initial_pixel_search'] = self.initial_pixel_search
            self.tracking_parameters_dict['invert_threshold'] = self.invert_threshold
            self.tracking_parameters_dict['range_angles'] = self.range_angles
            self.tracking_parameters_dict['background_calculation_method'] = self.background_calculation_method
            self.tracking_parameters_dict['background_calculation_frame_chunk_width'] = self.background_calculation_frame_chunk_width
            self.tracking_parameters_dict['background_calculation_frame_chunk_height'] = self.background_calculation_frame_chunk_height
            self.tracking_parameters_dict['background_calculation_frames_to_skip'] = self.background_calculation_frames_to_skip

            self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] = self.descriptors_dict.copy()
            self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'] = self.tracking_parameters_dict.copy()
            self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'] = self.colours.copy()
            if self.background is not None:
                self.loaded_videos_and_parameters_dict[self.video_path]['background'] = self.background.copy()
            if self.mask is not None:
                if self.video_frame_width > self.video_frame_height:
                    center_x = (self.mask[0] / self.preview_frame_window_size[0]) * self.video_frame_width
                    center_y = (self.mask[1] / int((self.video_frame_height / self.video_frame_width) * self.preview_frame_window_size[1])) * self.video_frame_height
                    width = (self.mask[2] / self.preview_frame_window_size[0]) * self.video_frame_width
                    height = (self.mask[3] / int((self.video_frame_height / self.video_frame_width) * self.preview_frame_window_size[1])) * self.video_frame_height
                else:
                    center_x = (self.mask[0] / int((self.video_frame_width / self.video_frame_height) * self.preview_frame_window_size[0])) * self.video_frame_width
                    center_y = (self.mask[1] / self.preview_frame_window_size[1]) * self.video_frame_height
                    width = (self.mask[2] / int((self.video_frame_width / self.video_frame_height) * self.preview_frame_window_size[0])) * self.video_frame_width
                    height = (self.mask[3] / self.preview_frame_window_size[1]) * self.video_frame_height
                self.loaded_videos_and_parameters_dict[self.video_path]['mask'] = [center_x, center_y, width, height, self.mask[4]]
    def trigger_reload_parameters(self):
        if self.video_path is not None and self.video_path != '':

            self.descriptors_dict = self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'].copy()
            self.tracking_parameters_dict = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'].copy()
            self.colours = self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'].copy()
            self.update_colours()
            self.background = self.loaded_videos_and_parameters_dict[self.video_path]['background'].copy()
            self.mask = self.loaded_videos_and_parameters_dict[self.video_path]['mask'].copy()

            self.video_path_basename = self.descriptors_dict['video_path_basename']
            self.video_path_folder = self.descriptors_dict['video_path_folder']
            self.video_n_frames = self.descriptors_dict['video_n_frames']
            self.video_fps = self.descriptors_dict['video_fps']
            self.video_frame_width = self.descriptors_dict['video_frame_width']
            self.video_frame_height = self.descriptors_dict['video_frame_height']
            self.background_path_basename = self.descriptors_dict['background_path_basename']
            self.save_path = self.descriptors_dict['save_path']
            self.update_descriptors()

            self.n_tail_points = self.tracking_parameters_dict['n_tail_points']
            self.dist_tail_points = self.tracking_parameters_dict['dist_tail_points']
            self.dist_eyes = self.tracking_parameters_dict['dist_eyes']
            self.dist_swim_bladder = self.tracking_parameters_dict['dist_swim_bladder']
            self.tracking_method = self.tracking_parameters_dict['tracking_method']
            self.save_video = self.tracking_parameters_dict['save_video']
            self.extended_eyes_calculation = self.tracking_parameters_dict['extended_eyes_calculation']
            self.n_frames = self.tracking_parameters_dict['n_frames']
            self.starting_frame = self.tracking_parameters_dict['starting_frame']
            self.median_blur = self.tracking_parameters_dict['median_blur']
            self.save_path = self.tracking_parameters_dict['save_path']
            self.background_path = self.tracking_parameters_dict['background_path']
            self.heading_line_length = self.tracking_parameters_dict['heading_line_length']
            self.video_fps = self.tracking_parameters_dict['video_fps']
            self.pixel_threshold = self.tracking_parameters_dict['pixel_threshold']
            self.frame_change_threshold = self.tracking_parameters_dict['frame_change_threshold']
            self.eyes_threshold = self.tracking_parameters_dict['eyes_threshold']
            self.initial_pixel_search = self.tracking_parameters_dict['initial_pixel_search']
            self.invert_threshold = self.tracking_parameters_dict['invert_threshold']
            self.range_angles = self.tracking_parameters_dict['range_angles']
            self.background_calculation_method = self.tracking_parameters_dict['background_calculation_method']
            self.background_calculation_frame_chunk_width = self.tracking_parameters_dict['background_calculation_frame_chunk_width']
            self.background_calculation_frame_chunk_height = self.tracking_parameters_dict['background_calculation_frame_chunk_height']
            self.background_calculation_frames_to_skip = self.tracking_parameters_dict['background_calculation_frames_to_skip']
            self.update_tracking_parameters()
    def trigger_open_videos_from_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select folder to add videos.')
        if folder:
            filenames = ut.filenames_from_folder(folder, filename_ends_with = ['.avi', '.mp4'])
            if len(filenames) > 0:
                self.frame_number = 1
                self.background = None
                self.background_path = None
                self.background_path_basename = None
                if len(filenames) == 1:
                    self.video_path = filenames
                    self.update_preview_parameters(inactivate = True)
                    self.trigger_load_default_tracking_parameters()
                    self.update_colours()
                    self.trigger_load_default_colours()
                    self.update_colours()
                    self.video_path.replace('/', '\\')
                    self.get_video_attributes()
                    self.update_descriptors()
                    if len(self.loaded_videos_and_parameters_dict) == 0:
                        self.loaded_videos_and_parameters_dict[self.video_path] = {     'descriptors'           :   None,
                                                                                        'tracking_parameters'   :   None,
                                                                                        'colour_parameters'     :   None,
                                                                                        'background'            :   None,
                                                                                        'mask'                  :   None    }
                        self.loaded_videos_listbox.addItem(self.video_path)
                        self.loaded_videos_listbox.setCurrentRow(0)
                    else:
                        if self.video_path not in self.loaded_videos_and_parameters_dict.keys():
                            self.loaded_videos_and_parameters_dict[self.video_path] = { 'descriptors'           :   None,
                                                                                        'tracking_parameters'   :   None,
                                                                                        'colour_parameters'     :   None,
                                                                                        'background'            :   None,
                                                                                        'mask'                  :   None    }
                            self.loaded_videos_listbox.addItem(self.video_path)
                            self.loaded_videos_listbox.setCurrentRow(self.loaded_videos_listbox.count() - 1)
                        else:
                            self.loaded_videos_listbox.setCurrentRow(list(self.loaded_videos_and_parameters_dict.keys()).index(self.video_path))
                    self.trigger_update_parameters()
                    success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
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
                        self.update_loaded_videos_buttons(activate = True)
                        self.update_tracking_parameters(activate = True)
                        self.update_tracking_parameters_buttons(activate = True)
                        self.update_colour_parameters(activate = True)
                        self.update_colour_parameters_buttons(activate = True)
                        if self.background_path:
                            self.update_preview_parameters(activate = True)
                else:
                    for i in range(len(filenames)):
                        self.video_path = filenames[i]
                        self.video_path.replace('/', '\\')
                        if i == len(filenames) - 1:
                            self.update_preview_parameters(inactivate = True)
                            self.trigger_load_default_tracking_parameters()
                            self.update_colours()
                            self.trigger_load_default_colours()
                            self.update_colours()
                            self.get_video_attributes()
                            self.update_descriptors()
                            if self.video_path not in self.loaded_videos_and_parameters_dict.keys():
                                self.loaded_videos_and_parameters_dict[self.video_path] = { 'descriptors'           :   None,
                                                                                            'tracking_parameters'   :   None,
                                                                                            'colour_parameters'     :   None,
                                                                                            'background'            :   None,
                                                                                            'mask'                  :   None    }
                                self.loaded_videos_listbox.addItem(self.video_path)
                                self.loaded_videos_listbox.setCurrentRow(self.loaded_videos_listbox.count() - 1)
                            else:
                                self.loaded_videos_listbox.setCurrentRow(list(self.loaded_videos_and_parameters_dict.keys()).index(self.video_path))
                            self.trigger_update_parameters()
                            success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
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
                                self.update_loaded_videos_buttons(activate = True)
                                self.update_tracking_parameters(activate = True)
                                self.update_tracking_parameters_buttons(activate = True)
                                self.update_colour_parameters(activate = True)
                                self.update_colour_parameters_buttons(activate = True)
                                if self.background_path:
                                    self.update_preview_parameters(activate = True)
                        else:
                            self.loaded_videos_and_parameters_dict[self.video_path] = { 'descriptors'           :   None,
                                                                                        'tracking_parameters'   :   None,
                                                                                        'colour_parameters'     :   None,
                                                                                        'background'            :   None,
                                                                                        'mask'                  :   None    }
                            self.loaded_videos_listbox.addItem(self.video_path)

    # Defining Check Functions
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
    def check_preview_background_checkbox(self):
        self.preview_background = self.preview_background_checkbox.isChecked()
        self.trigger_update_preview()
    def check_preview_background_subtracted_frame_checkbox(self):
        self.preview_background_subtracted_frame = self.preview_background_subtracted_frame_checkbox.isChecked()
        self.trigger_update_preview()
    def check_preview_eyes_threshold_checkbox(self):
        self.preview_eyes_threshold = self.preview_eyes_threshold_checkbox.isChecked()
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
    def check_tracking_method_combobox(self):
        current_index = self.tracking_method_combobox.currentIndex()
        if current_index == 0:
            self.tracking_method = 'free_swimming'
        if current_index == 1:
            self.tracking_method = 'head_fixed_1'
        if current_index == 2:
            self.tracking_method = 'head_fixed_2'
        if self.preview_tracking_results:
            self.trigger_update_preview()
    def check_preview_tracking_results_checkbox(self):
        self.preview_tracking_results = self.preview_tracking_results_checkbox.isChecked()
        self.trigger_update_preview()
    def check_save_background_combobox(self):
        current_index = self.save_background_combobox.currentIndex()
        if current_index == 0:
            self.save_background = True
        if current_index == 1:
            self.save_background = False
    def check_tracking_n_tail_points_textbox(self):
        if self.tracking_n_tail_points_textbox.text().isdigit():
            if int(self.tracking_n_tail_points_textbox.text()) > 0 and int(self.tracking_n_tail_points_textbox.text()) < 15:
                self.n_tail_points = int(self.tracking_n_tail_points_textbox.text())
            elif int(self.tracking_n_tail_points_textbox.text()) >= 15:
                self.n_tail_points = 15
                self.tracking_n_tail_points_textbox.setText('15')
            if self.n_tail_points != len(self.colours) - 3:
                self.update_colours()
            self.trigger_update_preview()
        else:
            self.tracking_n_tail_points_textbox.setText(str(self.n_tail_points))
    def check_tracking_dist_tail_points_textbox(self):
        if self.tracking_dist_tail_points_textbox.text().isdigit():
            self.dist_tail_points = int(self.tracking_dist_tail_points_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_dist_tail_points_textbox.setText(str(self.dist_tail_points))
    def check_tracking_dist_eyes_textbox(self):
        if self.tracking_dist_eyes_textbox.text().isdigit():
            self.dist_eyes = int(self.tracking_dist_eyes_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_dist_eyes_textbox.setText(str(self.dist_eyes))
    def check_tracking_dist_swim_bladder_textbox(self):
        if self.tracking_dist_swim_bladder_textbox.text().isdigit():
            self.dist_swim_bladder = int(self.tracking_dist_swim_bladder_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_dist_swim_bladder_textbox.setText(str(self.dist_swim_bladder))
    def check_tracking_starting_frame_textbox(self):
        if self.tracking_starting_frame_textbox.text().isdigit():
            self.starting_frame = int(self.tracking_starting_frame_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_starting_frame_textbox.setText(str(self.starting_frame))
    def check_tracking_n_frames_textbox(self):
        if self.tracking_n_frames_textbox.text().isdigit():
            self.n_frames = int(self.tracking_n_frames_textbox.text())
        elif self.tracking_n_frames_textbox.text() == 'All':
            self.n_frames = self.tracking_n_frames_textbox.text()
        else:
            self.tracking_n_frames_textbox.setText(str(self.n_frames))
    def check_tracking_line_length_textbox(self):
        if self.tracking_line_length_textbox.text().isdigit():
            self.heading_line_length = int(self.tracking_line_length_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_line_length_textbox.setText(str(self.heading_line_length))
    def check_tracking_pixel_threshold_textbox(self):
        if self.tracking_pixel_threshold_textbox.text().isdigit():
            self.pixel_threshold = int(self.tracking_pixel_threshold_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_pixel_threshold_textbox.setText(str(self.pixel_threshold))
    def check_tracking_frame_change_threshold_textbox(self):
        if self.tracking_frame_change_threshold_textbox.text().isdigit():
            self.frame_change_threshold = int(self.tracking_frame_change_threshold_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.tracking_frame_change_threshold_textbox.setText(str(self.frame_change_threshold))
    def check_eyes_threshold_textbox(self):
        if self.eyes_threshold_textbox.text().isdigit():
            if int(self.eyes_threshold_textbox.text()) > 0 and int(self.eyes_threshold_textbox.text()) <= 255:
                self.eyes_threshold = int(self.eyes_threshold_textbox.text())
            elif int(self.eyes_threshold_textbox.text()) > 255:
                self.eyes_threshold = 255
                self.eyes_threshold_textbox.setText('255')
            if self.preview_tracking_results or self.preview_eyes_threshold:
                self.trigger_update_preview()
        else:
            self.eyes_threshold_textbox.setText(str(self.eyes_threshold))
    def check_eyes_line_length_textbox(self):
        if self.eyes_line_length_textbox.text().isdigit():
            self.eyes_line_length = int(self.eyes_line_length_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.eyes_line_length_textbox.setText(str(self.eyes_line_length))
    def check_load_default_tracking_parameters_button(self):
        self.trigger_load_default_tracking_parameters()
        self.update_colours()
    def check_load_default_colours_button(self):
        self.trigger_load_default_colours()
        self.update_colours()
        self.trigger_update_preview()
    def check_save_tracked_video_combobox(self):
        current_index = self.save_tracked_video_combobox.currentIndex()
        if current_index == 0:
            self.save_video = True
        if current_index == 1:
            self.save_video = False
    def check_extended_eyes_calculation_combobox(self):
        current_index = self.extended_eyes_calculation_combobox.currentIndex()
        if current_index == 0:
            self.extended_eyes_calculation = True
        if current_index == 1:
            self.extended_eyes_calculation = False
        if self.preview_tracking_results:
            self.trigger_update_preview()
    def check_magnify_frame_button(self):
        if self.magnify_frame_button.isChecked():
            self.magnify_frame = True
            if self.pan_frame_button.isChecked():
                self.pan_frame = False
                self.pan_frame_button.setChecked(False)
            if self.elliptical_crop_frame_button.isChecked():
                self.elliptical_crop_frame = False
                self.elliptical_crop_frame_button.setChecked(False)
            if self.rectangular_crop_frame_button.isChecked():
                self.rectangular_crop_frame = False
                self.rectangular_crop_frame_button.setChecked(False)
        else:
            self.magnify_frame = False
    def check_pan_frame_button(self):
        if self.pan_frame_button.isChecked():
            self.pan_frame = True
            if self.magnify_frame_button.isChecked():
                self.magnify_frame = False
                self.magnify_frame_button.setChecked(False)
            if self.elliptical_crop_frame_button.isChecked():
                self.elliptical_crop_frame = False
                self.elliptical_crop_frame_button.setChecked(False)
            if self.rectangular_crop_frame_button.isChecked():
                self.rectangular_crop_frame = False
                self.rectangular_crop_frame_button.setChecked(False)
        else:
            self.pan_frame = False
    def check_elliptical_crop_frame_button(self):
        if self.elliptical_crop_frame_button.isChecked():
            self.elliptical_crop_frame = True
            if self.magnify_frame_button.isChecked():
                self.magnify_frame = False
                self.magnify_frame_button.setChecked(False)
            if self.pan_frame_button.isChecked():
                self.pan_frame = False
                self.pan_frame_button.setChecked(False)
            if self.rectangular_crop_frame_button.isChecked():
                self.rectangular_crop_frame = False
                self.rectangular_crop_frame_button.setChecked(False)
            self.trigger_update_preview(label_size = self.video_frame_width, preview_crop = True)
            self.update_preview_frame_window_scroll_bars()
        else:
            self.elliptical_crop_frame = False
    def check_rectangular_crop_frame_button(self):
        if self.rectangular_crop_frame_button.isChecked():
            self.rectangular_crop_frame = True
            if self.magnify_frame_button.isChecked():
                self.magnify_frame = False
                self.magnify_frame_button.setChecked(False)
            if self.pan_frame_button.isChecked():
                self.pan_frame = False
                self.pan_frame_button.setChecked(False)
            if self.elliptical_crop_frame_button.isChecked():
                self.elliptical_crop_frame = False
                self.elliptical_crop_frame_button.setChecked(False)
            self.trigger_update_preview(label_size = self.video_frame_width, preview_crop = True)
            self.update_preview_frame_window_scroll_bars()
        else:
            self.rectangular_crop_frame = False
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
    def check_median_blur_textbox(self):
        if self.median_blur_textbox.text().isdigit():
            self.median_blur = int(self.median_blur_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.median_blur_textbox.setText(str(self.median_blur))
    def check_background_calculation_method_combobox(self):
        current_index = self.background_calculation_method_combobox.currentIndex()
        if current_index == 0:
            self.background_calculation_method = 'brightest'
        if current_index == 1:
            self.background_calculation_method = 'darkest'
        if current_index == 2:
            self.background_calculation_method = 'mode'
    def check_background_calculation_frame_chunk_width_textbox(self):
        if self.background_calculation_frame_chunk_width_textbox.text().isdigit():
            self.background_calculation_frame_chunk_width = int(self.background_calculation_frame_chunk_width_textbox.text())
        else:
            self.background_calculation_frame_chunk_width_textbox.setText(str(self.background_calculation_frame_chunk_width))
    def check_background_calculation_frame_chunk_height_textbox(self):
        if self.background_calculation_frame_chunk_height_textbox.text().isdigit():
            self.background_calculation_frame_chunk_height = int(self.background_calculation_frame_chunk_height_textbox.text())
        else:
            self.background_calculation_frame_chunk_height_textbox.setText(str(self.background_calculation_frame_chunk_height))
    def check_background_calculation_frames_to_skip_textbox(self):
        if self.background_calculation_frames_to_skip_textbox.text().isdigit():
            self.background_calculation_frames_to_skip = int(self.background_calculation_frames_to_skip_textbox.text())
        else:
            self.background_calculation_frames_to_skip_textbox.setText(str(self.background_calculation_frames_to_skip))
    def check_initial_pixel_search_combobox(self):
        current_index = self.initial_pixel_search_combobox.currentIndex()
        if current_index == 0:
            self.initial_pixel_search = 'brightest'
        else:
            self.initial_pixel_search = 'darkest'
        if self.preview_tracking_results:
            self.trigger_update_preview()
    def check_add_video_button(self):
        self.trigger_open_video()
    def check_invert_threshold_combobox(self):
        current_index = self.invert_threshold_combobox.currentIndex()
        if current_index == 0:
            self.invert_threshold = True
        else:
            self.invert_threshold = False
        if self.preview_tracking_results or self.preview_eyes_threshold:
            self.trigger_update_preview()
    def check_remove_all_videos_button(self):
        self.trigger_unload_all_tracking()
    def check_loaded_videos_listbox_item_clicked(self):
        self.video_path = self.loaded_videos_listbox.currentItem().text()
        self.get_video_attributes()
        self.update_descriptors()
        success, self.frame = ut.load_frame_into_memory(self.video_path, self.frame_number - 1)
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
    def check_range_angles_textbox(self):
        if self.range_angles_textbox.text().isdigit():
            self.range_angles = int(self.range_angles_textbox.text())
            if self.preview_tracking_results:
                self.trigger_update_preview()
        else:
            self.range_angles_textbox.setText(str(self.range_angles))
    def check_remove_selected_video_button(self):
        self.trigger_unload_selected_video()
    def check_track_selected_video_button(self):
        if self.track_video_progress_window is None:
            if self.video_path:
                self.trigger_track_video()
        elif not self.track_video_progress_window.track_video_thread.isRunning():
            if self.video_path:
                self.trigger_track_video()
    def check_track_all_videos_button(self):
        if len(self.loaded_videos_and_parameters_dict) > 0:
            if len(self.loaded_videos_and_parameters_dict) == 1:
                self.trigger_track_video()
            else:
                self.trigger_track_all_videos()
    def check_update_parameters_button(self):
        self.trigger_update_parameters()
    def check_reload_parameters_button(self):
        self.trigger_reload_parameters()
    def check_add_videos_from_folder_button(self):
        self.trigger_open_videos_from_folder()

    # Defining Event Functions
    def event_preview_frame_window_label_mouse_clicked(self, event):
        if self.magnify_frame:
            self.initial_mouse_position = (event.x(), event.y())
            if qApp.mouseButtons() & Qt.LeftButton:
                self.trigger_update_preview(magnify = True)
            elif qApp.mouseButtons() & Qt.RightButton:
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
        if self.pan_frame or self.elliptical_crop_frame or self.rectangular_crop_frame:
            self.initial_mouse_position = [event.x(), event.y()]
        if self.mask:
            if abs(self.mask[2]) * (self.preview_frame_window_size[0] / self.video_frame_width) > 6 and abs(self.mask[3]) * (self.preview_frame_window_size[1] / self.video_frame_height) > 6:
                if abs(event.x() - self.mask[0]) <= 3 * self.preview_frame_window_size[0] / self.video_frame_width and abs(event.y() - self.mask[1]) <= 3 * self.preview_frame_window_size[1] / self.video_frame_height:
                    self.pan_crop = True
                else:
                    self.pan_crop = False
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
        if self.elliptical_crop_frame or self.rectangular_crop_frame:
            if qApp.mouseButtons() & Qt.LeftButton:
                if not self.pan_crop:
                    center_x = self.initial_mouse_position[0] + (event.x() - self.initial_mouse_position[0]) / 2
                    center_y = self.initial_mouse_position[1] + (event.y() - self.initial_mouse_position[1]) / 2
                    width = (event.x() - self.initial_mouse_position[0]) / 2
                    height = (event.y() - self.initial_mouse_position[1]) / 2
                    if width != 0 and height != 0:
                        if self.elliptical_crop_frame:
                            self.mask = [center_x, center_y, width, height, 'ellipse']
                        if self.rectangular_crop_frame:
                            self.mask = [center_x, center_y, width, height, 'rectangle']
                else:
                    center_x = event.x()
                    center_y = event.y()
                    width = self.mask[2]
                    height = self.mask[3]
                    if width != 0 and height != 0:
                        if self.elliptical_crop_frame:
                            self.mask = [center_x, center_y, width, height, 'ellipse']
                        if self.rectangular_crop_frame:
                            self.mask = [center_x, center_y, width, height, 'rectangle']
                self.trigger_update_preview(preview_crop = True)
        event.accept()
    def event_preview_frame_window_wheel_scrolled(self, event):
        event.ignore()
