'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import sys
import os
import cv2
import numpy as np
import utilities as ut
import matplotlib.cm as cm
import time
import threading
from functools import partial
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        super(MainWindow, self).__init__(parent)
        self.get_main_window_attributes()
        self.add_menubar()
        self.add_tracking_options_to_menubar()
        self.add_plotting_options_to_menubar()
        self.main_tab = MainTab(self.main_window_width, self.main_window_height)
        self.setCentralWidget(self.main_tab)
        self.setMenuBar(self.menubar)
        self.setWindowTitle('Zebrafish Behaviour Tracking')
        self.setWindowState(Qt.WindowMaximized)
        self.show()

    def add_menubar(self):
        self.menubar = QMenuBar()
        self.menubar.resize(self.main_window_width, self.menubar.height())
    def get_main_window_attributes(self):
        self.main_window_width = QDesktopWidget().availableGeometry().width()
        self.main_window_height = QDesktopWidget().availableGeometry().height()
    def add_tracking_options_to_menubar(self):
        self.tracking_options_menu = self.menubar.addMenu('&Tracking Options')

        self.open_video_action = QAction('&Open Video', self)
        self.open_video_action.setShortcut('Ctrl+O')
        self.open_video_action.setStatusTip('Open Video')
        self.open_video_action.triggered.connect(self.trigger_open_video)
        self.tracking_options_menu.addAction(self.open_video_action)

        self.select_save_path_action = QAction('&Select Save Path', self)
        self.select_save_path_action.setShortcut('Ctrl+P')
        self.select_save_path_action.setStatusTip('Select Save Path')
        self.select_save_path_action.triggered.connect(self.trigger_select_save_path)
        self.tracking_options_menu.addAction(self.select_save_path_action)

        self.load_background_action = QAction('&Load Background', self)
        self.load_background_action.setShortcut('Ctrl+L')
        self.load_background_action.setStatusTip('Load Background')
        self.load_background_action.triggered.connect(self.trigger_load_background)
        self.tracking_options_menu.addAction(self.load_background_action)

        self.calculate_background_action = QAction('&Calculate Background', self)
        self.calculate_background_action.setShortcut('Ctrl+B')
        self.calculate_background_action.setStatusTip('Calculate Background')
        self.calculate_background_action.triggered.connect(self.trigger_calculate_background)
        self.tracking_options_menu.addAction(self.calculate_background_action)

        self.save_background_action = QAction('&Save Background', self)
        self.save_background_action.setShortcut('Ctrl+S')
        self.save_background_action.setStatusTip('Save Background')
        self.save_background_action.triggered.connect(self.trigger_save_background)
        self.tracking_options_menu.addAction(self.save_background_action)

        self.unload_all_tracking_action = QAction('&Unload All Tracking', self)
        self.unload_all_tracking_action.setShortcut('Ctrl+U')
        self.unload_all_tracking_action.setStatusTip('Unload All Tracking From Memory')
        self.unload_all_tracking_action.triggered.connect(self.trigger_unload_all_tracking)
        self.tracking_options_menu.addAction(self.unload_all_tracking_action)
    def add_plotting_options_to_menubar(self):
        self.plotting_options_menu = self.menubar.addMenu('&Plotting Options')

        self.load_tracking_results_action = QAction('&Load Tracking Results')
        self.load_tracking_results_action.setStatusTip('Load Tracking Results')
        self.load_tracking_results_action.triggered.connect(self.trigger_load_tracking_results)
        self.plotting_options_menu.addAction(self.load_tracking_results_action)

        self.open_tracked_video_action = QAction('&Open Tracked Video', self)
        self.open_tracked_video_action.setShortcut('Ctrl+T')
        self.open_tracked_video_action.setStatusTip('Open Tracked Video')
        self.open_tracked_video_action.triggered.connect(self.trigger_open_tracked_video)
        self.plotting_options_menu.addAction(self.open_tracked_video_action)

        self.unload_all_plotting_action = QAction('&Unload All Plotting', self)
        self.unload_all_plotting_action.setStatusTip('Unload All Plotting')
        self.unload_all_plotting_action.triggered.connect(self.trigger_unload_all_plotting)
        self.plotting_options_menu.addAction(self.unload_all_plotting_action)

    def trigger_save_background(self):
        self.main_tab.tracking_window.tracking_content.trigger_save_background()
    def trigger_calculate_background(self):
        self.main_tab.tracking_window.tracking_content.trigger_calculate_background()
    def trigger_select_save_path(self):
        self.main_tab.tracking_window.tracking_content.trigger_select_save_path()
    def trigger_load_background(self):
        self.main_tab.tracking_window.tracking_content.trigger_load_background()
    def trigger_open_video(self):
        self.main_tab.tracking_window.tracking_content.trigger_open_video()
    def trigger_open_tracked_video(self):
        self.main_tab.plotting_window.plotting_content.trigger_open_video()
    def trigger_unload_all_tracking(self):
        self.main_tab.tracking_window.tracking_content.trigger_unload_all_tracking()
    def trigger_load_tracking_results(self):
        self.main_tab.plotting_window.plotting_content.trigger_load_tracking_results()
    def trigger_unload_all_plotting(self):
        self.main_tab.plotting_window.plotting_content.trigger_unload_all_plotting()

    # Defining Event Functions
    def closeEvent(self, event):
        if self.main_tab.tracking_window.tracking_content.calculate_background_progress_window is not None:
            if self.main_tab.tracking_window.tracking_content.calculate_background_progress_window.isVisible():
                self.main_tab.tracking_window.tracking_content.calculate_background_progress_window.close()
        if self.main_tab.tracking_window.tracking_content.track_video_progress_window is not None:
            if self.main_tab.tracking_window.tracking_content.track_video_progress_window.isVisible():
                self.main_tab.tracking_window.tracking_content.track_video_progress_window.close()
        if self.main_tab.tracking_window.tracking_content.track_all_videos_progress_window is not None:
            if self.main_tab.tracking_window.tracking_content.track_all_videos_progress_window.isVisible():
                self.main_tab.tracking_window.tracking_content.track_all_videos_progress_window.close()
        event.accept()

class MainTab(QTabWidget):

    def __init__(self, main_window_width, main_window_height):
        super(MainTab, self).__init__()
        self.main_window_width = main_window_width
        self.main_window_height = main_window_height
        self.tracking_window = TrackingWindow(self.main_window_width, self.main_window_height)
        self.addTab(self.tracking_window,"Tracking")
        self.plotting_window = PlottingWindow()
        self.addTab(self.plotting_window, "Plotting")

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
        # self.add_status_window()
        # self.add_statuses_to_window()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.resize(self.tracking_content_size[0], self.tracking_content_size[1])
    def initialize_layout(self):
        self.font_title = QFont()
        self.font_text = QFont()
        self.font_loaded_videos_buttons = QFont()
        self.font_colour_parameters = QFont()

        if self.main_window_width == 1920 and self.main_window_height == 1020:
            self.font_title.setPointSize(14)
            self.font_text.setPointSize(8)
            self.font_colour_parameters.setPointSize(7)
            self.font_loaded_videos_buttons.setPointSize(7)
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
            self.video_playback_button_size = (50, 50)
            self.video_playback_button_x_offset = 30
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
        self.preview_frame_window.wheelEvent = self.event_preview_frame_window_wheel_scrolled
        self.preview_frame_window.setWidget(self.preview_frame_window_label)
    def add_loaded_videos_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = (self.main_window_y_offset / 1400) * self.main_window_height
        new_width = (self.loaded_videos_window_size[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_window_size[1] / 1400) * self.main_window_height

        self.loaded_videos_window = QLabel(self)
        self.loaded_videos_window.setFrameShape(QFrame.StyledPanel)
        # self.loaded_videos_window.setFrameShadow(QFrame.Sunken)
        # self.loaded_videos_window.setLineWidth(5)
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
        # self.loaded_videos_listbox = QTableWidget(self)
        self.loaded_videos_listbox.setFrameShape(QFrame.StyledPanel)
        # self.loaded_videos_listbox.setFrameShadow(QFrame.Sunken)
        # self.loaded_videos_listbox.setLineWidth(5)
        self.loaded_videos_listbox.move(new_x, new_y)
        self.loaded_videos_listbox.resize(new_width, new_height)
        # self.loaded_videos_listbox.setEnabled(False)
        self.setStyleSheet( """QListWidget{background-color: rgb(240, 240, 240);}""")
        # self.loaded_videos_listbox.setColumnCount(3)
        # self.loaded_videos_listbox.setColumnWidth(0, 301)
        # self.loaded_videos_listbox.setHorizontalHeaderLabels(['Video Name', 'Parameters Set', 'Tracking Status'])
        # self.loaded_videos_listbox.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        # self.setStyleSheet( """QTableWidget{background-color: rgb(240, 240, 240);}""")
        self.loaded_videos_listbox.itemClicked.connect(self.check_loaded_videos_listbox_item_clicked)
    def add_loaded_videos_buttons(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (0 * (self.loaded_videos_button_size[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.loaded_videos_y_offset + self.loaded_videos_listbox_size[1] + (0 * (self.loaded_videos_y_spacing + self.loaded_videos_button_size[1])) + self.loaded_videos_y_spacing) / 1400) * self.main_window_height
        new_width = (self.loaded_videos_button_size[0] / 2560) * self.main_window_width
        new_height = (self.loaded_videos_button_size[1] / 1400) * self.main_window_height

        self.add_video_button = QPushButton('Add Video', self)
        self.add_video_button.move(new_x, new_y)
        self.add_video_button.resize(new_width, new_height)
        self.add_video_button.setFont(self.font_loaded_videos_buttons)
        self.add_video_button.clicked.connect(self.check_add_video_button)

        self.remove_selected_video_button = QPushButton('Remove Selected Video', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (1 * (self.loaded_videos_button_size[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.remove_selected_video_button.move(new_x, new_y)
        self.remove_selected_video_button.resize(new_width, new_height)
        self.remove_selected_video_button.setFont(self.font_loaded_videos_buttons)
        self.remove_selected_video_button.clicked.connect(self.check_remove_selected_video_button)

        self.remove_all_videos_button = QPushButton('Remove All Videos', self)
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing + self.loaded_videos_x_offset + (2 * (self.loaded_videos_button_size[0] + self.loaded_videos_x_spacing))) / 2560) * self.main_window_width
        self.remove_all_videos_button.move(new_x, new_y)
        self.remove_all_videos_button.resize(new_width, new_height)
        self.remove_all_videos_button.setFont(self.font_loaded_videos_buttons)
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
    def add_update_preview_button(self):
        new_x = (self.main_window_x_offset / 2560) * self.main_window_width
        new_y = self.preview_frame_window_size[1] + ((self.main_window_y_offset + self.main_window_spacing + self.preview_frame_window_slider_height + self.preview_frame_number_textbox_y_spacing + self.preview_frame_number_textbox_label_size[1] + self.update_preview_button_y_spacing) / 1400) * self.main_window_height
        new_width = ((self.preview_frame_number_textbox_label_size[0] + self.preview_frame_number_textbox_size[0]) / 2560) * self.main_window_width
        new_height = (self.update_preview_button_height / 1400) * self.main_window_height

        self.update_preview_button = QPushButton('Update Preview', self)
        self.update_preview_button.move(new_x, new_y)
        self.update_preview_button.resize(new_width, new_height)
        self.update_preview_button.setFont(self.font_text)
        self.update_preview_button.clicked.connect(self.check_preview_frame_number_textbox)
        self.update_update_preview_button(inactivate = True)
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
    def add_preview_parameters_window(self):
        new_x = self.preview_frame_window_size[0] + ((self.main_window_x_offset + self.main_window_spacing) / 2560) * self.main_window_width
        new_y = ((self.main_window_y_offset + self.tracking_parameters_window_size[1] + self.main_window_spacing) / 1400) * self.main_window_height
        new_width = (self.preview_parameters_window_size[0] / 2560) * self.main_window_width
        new_height = (self.preview_parameters_window_size[1] / 1400) * self.main_window_height

        self.preview_parameters_window = QLabel(self)
        self.preview_parameters_window.setFrameShape(QFrame.StyledPanel)
        # self.preview_parameters_window.setFrameShadow(QFrame.Sunken)
        # self.preview_parameters_window.setLineWidth(5)
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
        # self.tracking_parameters_window.setFrameShadow(QFrame.Sunken)
        # self.tracking_parameters_window.setLineWidth(5)
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

        self.tracking_method_combobox_label = QLabel(self)
        self.tracking_method_combobox_label.setText('Tracking Method: ')
        self.tracking_method_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_method_combobox_label.setFont(self.font_text)
        self.tracking_method_combobox = QComboBox(self)
        self.tracking_method_combobox.addItem('Free Swimming')
        self.tracking_method_combobox.addItem('Head Fixed')
        self.tracking_method_combobox.setCurrentIndex(0)
        self.tracking_method_combobox.currentIndexChanged.connect(self.check_tracking_method_combobox)
        self.grid_layout.addWidget(self.tracking_method_combobox_label, 5, 1)
        self.grid_layout.addWidget(self.tracking_method_combobox, 5, 2)

        self.tracking_n_tail_points_textbox_label = QLabel(self)
        self.tracking_n_tail_points_textbox_label.setText('Number of Tail Points: ')
        self.tracking_n_tail_points_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_n_tail_points_textbox_label.setFont(self.font_text)
        self.tracking_n_tail_points_textbox = QLineEdit(self)
        self.tracking_n_tail_points_textbox.setText('{0}'.format(self.n_tail_points))
        self.tracking_n_tail_points_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_n_tail_points_textbox.setFont(self.font_text)
        self.tracking_n_tail_points_textbox.returnPressed.connect(self.check_tracking_n_tail_points_textbox)
        self.grid_layout.addWidget(self.tracking_n_tail_points_textbox_label, 6, 1)
        self.grid_layout.addWidget(self.tracking_n_tail_points_textbox, 6, 2)

        self.tracking_dist_tail_points_textbox_label = QLabel(self)
        self.tracking_dist_tail_points_textbox_label.setText('Distance Between Tail Points: ')
        self.tracking_dist_tail_points_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_tail_points_textbox_label.setFont(self.font_text)
        self.tracking_dist_tail_points_textbox = QLineEdit(self)
        self.tracking_dist_tail_points_textbox.setText('{0}'.format(self.dist_tail_points))
        self.tracking_dist_tail_points_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_tail_points_textbox.setFont(self.font_text)
        self.tracking_dist_tail_points_textbox.returnPressed.connect(self.check_tracking_dist_tail_points_textbox)
        self.grid_layout.addWidget(self.tracking_dist_tail_points_textbox_label, 7, 1)
        self.grid_layout.addWidget(self.tracking_dist_tail_points_textbox, 7, 2)

        self.tracking_dist_eyes_textbox_label = QLabel(self)
        self.tracking_dist_eyes_textbox_label.setText('Distance Between Eyes: ')
        self.tracking_dist_eyes_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_eyes_textbox_label.setFont(self.font_text)
        self.tracking_dist_eyes_textbox = QLineEdit(self)
        self.tracking_dist_eyes_textbox.setText('{0}'.format(self.dist_eyes))
        self.tracking_dist_eyes_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_eyes_textbox.setFont(self.font_text)
        self.tracking_dist_eyes_textbox.returnPressed.connect(self.check_tracking_dist_eyes_textbox)
        self.grid_layout.addWidget(self.tracking_dist_eyes_textbox_label, 8, 1)
        self.grid_layout.addWidget(self.tracking_dist_eyes_textbox, 8, 2)

        self.tracking_dist_swim_bladder_textbox_label = QLabel(self)
        self.tracking_dist_swim_bladder_textbox_label.setText('Distance Between Eyes and Swim Bladder: ')
        self.tracking_dist_swim_bladder_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_dist_swim_bladder_textbox_label.setFont(self.font_text)
        self.tracking_dist_swim_bladder_textbox = QLineEdit(self)
        self.tracking_dist_swim_bladder_textbox.setText('{0}'.format(self.dist_swim_bladder))
        self.tracking_dist_swim_bladder_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_dist_swim_bladder_textbox.setFont(self.font_text)
        self.tracking_dist_swim_bladder_textbox.returnPressed.connect(self.check_tracking_dist_swim_bladder_textbox)
        self.grid_layout.addWidget(self.tracking_dist_swim_bladder_textbox_label, 9, 1)
        self.grid_layout.addWidget(self.tracking_dist_swim_bladder_textbox, 9, 2)

        self.tracking_starting_frame_textbox_label = QLabel(self)
        self.tracking_starting_frame_textbox_label.setText('Starting Frame: ')
        self.tracking_starting_frame_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_starting_frame_textbox_label.setFont(self.font_text)
        self.tracking_starting_frame_textbox = QLineEdit(self)
        self.tracking_starting_frame_textbox.setText('{0}'.format(self.starting_frame))
        self.tracking_starting_frame_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_starting_frame_textbox.setFont(self.font_text)
        self.tracking_starting_frame_textbox.returnPressed.connect(self.check_tracking_starting_frame_textbox)
        self.grid_layout.addWidget(self.tracking_starting_frame_textbox_label, 10, 1)
        self.grid_layout.addWidget(self.tracking_starting_frame_textbox, 10, 2)

        self.tracking_n_frames_textbox_label = QLabel(self)
        self.tracking_n_frames_textbox_label.setText('Number of Frames to Track: ')
        self.tracking_n_frames_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_n_frames_textbox_label.setFont(self.font_text)
        self.tracking_n_frames_textbox = QLineEdit(self)
        self.tracking_n_frames_textbox.setText('{0}'.format(self.n_frames))
        self.tracking_n_frames_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_n_frames_textbox.setFont(self.font_text)
        self.tracking_n_frames_textbox.returnPressed.connect(self.check_tracking_n_frames_textbox)
        self.grid_layout.addWidget(self.tracking_n_frames_textbox_label, 11, 1)
        self.grid_layout.addWidget(self.tracking_n_frames_textbox, 11, 2)

        self.tracking_line_length_textbox_label = QLabel(self)
        self.tracking_line_length_textbox_label.setText('Line Length: ')
        self.tracking_line_length_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_line_length_textbox_label.setFont(self.font_text)
        self.tracking_line_length_textbox = QLineEdit(self)
        self.tracking_line_length_textbox.setText('{0}'.format(self.heading_line_length))
        self.tracking_line_length_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_line_length_textbox.setFont(self.font_text)
        self.tracking_line_length_textbox.returnPressed.connect(self.check_tracking_line_length_textbox)
        self.grid_layout.addWidget(self.tracking_line_length_textbox_label, 12, 1)
        self.grid_layout.addWidget(self.tracking_line_length_textbox, 12, 2)

        self.tracking_pixel_threshold_textbox_label = QLabel(self)
        self.tracking_pixel_threshold_textbox_label.setText('Pixel Threshold: ')
        self.tracking_pixel_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_pixel_threshold_textbox_label.setFont(self.font_text)
        self.tracking_pixel_threshold_textbox = QLineEdit(self)
        self.tracking_pixel_threshold_textbox.setText('{0}'.format(self.pixel_threshold))
        self.tracking_pixel_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_pixel_threshold_textbox.setFont(self.font_text)
        self.tracking_pixel_threshold_textbox.returnPressed.connect(self.check_tracking_pixel_threshold_textbox)
        self.grid_layout.addWidget(self.tracking_pixel_threshold_textbox_label, 13, 1)
        self.grid_layout.addWidget(self.tracking_pixel_threshold_textbox, 13, 2)

        self.tracking_frame_change_threshold_textbox_label = QLabel(self)
        self.tracking_frame_change_threshold_textbox_label.setText('Frame Change Threshold: ')
        self.tracking_frame_change_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.tracking_frame_change_threshold_textbox_label.setFont(self.font_text)
        self.tracking_frame_change_threshold_textbox = QLineEdit(self)
        self.tracking_frame_change_threshold_textbox.setText('{0}'.format(self.frame_change_threshold))
        self.tracking_frame_change_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.tracking_frame_change_threshold_textbox.setFont(self.font_text)
        self.tracking_frame_change_threshold_textbox.returnPressed.connect(self.check_tracking_frame_change_threshold_textbox)
        self.grid_layout.addWidget(self.tracking_frame_change_threshold_textbox_label, 14, 1)
        self.grid_layout.addWidget(self.tracking_frame_change_threshold_textbox, 14, 2)

        self.eyes_threshold_textbox_label = QLabel(self)
        self.eyes_threshold_textbox_label.setText('Eyes Threshold: ')
        self.eyes_threshold_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.eyes_threshold_textbox_label.setFont(self.font_text)
        self.eyes_threshold_textbox = QLineEdit(self)
        self.eyes_threshold_textbox.setText('{0}'.format(self.eyes_threshold))
        self.eyes_threshold_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.eyes_threshold_textbox.setFont(self.font_text)
        self.eyes_threshold_textbox.returnPressed.connect(self.check_eyes_threshold_textbox)
        self.grid_layout.addWidget(self.eyes_threshold_textbox_label, 15, 1)
        self.grid_layout.addWidget(self.eyes_threshold_textbox, 15, 2)

        self.eyes_line_length_textbox_label = QLabel(self)
        self.eyes_line_length_textbox_label.setText('Eyes Line Length: ')
        self.eyes_line_length_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.eyes_line_length_textbox_label.setFont(self.font_text)
        self.eyes_line_length_textbox = QLineEdit(self)
        self.eyes_line_length_textbox.setText('{0}'.format(self.eyes_threshold))
        self.eyes_line_length_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.eyes_line_length_textbox.setFont(self.font_text)
        self.eyes_line_length_textbox.returnPressed.connect(self.check_eyes_line_length_textbox)
        self.grid_layout.addWidget(self.eyes_line_length_textbox_label, 16, 1)
        self.grid_layout.addWidget(self.eyes_line_length_textbox, 16, 2)

        self.save_tracked_video_combobox_label = QLabel(self)
        self.save_tracked_video_combobox_label.setText('Save Tracked Video: ')
        self.save_tracked_video_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.save_tracked_video_combobox_label.setFont(self.font_text)
        self.save_tracked_video_combobox = QComboBox(self)
        self.save_tracked_video_combobox.addItem('True')
        self.save_tracked_video_combobox.addItem('False')
        self.save_tracked_video_combobox.setCurrentIndex(1)
        self.save_tracked_video_combobox.currentIndexChanged.connect(self.check_save_tracked_video_combobox)
        self.grid_layout.addWidget(self.save_tracked_video_combobox_label, 17, 1)
        self.grid_layout.addWidget(self.save_tracked_video_combobox, 17, 2)

        self.extended_eyes_calculation_combobox_label = QLabel(self)
        self.extended_eyes_calculation_combobox_label.setText('Extended Eyes Calculation: ')
        self.extended_eyes_calculation_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.extended_eyes_calculation_combobox_label.setFont(self.font_text)
        self.extended_eyes_calculation_combobox = QComboBox(self)
        self.extended_eyes_calculation_combobox.addItem('True')
        self.extended_eyes_calculation_combobox.addItem('False')
        self.extended_eyes_calculation_combobox.setCurrentIndex(1)
        self.extended_eyes_calculation_combobox.currentIndexChanged.connect(self.check_extended_eyes_calculation_combobox)
        self.grid_layout.addWidget(self.extended_eyes_calculation_combobox_label, 18, 1)
        self.grid_layout.addWidget(self.extended_eyes_calculation_combobox, 18, 2)

        self.median_blur_textbox_label = QLabel(self)
        self.median_blur_textbox_label.setText('Median Blur Value: ')
        self.median_blur_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.median_blur_textbox_label.setFont(self.font_text)
        self.median_blur_textbox = QLineEdit(self)
        self.median_blur_textbox.setText('{0}'.format(self.median_blur))
        self.median_blur_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.median_blur_textbox.setFont(self.font_text)
        self.median_blur_textbox.returnPressed.connect(self.check_median_blur_textbox)
        self.grid_layout.addWidget(self.median_blur_textbox_label, 19, 1)
        self.grid_layout.addWidget(self.median_blur_textbox, 19, 2)

        self.initial_pixel_search_combobox_label = QLabel(self)
        self.initial_pixel_search_combobox_label.setText('Initial Pixel Search: ')
        self.initial_pixel_search_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.initial_pixel_search_combobox_label.setFont(self.font_text)
        self.initial_pixel_search_combobox = QComboBox(self)
        self.initial_pixel_search_combobox.addItem('Brightest')
        self.initial_pixel_search_combobox.addItem('Darkest')
        self.initial_pixel_search_combobox.setCurrentIndex(0)
        self.initial_pixel_search_combobox.currentIndexChanged.connect(self.check_initial_pixel_search_combobox)
        self.grid_layout.addWidget(self.initial_pixel_search_combobox_label, 20, 1)
        self.grid_layout.addWidget(self.initial_pixel_search_combobox, 20, 2)

        self.invert_threshold_combobox_label = QLabel(self)
        self.invert_threshold_combobox_label.setText('Invert Eyes Treshold: ')
        self.invert_threshold_combobox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.invert_threshold_combobox_label.setFont(self.font_text)
        self.invert_threshold_combobox = QComboBox(self)
        self.invert_threshold_combobox.addItem('True')
        self.invert_threshold_combobox.addItem('False')
        self.invert_threshold_combobox.setCurrentIndex(0)
        self.invert_threshold_combobox.currentIndexChanged.connect(self.check_invert_threshold_combobox)
        self.grid_layout.addWidget(self.invert_threshold_combobox_label, 21, 1)
        self.grid_layout.addWidget(self.invert_threshold_combobox, 21, 2)

        self.range_angles_textbox_label = QLabel(self)
        self.range_angles_textbox_label.setText('Range of Angles for Tail Calculation: ')
        self.range_angles_textbox_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.range_angles_textbox_label.setFont(self.font_text)
        self.range_angles_textbox = QLineEdit(self)
        self.range_angles_textbox.setText('{0}'.format(self.range_angles))
        self.range_angles_textbox.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.range_angles_textbox.setFont(self.font_text)
        self.range_angles_textbox.returnPressed.connect(self.check_range_angles_textbox)
        self.grid_layout.addWidget(self.range_angles_textbox_label, 22, 1)
        self.grid_layout.addWidget(self.range_angles_textbox, 22, 2)

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
    def update_preview_frame(self, frame, frame_width, frame_height, scaled_width = None, grayscale = True):
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
        self.calculate_background_progress_window.save_background = True
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
        # if self.video_path is not None and self.video_path != '':
            # self.descriptors_dict['video_path_basename'] = self.video_path_basename
            # self.descriptors_dict['video_path_folder'] = self.video_path_folder
            # self.descriptors_dict['video_n_frames'] = self.video_n_frames
            # self.descriptors_dict['video_fps'] = self.video_fps
            # self.descriptors_dict['video_frame_width'] = self.video_frame_width
            # self.descriptors_dict['video_frame_height'] = self.video_frame_height
            # self.descriptors_dict['background_path_basename'] = self.background_path_basename
            # self.descriptors_dict['save_path'] = self.save_path
            #
            # self.tracking_parameters_dict['n_tail_points'] = self.n_tail_points
            # self.tracking_parameters_dict['dist_tail_points'] = self.dist_tail_points
            # self.tracking_parameters_dict['dist_eyes'] = self.dist_eyes
            # self.tracking_parameters_dict['dist_swim_bladder'] = self.dist_swim_bladder
            # self.tracking_parameters_dict['tracking_method'] = self.tracking_method
            # self.tracking_parameters_dict['save_video'] = self.save_video
            # self.tracking_parameters_dict['extended_eyes_calculation'] = self.extended_eyes_calculation
            # self.tracking_parameters_dict['n_frames'] = self.n_frames
            # self.tracking_parameters_dict['starting_frame'] = self.starting_frame
            # self.tracking_parameters_dict['median_blur'] = self.median_blur
            # self.tracking_parameters_dict['save_path'] = self.save_path
            # self.tracking_parameters_dict['background_path'] = self.background_path
            # self.tracking_parameters_dict['heading_line_length'] = self.heading_line_length
            # self.tracking_parameters_dict['video_fps'] = self.video_fps
            # self.tracking_parameters_dict['pixel_threshold'] = self.pixel_threshold
            # self.tracking_parameters_dict['frame_change_threshold'] = self.frame_change_threshold
            # self.tracking_parameters_dict['eyes_threshold'] = self.eyes_threshold
            # self.tracking_parameters_dict['initial_pixel_search'] = self.initial_pixel_search
            # self.tracking_parameters_dict['invert_threshold'] = self.invert_threshold
            # self.tracking_parameters_dict['range_angles'] = self.range_angles
            # self.tracking_parameters_dict['background_calculation_method'] = self.background_calculation_method
            # self.tracking_parameters_dict['background_calculation_frame_chunk_width'] = self.background_calculation_frame_chunk_width
            # self.tracking_parameters_dict['background_calculation_frame_chunk_height'] = self.background_calculation_frame_chunk_height
            # self.tracking_parameters_dict['background_calculation_frames_to_skip'] = self.background_calculation_frames_to_skip
            #
            # self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] = self.descriptors_dict.copy()
            # self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'] = self.tracking_parameters_dict.copy()
            # self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'] = self.colours.copy()
            # if self.background is not None:
            #     self.loaded_videos_and_parameters_dict[self.video_path]['background'] = self.background.copy()

        self.background = None
        self.background_path = None
        self.background_path_basename = None

        self.video_path, _ = QFileDialog.getOpenFileName(self,"Open Video File", "","Video Files (*.avi; *.mp4)", options=QFileDialog.Options())
        if self.video_path:
            self.update_preview_parameters(inactivate = True)
            self.trigger_load_default_tracking_parameters()
            self.update_colours()
            self.trigger_load_default_colours()
            self.update_colours()
            self.video_path.replace('/', '\\')
            self.get_video_attributes()
            self.update_descriptors()
            if len(self.loaded_videos_and_parameters_dict) == 0:
                self.loaded_videos_and_parameters_dict[self.video_path] = {  'descriptors' : None,
                                                                        'tracking_parameters' : None,
                                                                        'colour_parameters' : None,
                                                                        'background' : None}
                self.loaded_videos_listbox.addItem(self.video_path)
                self.loaded_videos_listbox.setCurrentRow(0)
            else:
                if self.video_path not in self.loaded_videos_and_parameters_dict.keys():
                    self.loaded_videos_and_parameters_dict[self.video_path] = {  'descriptors' : None,
                                                                            'tracking_parameters' : None,
                                                                            'colour_parameters' : None,
                                                                            'background' : None}
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
    def trigger_update_preview(self, magnify = False, demagnify = False):
        if self.preview_background:
            use_grayscale = True
            if magnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = self.preview_frame_window_label_size[0] + 100, grayscale = use_grayscale)
            if demagnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = self.preview_frame_window_label_size[0] - 100, grayscale = use_grayscale)
            if not magnify and not demagnify:
                self.update_preview_frame(self.background, self.background_width, self.background_height, scaled_width = self.preview_frame_window_label_size[0], grayscale = use_grayscale)
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
                    elif self.tracking_method == 'head_fixed':
                        self.frame = ut.apply_threshold_to_frame(self.frame, self.eyes_threshold, invert = self.invert_threshold)
                    if magnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] + 100, grayscale = use_grayscale)
                    if demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] - 100, grayscale = use_grayscale)
                    if not magnify and not demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0], grayscale = use_grayscale)
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
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] + 100, grayscale = use_grayscale)
                    if demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0] - 100, grayscale = use_grayscale)
                    if not magnify and not demagnify:
                        self.update_preview_frame(self.frame, self.video_frame_width, self.video_frame_height, scaled_width = self.preview_frame_window_label_size[0], grayscale = use_grayscale)
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
        # self.save_tracked_video_combobox.setCurrentIndex(1)
        self.extended_eyes_calculation = False
        # self.extended_eyes_calculation_combobox.setCurrentIndex(1)
        self.background_calculation_method = 'brightest'
        # self.background_calculation_method_combobox.setCurrentIndex(0)
        self.background_calculation_frame_chunk_width = 250
        self.background_calculation_frame_chunk_height = 250
        self.background_calculation_frames_to_skip = 10
        self.initial_pixel_search = 'brightest'
        # self.initial_pixel_search_combobox.setCurrentIndex(0)
        self.invert_threshold = False
        # self.invert_threshold_combobox.setCurrentIndex(1)
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
            'initial_pixel_search' : self.initial_pixel_search, 'invert_threshold' : self.invert_threshold}
        np.save('saved_parameters\\tracking_parameters.npy', tracking_parameters)
    def trigger_track_video(self):
        if self.track_selected_video_button.isEnabled():
            self.track_selected_video_button.setEnabled(False)
        if self.track_all_videos_button.isEnabled():
            self.track_all_videos_button.setEnabled(False)

        self.track_video_progress_window = TrackVideoProgressWindow()
        self.track_video_progress_window.video_path = self.video_path
        self.track_video_progress_window.median_blur = self.median_blur
        self.track_video_progress_window.n_tail_points = self.n_tail_points
        self.track_video_progress_window.dist_tail_points = self.dist_tail_points
        self.track_video_progress_window.dist_eyes = self.dist_eyes
        self.track_video_progress_window.dist_swim_bladder = self.dist_swim_bladder
        self.track_video_progress_window.save_background = self.save_background
        self.track_video_progress_window.tracking_method = self.tracking_method
        self.track_video_progress_window.n_frames = self.n_frames
        self.track_video_progress_window.starting_frame = self.starting_frame
        self.track_video_progress_window.save_path = self.save_path
        self.track_video_progress_window.background_path = self.background_path
        self.track_video_progress_window.background = self.background
        self.track_video_progress_window.heading_line_length = self.heading_line_length
        self.track_video_progress_window.video_fps = self.video_fps
        self.track_video_progress_window.pixel_threshold = self.pixel_threshold
        self.track_video_progress_window.frame_change_threshold = self.frame_change_threshold
        self.track_video_progress_window.colours = self.colours
        self.track_video_progress_window.save_video = self.save_video
        self.track_video_progress_window.extended_eyes_calculation = self.extended_eyes_calculation
        self.track_video_progress_window.eyes_threshold = self.eyes_threshold
        self.track_video_progress_window.eyes_line_length = self.eyes_line_length
        self.track_video_progress_window.initial_pixel_search = self.initial_pixel_search
        self.track_video_progress_window.range_angles = self.range_angles
        self.track_video_progress_window.background_calculation_method = self.background_calculation_method
        self.track_video_progress_window.background_calculation_frame_chunk_width = self.background_calculation_frame_chunk_width
        self.track_video_progress_window.background_calculation_frame_chunk_height = self.background_calculation_frame_chunk_height
        self.track_video_progress_window.background_calculation_frames_to_skip = self.background_calculation_frames_to_skip
        self.track_video_progress_window.video_n_frames = self.video_n_frames
        self.track_video_progress_window.update_processing_video_label()
        self.track_video_progress_window.update_progress_bar_range()
        self.track_video_progress_window.update_total_tracking_progress_bar_range()
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

        if self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] is None:
            print('here')
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

            self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'] = self.descriptors_dict.copy()
            self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'] = self.tracking_parameters_dict.copy()
            self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'] = self.colours.copy()
            if self.background is not None:
                self.loaded_videos_and_parameters_dict[self.video_path]['background'] = self.background.copy()
    def trigger_reload_parameters(self):
        if self.video_path is not None and self.video_path != '':

            self.descriptors_dict = self.loaded_videos_and_parameters_dict[self.video_path]['descriptors'].copy()
            self.tracking_parameters_dict = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters'].copy()
            self.colours = self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters'].copy()
            self.update_colours()
            self.background = self.loaded_videos_and_parameters_dict[self.video_path]['background'].copy()

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
            self.tracking_method = 'head_fixed'
        if self.preview_tracking_results:
            self.trigger_update_preview()
    def check_preview_tracking_results_checkbox(self):
        self.preview_tracking_results = self.preview_tracking_results_checkbox.isChecked()
        self.trigger_update_preview()
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
    def event_preview_frame_window_wheel_scrolled(self, event):
        event.ignore()

class TrackVideoProgressWindow(QMainWindow):

    track_video_progress_finished = pyqtSignal(bool)

    # Defining Initialization Functions
    def __init__(self):
        super(TrackVideoProgressWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.initialize_class_variables()
        self.add_processing_video_label()
        self.add_current_status_label()
        self.add_current_tracking_progress_bar()
        self.add_total_progress_label()
        self.add_total_tracking_progress_bar()
        self.add_total_time_elapsed_label()
        self.add_cancel_tracking_button()
        self.setWindowTitle('Video Tracking in Progress')
        self.setFixedSize(500, 270)

    def initialize_class_variables(self):
        self.video_path = None
        self.background = None
        self.colours = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.save_background = None
        self.tracking_method = None
        self.initial_pixel_search = None
        self.n_tail_points = None
        self.dist_tail_points = None
        self.dist_eyes = None
        self.dist_swim_bladder = None
        self.range_angles = None
        self.median_blur = None
        self.pixel_threshold = None
        self.frame_change_threshold = None
        self.heading_line_length = None
        self.extended_eyes_calculation = None
        self.eyes_threshold = None
        self.eyes_line_length = None
        self.invert_threshold = None
        self.save_video = None
        self.starting_frame = None
        self.n_frames = None
        self.save_path = None
        self.video_fps = None
        self.track_video_thread = None

        self.video_n_frames = None

    def add_processing_video_label(self):
        self.processing_video_label = QLabel(self)
        self.processing_video_label.move(40, 10)
        self.processing_video_label.resize(400, 20)

    def add_current_status_label(self):
        self.current_status_label = QLabel(self)
        self.current_status_label.move(40, 40)
        self.current_status_label.resize(400, 20)

    def add_current_tracking_progress_bar(self):
        self.current_tracking_progress_bar = QProgressBar(self)
        self.current_tracking_progress_bar.move(50, 70)
        self.current_tracking_progress_bar.resize(400, 30)
        self.current_tracking_progress_bar.setMinimum(0)

    def add_total_progress_label(self):
        self.total_progress_label = QLabel(self)
        self.total_progress_label.move(40, 110)
        self.total_progress_label.resize(400, 20)
        self.total_progress_label.setText('Total Progress: ')

    def add_total_tracking_progress_bar(self):
        self.total_tracking_progress_bar = QProgressBar(self)
        self.total_tracking_progress_bar.move(50, 140)
        self.total_tracking_progress_bar.resize(400, 30)

    def add_total_time_elapsed_label(self):
        self.total_time_elapsed_label = QLabel(self)
        self.total_time_elapsed_label.move(40, 180)
        self.total_time_elapsed_label.resize(400, 20)

    def add_cancel_tracking_button(self):
        self.cancel_tracking_button = QPushButton('Cancel', self)
        self.cancel_tracking_button.move(150, 210)
        self.cancel_tracking_button.resize(200, 50)
        self.cancel_tracking_button.clicked.connect(self.close)

    def update_processing_video_label(self):
        self.processing_video_label.setText('Processing Video: {0}'.format(self.video_path))

    def update_progress_bar_range(self):
        if self.n_frames == 'All':
            self.current_tracking_progress_bar.setMaximum(self.video_n_frames)
        else:
            # if self.n_frames + self.starting_frame < self.video_n_frames:
            self.current_tracking_progress_bar.setMaximum(self.n_frames)

    def update_progress_bar_value(self, value, current_status):
        self.current_tracking_progress_bar.setValue(value)

    def update_current_status_label(self, value):
        self.current_status_label.setText('Current Status: {0}'.format(value))

    def update_total_time_elapsed_label(self, value):
        elapsed_time = int(round(value, 0))
        hours, minutes, seconds = ut.convert_total_seconds_to_hours_minutes_seconds(elapsed_time)
        elapsed_time_message = 'Total Time Elapsed: '
        if hours != 0:
            if hours == 1:
                elapsed_time_message += '{0} hour '.format(hours)
            else:
                elapsed_time_message += '{0} hours '.format(hours)
        if minutes != 0:
            if minutes == 1:
                elapsed_time_message += '{0} minute '.format(minutes)
            else:
                elapsed_time_message += '{0} minutes '.format(minutes)
        if seconds != 0:
            if seconds == 1:
                elapsed_time_message += '{0} second '.format(seconds)
            else:
                elapsed_time_message += '{0} seconds '.format(seconds)
        if hours != 0 or minutes != 0 or seconds != 0:
            elapsed_time_message = elapsed_time_message[:-1] + '.'
        self.total_time_elapsed_label.setText(elapsed_time_message)

    def update_total_tracking_progress_bar_range(self):
        if self.background is None and self.background_calculation_method == 'mode':
            self.total_tracking_progress_bar.setMaximum(self.video_n_frames * 5)
        elif self.background is None:
            self.total_tracking_progress_bar.setMaximum(self.video_n_frames * 10)
        else:
            self.total_tracking_progress_bar.setMaximum(self.video_n_frames)

    def update_total_tracking_progress_bar_value(self, value, current_status):
        if current_status == 'Calculating Background':
            self.total_tracking_progress_bar.setValue(value)
        elif self.background is None and self.background_calculation_method == 'mode':
            self.total_tracking_progress_bar.setValue(self.video_n_frames + (value * 4))
        elif self.background is None:
            self.total_tracking_progress_bar.setValue(self.video_n_frames + (value * 9))
        else:
            self.total_tracking_progress_bar.setValue(value)

    def trigger_track_video(self):
        self.track_video_thread = TrackVideoThread()
        self.track_video_thread.video_path = self.video_path
        self.track_video_thread.background = self.background
        self.track_video_thread.colours = self.colours
        self.track_video_thread.background_calculation_method = self.background_calculation_method
        self.track_video_thread.background_calculation_frame_chunk_width = self.background_calculation_frame_chunk_width
        self.track_video_thread.background_calculation_frame_chunk_height = self.background_calculation_frame_chunk_height
        self.track_video_thread.background_calculation_frames_to_skip = self.background_calculation_frames_to_skip
        self.track_video_thread.save_background = self.save_background
        self.track_video_thread.tracking_method = self.tracking_method
        self.track_video_thread.initial_pixel_search = self.initial_pixel_search
        self.track_video_thread.n_tail_points = self.n_tail_points
        self.track_video_thread.dist_tail_points = self.dist_tail_points
        self.track_video_thread.dist_eyes = self.dist_eyes
        self.track_video_thread.dist_swim_bladder = self.dist_swim_bladder
        self.track_video_thread.range_angles = self.range_angles
        self.track_video_thread.median_blur = self.median_blur
        self.track_video_thread.pixel_threshold = self.pixel_threshold
        self.track_video_thread.frame_change_threshold = self.frame_change_threshold
        self.track_video_thread.heading_line_length = self.heading_line_length
        self.track_video_thread.extended_eyes_calculation = self.extended_eyes_calculation
        self.track_video_thread.eyes_threshold = self.eyes_threshold
        self.track_video_thread.eyes_line_length = self.eyes_line_length
        self.track_video_thread.invert_threshold = self.invert_threshold
        self.track_video_thread.save_video = self.save_video
        self.track_video_thread.starting_frame = self.starting_frame
        self.track_video_thread.n_frames = self.n_frames
        self.track_video_thread.save_path = self.save_path
        self.track_video_thread.video_fps = self.video_fps
        self.track_video_thread.start()
        self.track_video_thread.progress_signal.connect(self.update_progress_bar_value)
        self.track_video_thread.progress_signal.connect(self.update_total_tracking_progress_bar_value)
        self.track_video_thread.current_status_signal.connect(self.update_current_status_label)
        self.track_video_thread.total_time_elapsed_signal.connect(self.update_total_time_elapsed_label)
        self.track_video_thread.background_calculation_finished_signal.connect(self.trigger_reset_progress_bar)
        self.track_video_thread.tracking_finished_signal.connect(self.close)

    def trigger_reset_progress_bar(self):
        self.current_tracking_progress_bar.reset()

    def closeEvent(self, event):
        self.track_video_progress_finished.emit(True)
        if self.track_video_thread is not None:
            if self.track_video_thread.isRunning():
                self.track_video_thread.timer_thread.terminate()
                self.track_video_thread.terminate()
        event.accept()

class TrackVideoThread(QThread):

    background_calculation_finished_signal = pyqtSignal(bool)
    tracking_finished_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(float, str)
    current_status_signal = pyqtSignal(str)
    total_time_elapsed_signal = pyqtSignal(float)

    def __init__(self):
        super(TrackVideoThread, self).__init__()
        self.initialize_class_variables()

    def initialize_class_variables(self):
        self.video_path = None
        self.background = None
        self.colours = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.save_background = None
        self.tracking_method = None
        self.initial_pixel_search = None
        self.n_tail_points = None
        self.dist_tail_points = None
        self.dist_eyes = None
        self.dist_swim_bladder = None
        self.range_angles = None
        self.median_blur = None
        self.pixel_threshold = None
        self.frame_change_threshold = None
        self.heading_line_length = None
        self.extended_eyes_calculation = None
        self.eyes_threshold = None
        self.invert_threshold = None
        self.save_video = None
        self.starting_frame = None
        self.n_frames = None
        self.save_path = None
        self.video_fps = None

        self.periods = None
        self.start_time = None
        self.total_time_elapsed = None
        self.current_status = None

        self.timer_thread = None

    def update_current_status(self, value):
        if self.current_status is not None:
            if self.periods is None:
                self.periods = '.'
            elif len(self.periods) == 6:
                self.periods = '.'
            else:
                self.periods += '.'
            self.current_status_signal.emit(self.current_status + self.periods)
        if self.start_time is None:
            self.start_time = value
            self.total_time_elapsed = self.start_time
        else:
            self.total_time_elapsed = value - self.start_time
        self.total_time_elapsed_signal.emit(self.total_time_elapsed)

    def run(self):
        self.timer_thread = TimerThread()
        self.timer_thread.start()
        self.timer_thread.time_signal.connect(self.update_current_status)
        if self.background is None:
            self.background = self.calculate_background(self.video_path, self.background_calculation_method, [self.background_calculation_frame_chunk_width, self.background_calculation_frame_chunk_height],
                            self.background_calculation_frames_to_skip, self.save_path, self.save_background)

        self.track_video(self.video_path, self.background, self.colours, self.tracking_method, self.initial_pixel_search, self.n_tail_points, self.dist_tail_points, self.dist_eyes,
                        self.dist_swim_bladder, self.range_angles, self.median_blur, self.pixel_threshold, self.frame_change_threshold, self.heading_line_length, self.extended_eyes_calculation, self.eyes_threshold,
                        self.eyes_line_length, self.invert_threshold, self.save_video, self.starting_frame, self.n_frames, self.save_path, self.video_fps)

    def calculate_background(self, video_path, method, chunk_size, frames_to_skip, save_path, save_background):
        # Check arguments.
        if not isinstance(video_path, str):
            print('Error: video_path must be formatted as a string.')
            return
        if not isinstance(method, str) or method not in ['brightest', 'darkest', 'mode']:
            print('Error: method must be formatted as a string and must be one of the following: brightest, darkest, or mode.')
            return
        if not isinstance(save_background, bool):
            print('Error: save_background must be formatted as a boolean (True/False).')
            return
        if not isinstance(chunk_size, list):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if len(chunk_size) != 2:
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(chunk_size[0], int) or not isinstance(chunk_size[1], int):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(frames_to_skip, int):
            print('Error: frames_to_skip must be formatted as an integer.')
            return

        self.current_status = 'Calculating Background'

        frame_size = ut.get_frame_size_from_video(video_path)
        video_n_frames = ut.get_total_frame_number_from_video(video_path)

        try:
            # Load the video.
            capture = cv2.VideoCapture(video_path)
            # Retrieve total number of frames in video.
            frames_to_skip += 1

            if method == 'mode':
                background = np.zeros(frame_size)
                pix = []
                width_iterations = int(frame_size[0]/chunk_size[0])
                if frame_size[0] % chunk_size[0] != 0:
                    width_iterations += 1
                height_iterations = int(frame_size[1] / chunk_size[1])
                if frame_size[1] % chunk_size[1] != 0:
                    height_iterations += 1
                for i in range(height_iterations):
                    for j in range(width_iterations):
                        for frame_num in range(video_n_frames):
                            self.progress_signal.emit((frame_num + 1 + (j * video_n_frames) + (video_n_frames * width_iterations * i)) / (width_iterations * height_iterations * video_n_frames) * video_n_frames, self.current_status)
                            success, frame = capture.read()
                            if success:
                                if frame_num % frames_to_skip == 0:
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    if i == height_iterations - 1 and j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : ])
                                    elif i == height_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                                    elif j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ])
                                    else:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                        bg_pix = stats.mode(pix)[0]
                        if i == height_iterations - 1 and j == width_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : ] = bg_pix
                        elif i == height_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        elif j == width_iterations - 1:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ] = bg_pix
                        else:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        pix = []
                        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                background = background.astype(np.uint8)
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
            else:
                # Iterate through each frame in the video.
                for frame_num in range(video_n_frames):
                    self.progress_signal.emit(frame_num + 1, self.current_status)
                    # Load frame into memory.
                    success, frame = capture.read()
                    # Check if frame was loaded successfully.
                    if success:
                        if frame_num % frames_to_skip == 0:
                            # Convert frame to grayscale.
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # Copy frame into background if this is the first frame.
                            if frame_num == 0:
                                background = frame.copy().astype(np.float32)
                            elif method == 'brightest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.less(background, frame)
                                # Update the background image where all of the pixels in the new frame are brighter than the background image.
                                background[mask] = frame[mask]
                            elif method == 'darkest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.greater(background, frame)
                                # Update the background image where all of the pixels in the new frame are darker than the background image.
                                background[mask] = frame[mask]
                background = background.astype(np.uint8)
                # Save the background into an external file if requested.
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
        except:
            # Errors that may occur during the background calculation are handled.
            print('Error calculating background')
            if capture.isOpened():
                capture.release()
            return None
        if capture.isOpened():
            # Unload video from memory.
            capture.release()
        # Return the calculated background.
        time.sleep(0.5)
        return background

    def track_video(self, video_path, background, colours, tracking_method, initial_pixel_search, n_tail_points, dist_tail_points, dist_eyes,
                    dist_swim_bladder, range_angles, median_blur, pixel_threshold, frame_change_threshold, heading_line_length, extended_eyes_calculation, eyes_threshold,
                    eyes_line_length, invert_threshold, save_video, starting_frame, n_frames, save_path, video_fps):

        self.current_status = 'Tracking Video'
        colours = [[colours[i][2], colours[i][1], colours[i][0]] for i in range(len(colours))]

        if heading_line_length == 0:
            heading_line_length = dist_eyes

        if extended_eyes_calculation and eyes_line_length == 0:
            eyes_line_length = heading_line_length

        if save_path == None:
            save_path = os.path.dirname(video_path)

        video_n_frames = ut.get_total_frame_number_from_video(video_path)
        frame_size = ut.get_frame_size_from_video(video_path)

        # Get the fps.
        if video_fps is None:
            video_fps = get_fps_from_video(video_path)

        # Get the total number of frames.
        if n_frames == 'All':
            n_frames = video_n_frames

        if n_frames > video_n_frames:
            print('The number of frames requested to track exceeds the total number of frames in the video.')
            n_frames = video_n_frames

        if starting_frame >= video_n_frames:
            print('Starting frame number provided exceeds the total number of frames in the video. Setting the starting frame number to 0.')
            starting_frame = 0
            n_frames = video_n_frames

        if starting_frame + n_frames > video_n_frames:
            print('The number of frames requested to track plus the number of initial frames to offset exceeds the total number of frames in the video. Keeping the initial frames to offset and tracking the remaining frames.')
            n_frames = video_n_frames - starting_frame

        # Open the video path.
        capture = cv2.VideoCapture(video_path)

        # Set the frame position to start.
        capture.set(cv2.CAP_PROP_POS_FRAMES, starting_frame)

        if save_video:
            # Create a path for the video once it is tracked.
            save_video_path = "{0}\\{1}_tracked.avi".format(save_path, os.path.basename(video_path)[:-4])

            # Create video writer.
            writer = cv2.VideoWriter(save_video_path, 0, video_fps, frame_size)

        # Initialize variables for data.
        eye_coord_array = []
        eye_angle_array = []
        tail_coord_array = []
        body_coord_array = []
        heading_angle_array = []
        prev_frame = None
        prev_eye_angle = None

        range_angles = np.radians(range_angles)

        if tracking_method == 'free_swimming':
            # Iterate through each frame.
            for n in range(n_frames):
                self.progress_signal.emit(n + 1, self.current_status)
                # Load a frame into memory.
                success, original_frame = capture.read()
                # Checks if the frame was loaded successfully.
                if success:
                    # Initialize variables for each frame.
                    first_eye_coords = [np.nan, np.nan]
                    second_eye_coords = [np.nan, np.nan]
                    first_eye_angle = np.nan
                    second_eye_angle = np.nan
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    swim_bladder_coords = [np.nan, np.nan]
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                    tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    # Convert the frame into the absolute difference between the frame and the background.
                    frame = cv2.absdiff(frame, background)
                    # Apply a median blur filter to the frame.
                    frame = cv2.medianBlur(frame, median_blur)
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.max(frame) > pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                swim_bladder_coords = tail_coord_array[len(tail_coord_array) - 1][0]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1][1:]
                            else:
                                # Return the coordinate of the brightest pixel.
                                first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                second_eye_coords = ut.calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Calculate the angle between the two eyes.
                                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Check if this is the first frame.
                                    if prev_eye_angle is not None:
                                        # Check if the difference between the current eye angle and previous eye angle is somwehere around pi, meaning the first and second eye coordiantes have reversed. Occasionally, the coordinates of the eyes will switch between one and the other. This method is useful for keeping the positions of the left and right eye the same between frames.
                                        if eye_angle - prev_eye_angle > np.pi / 2 or eye_angle - prev_eye_angle < -np.pi / 2:
                                            if eye_angle - prev_eye_angle < np.pi * 3 / 2 and eye_angle - prev_eye_angle > -np.pi * 3 / 2:
                                                # Switch the first and second eye coordinates.
                                                coords = first_eye_coords
                                                first_eye_coords = second_eye_coords
                                                second_eye_coords = coords
                                                # Calculate the new eye angle.
                                                eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Apply a threshold to the frame.
                                    thresh = ut.apply_threshold_to_frame(frame, eyes_threshold, invert = invert_threshold)
                                    # Find the contours of the binary regions in the thresholded frame.
                                    contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]
                                    # Iterate through each contour in the list of contours.
                                    for i in range(len(contours)):
                                        # Check if the first eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (first_eye_coords[1], first_eye_coords[0]), False) == 1:
                                            # Set the first eye coordinates to the centroid of the binary region and calculate the first eye angle.
                                            M = cv2.moments(contours[i])
                                            first_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            first_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                        # Check if the second eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (second_eye_coords[1], second_eye_coords[0]), False) == 1:
                                            # Set the second eye coordinates to the centroid of the binary region and calculate the second eye angle.
                                            M = cv2.moments(contours[i])
                                            second_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            second_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                # Find the midpoint of the line that connects both eyes.
                                heading_coords = [(first_eye_coords[0] + second_eye_coords[0]) / 2, (first_eye_coords[1] + second_eye_coords[1]) / 2]
                                # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                swim_bladder_coords = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                body_coords = [int(round((swim_bladder_coords[0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((swim_bladder_coords[1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                    body_contour = np.array([np.array([swim_bladder_coords[1], swim_bladder_coords[0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([second_eye_coords[1], second_eye_coords[0]])])
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (first_eye_coords[1] + (dist_eyes / 2 * np.cos(first_eye_angle)), first_eye_coords[0] + (dist_eyes / 2 * np.sin(first_eye_angle))), False) == 1:
                                        # Flip the first eye angle.
                                        if first_eye_angle > 0:
                                            first_eye_angle -= np.pi
                                        else:
                                            first_eye_angle += np.pi
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (second_eye_coords[1] + (dist_eyes / 2 * np.cos(second_eye_angle)), second_eye_coords[0] + (dist_eyes / 2 * np.sin(second_eye_angle))), False) == 1:
                                        # Flip the second eye angle.
                                        if second_eye_angle > 0:
                                            second_eye_angle -= np.pi
                                        else:
                                            second_eye_angle += np.pi
                                # Calculate the initial tail angle as the angle opposite to the heading angle.
                                if heading_angle > 0:
                                    tail_angle = heading_angle - np.pi
                                else:
                                    tail_angle = heading_angle + np.pi
                                # Iterate through the number of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point.
                                    if m == 0:
                                        # Calculate the first tail point using the swim bladder as the first set of coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                    else:
                                        # Check if this is the second tail point.
                                        if m == 1:
                                            # Calculate the next tail angle as the angle between the first tail point and the swim bladder.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - swim_bladder_coords[0], tail_point_coords[m - 1][1] - swim_bladder_coords[1])
                                        # Check if the number of tail points calculated is greater than 2.
                                        else:
                                            # Calculate the next tail angle as the angle between the last two tail points.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                        # Calculate the next set of tail coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                # Set the previous frame to the current frame.
                                prev_frame = frame
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Set the previous eye angle to the current eye angle.
                                    prev_eye_angle = eye_angle

                            if save_video:
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a line representing the first eye angle.
                                    original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (eyes_line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (eyes_line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                                    # Draw a circle around the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                    # Draw a line representing the second eye angle.
                                    original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (eyes_line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (eyes_line_length * np.sin(second_eye_angle))))), colours[-2], 1)
                                else:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a circle arround the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                # Iterate through each set of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point
                                    if m == 0:
                                        # For the first tail point, draw around the midpoint of the line that connects the swim bladder to the first tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((swim_bladder_coords[1] + tail_point_coords[m][1]) / 2)), int(round((swim_bladder_coords[0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                    else:
                                        # For all subsequent tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        swim_bladder_coords = [np.nan, np.nan]
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                        tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Iterate through the number of tail points, including the swim bladder coordinates.
                    for m in range(n_tail_points + 1):
                        # Check if this is the first tail point.
                        if m == 0:
                            # Add the swim bladder to a list that will contain all of the tail points, including the swim bladder.
                            tail_points[m] = swim_bladder_coords
                        else:
                            # Add all of the tail points to the list.
                            tail_points[m] = tail_point_coords[m - 1]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    tail_coord_array.append(tail_points)
                    body_coord_array.append(body_coords)
                    heading_angle_array.append(heading_angle)
                    if save_video:
                        # Write the new frame that contains the annotated frame with tracked points to a new video.
                        writer.write(original_frame)
        elif tracking_method == 'head_fixed':
            # Iterate through each frame.
            for n in range(n_frames):
                self.progress_signal.emit(n + 1, self.current_status)
                # Load a frame into memory.
                success, original_frame = capture.read()
                # Checks if the frame was loaded successfully.
                if success:
                    # Initialize variables for each frame.
                    first_eye_coords = [np.nan, np.nan]
                    second_eye_coords = [np.nan, np.nan]
                    first_eye_angle = np.nan
                    second_eye_angle = np.nan
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    swim_bladder_coords = [np.nan, np.nan]
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                    tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.min(frame) < pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                swim_bladder_coords = tail_coord_array[len(tail_coord_array) - 1][0]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1][1:]
                            else:
                                if initial_pixel_search == 'darkest':
                                    # Return the coordinate of the brightest pixel.
                                    first_eye_coords = [np.where(frame == np.min(frame))[0][0], np.where(frame == np.min(frame))[1][0]]
                                elif initial_pixel_search == 'brightest':
                                    first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                second_eye_coords = ut.calculate_next_coords(first_eye_coords, dist_eyes, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Calculate the angle between the two eyes.
                                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Check if this is the first frame.
                                    if prev_eye_angle is not None:
                                        # Check if the difference between the current eye angle and previous eye angle is somwehere around pi, meaning the first and second eye coordiantes have reversed. Occasionally, the coordinates of the eyes will switch between one and the other. This method is useful for keeping the positions of the left and right eye the same between frames.
                                        if eye_angle - prev_eye_angle > np.pi / 2 or eye_angle - prev_eye_angle < -np.pi / 2:
                                            if eye_angle - prev_eye_angle < np.pi * 3 / 2 and eye_angle - prev_eye_angle > -np.pi * 3 / 2:
                                                # Switch the first and second eye coordinates.
                                                coords = first_eye_coords
                                                first_eye_coords = second_eye_coords
                                                second_eye_coords = coords
                                                # Calculate the new eye angle.
                                                eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Apply a threshold to the frame.
                                    thresh = ut.apply_threshold_to_frame(frame, eyes_threshold, invert = invert_threshold)
                                    # Find the contours of the binary regions in the thresholded frame.
                                    contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]
                                    # Iterate through each contour in the list of contours.
                                    for i in range(len(contours)):
                                        # Check if the first eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (first_eye_coords[1], first_eye_coords[0]), False) == 1:
                                            # Set the first eye coordinates to the centroid of the binary region and calculate the first eye angle.
                                            M = cv2.moments(contours[i])
                                            first_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            first_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                        # Check if the second eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (second_eye_coords[1], second_eye_coords[0]), False) == 1:
                                            # Set the second eye coordinates to the centroid of the binary region and calculate the second eye angle.
                                            M = cv2.moments(contours[i])
                                            second_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            second_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                # Find the midpoint of the line that connects both eyes.
                                heading_coords = [(first_eye_coords[0] + second_eye_coords[0]) / 2, (first_eye_coords[1] + second_eye_coords[1]) / 2]
                                # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                swim_bladder_coords = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Convert the frame into the absolute difference between the frame and the background.
                                frame = cv2.absdiff(frame, background)
                                # Apply a median blur filter to the frame.
                                frame = cv2.medianBlur(frame, median_blur)
                                # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                body_coords = [int(round((swim_bladder_coords[0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((swim_bladder_coords[1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                    body_contour = np.array([np.array([swim_bladder_coords[1], swim_bladder_coords[0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([second_eye_coords[1], second_eye_coords[0]])])
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (first_eye_coords[1] + (dist_eyes / 2 * np.cos(first_eye_angle)), first_eye_coords[0] + (dist_eyes / 2 * np.sin(first_eye_angle))), False) == 1:
                                        # Flip the first eye angle.
                                        if first_eye_angle > 0:
                                            first_eye_angle -= np.pi
                                        else:
                                            first_eye_angle += np.pi
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (second_eye_coords[1] + (dist_eyes / 2 * np.cos(second_eye_angle)), second_eye_coords[0] + (dist_eyes / 2 * np.sin(second_eye_angle))), False) == 1:
                                        # Flip the second eye angle.
                                        if second_eye_angle > 0:
                                            second_eye_angle -= np.pi
                                        else:
                                            second_eye_angle += np.pi
                                # Calculate the initial tail angle as the angle opposite to the heading angle.
                                if heading_angle > 0:
                                    tail_angle = heading_angle - np.pi
                                else:
                                    tail_angle = heading_angle + np.pi
                                # Iterate through the number of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point.
                                    if m == 0:
                                        # Calculate the first tail point using the swim bladder as the first set of coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                    else:
                                        # Check if this is the second tail point.
                                        if m == 1:
                                            # Calculate the next tail angle as the angle between the first tail point and the swim bladder.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - swim_bladder_coords[0], tail_point_coords[m - 1][1] - swim_bladder_coords[1])
                                        # Check if the number of tail points calculated is greater than 2.
                                        else:
                                            # Calculate the next tail angle as the angle between the last two tail points.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                        # Calculate the next set of tail coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                # Set the previous frame to the current frame.
                                prev_frame = frame
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Set the previous eye angle to the current eye angle.
                                    prev_eye_angle = eye_angle

                            if save_video:
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a line representing the first eye angle.
                                    original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (eyes_line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (eyes_line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                                    # Draw a circle around the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                    # Draw a line representing the second eye angle.
                                    original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (eyes_line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (eyes_line_length * np.sin(second_eye_angle))))), colours[-2], 1)
                                else:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a circle arround the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                # Iterate through each set of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point
                                    if m == 0:
                                        # For the first tail point, draw around the midpoint of the line that connects the swim bladder to the first tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((swim_bladder_coords[1] + tail_point_coords[m][1]) / 2)), int(round((swim_bladder_coords[0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                    else:
                                        # For all subsequent tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        swim_bladder_coords = [np.nan, np.nan]
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                        tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Iterate through the number of tail points, including the swim bladder coordinates.
                    for m in range(n_tail_points + 1):
                        # Check if this is the first tail point.
                        if m == 0:
                            # Add the swim bladder to a list that will contain all of the tail points, including the swim bladder.
                            tail_points[m] = swim_bladder_coords
                        else:
                            # Add all of the tail points to the list.
                            tail_points[m] = tail_point_coords[m - 1]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    tail_coord_array.append(tail_points)
                    body_coord_array.append(body_coords)
                    heading_angle_array.append(heading_angle)
                    if save_video:
                        # Write the new frame that contains the annotated frame with tracked points to a new video.
                        writer.write(original_frame)

        # Unload the video and writer from memory.
        capture.release()
        if save_video:
            writer.release()

        # Create a dictionary that contains all of the results.
        results =   {   'eye_coord_array' : eye_coord_array,
                        'eye_angle_array' : eye_angle_array,
                        'tail_coord_array' : tail_coord_array,
                        'body_coord_array' : body_coord_array,
                        'heading_angle_array' : heading_angle_array,
                        'video_path' : video_path,
                        'video_n_frames' : video_n_frames,
                        'video_fps' : video_fps,
                        'dist_tail_points' : dist_tail_points,
                        'dist_eyes' : dist_eyes,
                        'dist_swim_bladder' : dist_swim_bladder,
                        'eyes_threshold' : eyes_threshold,
                        'pixel_threshold' : pixel_threshold,
                        'frame_change_threshold' : frame_change_threshold,
                        'colours' : colours
                    }

        # Create a path that will contain all of the results from tracking.
        data_path = "{0}\\{1}_results.npy".format(save_path, os.path.basename(video_path)[:-4])

        # Save the results to a npz file.
        np.save(data_path, results)

        time.sleep(0.5)

        self.tracking_finished_signal.emit(True)

class TrackAllVideosProgressWindow(QMainWindow):

    track_all_videos_progress_finished = pyqtSignal(bool)

    # Defining Initialization Functions
    def __init__(self):
        super(TrackAllVideosProgressWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.initialize_class_variables()
        self.add_processing_video_label()
        self.add_processing_video_number_label()
        self.add_current_status_label()
        self.add_current_tracking_progress_bar()
        self.add_total_progress_label()
        self.add_total_tracking_progress_bar()
        self.add_total_time_elapsed_label()
        self.add_cancel_tracking_button()
        self.setWindowTitle('Multiple Video Tracking in Progress')
        self.setFixedSize(480, 300)

    def initialize_class_variables(self):
        self.loaded_videos_and_parameters_dict = None

        self.video_path = None
        self.background = None
        self.colours = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.save_background = None
        self.tracking_method = None
        self.initial_pixel_search = None
        self.n_tail_points = None
        self.dist_tail_points = None
        self.dist_eyes = None
        self.dist_swim_bladder = None
        self.range_angles = None
        self.median_blur = None
        self.pixel_threshold = None
        self.frame_change_threshold = None
        self.heading_line_length = None
        self.extended_eyes_calculation = None
        self.eyes_threshold = None
        self.invert_threshold = None
        self.save_video = None
        self.starting_frame = None
        self.n_frames = None
        self.save_path = None
        self.video_fps = None
        self.track_all_videos_thread = None

        self.video_n_frames = None

        self.i = None
        self.total_progress = None

    def add_processing_video_label(self):
        self.processing_video_label = QLabel(self)
        self.processing_video_label.move(40, 10)
        self.processing_video_label.resize(400, 20)

    def add_processing_video_number_label(self):
        self.processing_video_number_label = QLabel(self)
        self.processing_video_number_label.move(40, 40)
        self.processing_video_number_label.resize(400, 20)

    def add_current_status_label(self):
        self.current_status_label = QLabel(self)
        self.current_status_label.move(40, 70)
        self.current_status_label.resize(400, 20)

    def add_current_tracking_progress_bar(self):
        self.current_tracking_progress_bar = QProgressBar(self)
        self.current_tracking_progress_bar.move(50, 100)
        self.current_tracking_progress_bar.resize(400, 30)
        self.current_tracking_progress_bar.setMinimum(0)

    def add_total_progress_label(self):
        self.total_progress_label = QLabel(self)
        self.total_progress_label.move(40, 140)
        self.total_progress_label.resize(400, 20)
        self.total_progress_label.setText('Total Progress: ')

    def add_total_tracking_progress_bar(self):
        self.total_tracking_progress_bar = QProgressBar(self)
        self.total_tracking_progress_bar.move(50, 170)
        self.total_tracking_progress_bar.resize(400, 30)

    def add_total_time_elapsed_label(self):
        self.total_time_elapsed_label = QLabel(self)
        self.total_time_elapsed_label.move(40, 210)
        self.total_time_elapsed_label.resize(400, 20)

    def add_cancel_tracking_button(self):
        self.cancel_tracking_button = QPushButton('Cancel', self)
        self.cancel_tracking_button.move(150, 240)
        self.cancel_tracking_button.resize(200, 50)
        self.cancel_tracking_button.clicked.connect(self.close)

    def update_processing_video_label(self, value):
        self.processing_video_label.setText('Processing Video: {0}'.format(value))

    def update_processing_video_number_label(self, value):
        self.processing_video_number_label.setText('Processing Video Number: {0} / {1}'.format(value + 1, len(self.loaded_videos_and_parameters_dict.keys())))

    def update_current_progress_range(self, value):
        self.current_tracking_progress_bar.setMaximum(value)

    def update_current_progress_value(self, value):
        self.current_tracking_progress_bar.setValue(value)

    def update_current_status_label(self, value):
        self.current_status_label.setText('Current Status: {0}'.format(value))

    def update_total_time_elapsed_label(self, value):
        elapsed_time = int(round(value, 0))
        hours, minutes, seconds = ut.convert_total_seconds_to_hours_minutes_seconds(elapsed_time)
        elapsed_time_message = 'Total Time Elapsed: '
        if hours != 0:
            if hours == 1:
                elapsed_time_message += '{0} hour '.format(hours)
            else:
                elapsed_time_message += '{0} hours '.format(hours)
        if minutes != 0:
            if minutes == 1:
                elapsed_time_message += '{0} minute '.format(minutes)
            else:
                elapsed_time_message += '{0} minutes '.format(minutes)
        if seconds != 0:
            if seconds == 1:
                elapsed_time_message += '{0} second '.format(seconds)
            else:
                elapsed_time_message += '{0} seconds '.format(seconds)
        if hours != 0 or minutes != 0 or seconds != 0:
            elapsed_time_message = elapsed_time_message[:-1] + '.'
        self.total_time_elapsed_label.setText(elapsed_time_message)

    def update_total_progress_value(self, value):
        self.total_progress += value
        self.total_tracking_progress_bar.setValue(self.total_progress)

    def update_total_progress_range(self, value):
        self.total_tracking_progress_bar.setMaximum(value)

    def update_total_tracking_progress_bar_value(self, value, current_status):
        if current_status == 'Calculating Background':
            self.total_tracking_progress_bar.setValue(value)
        elif self.background is None and self.background_calculation_method == 'mode':
            self.total_tracking_progress_bar.setValue(self.video_n_frames + (value * 4))
        elif self.background is None:
            self.total_tracking_progress_bar.setValue(self.video_n_frames + (value * 9))
        else:
            self.total_tracking_progress_bar.setValue(value)

    def trigger_track_all_videos(self):
        self.total_progress = 0
        self.track_all_videos_thread = TrackAllVideosThread()
        self.track_all_videos_thread.loaded_videos_and_parameters_dict = self.loaded_videos_and_parameters_dict
        self.track_all_videos_thread.current_video_process_signal.connect(self.update_processing_video_label)
        self.track_all_videos_thread.current_status_signal.connect(self.update_current_status_label)
        self.track_all_videos_thread.total_time_elapsed_signal.connect(self.update_total_time_elapsed_label)
        self.track_all_videos_thread.processing_video_number_signal.connect(self.update_processing_video_number_label)
        self.track_all_videos_thread.current_progress_signal.connect(self.update_current_progress_value)
        self.track_all_videos_thread.current_progress_range_signal.connect(self.update_current_progress_range)
        self.track_all_videos_thread.total_progress_signal.connect(self.update_total_progress_value)
        self.track_all_videos_thread.total_progress_range_signal.connect(self.update_total_progress_range)
        self.track_all_videos_thread.current_tracking_finished_signal.connect(self.trigger_reset_progress_bar)
        self.track_all_videos_thread.total_tracking_finished_signal.connect(self.close)
        self.track_all_videos_thread.start()

    def trigger_reset_progress_bar(self):
        self.current_tracking_progress_bar.reset()

    def closeEvent(self, event):
        self.track_all_videos_progress_finished.emit(True)
        if self.track_all_videos_thread is not None:
            if self.track_all_videos_thread.isRunning():
                self.track_all_videos_thread.timer_thread.terminate()
                self.track_all_videos_thread.terminate()
        event.accept()

class TrackAllVideosThread(QThread):

    background_calculation_finished_signal = pyqtSignal(bool)
    total_tracking_finished_signal = pyqtSignal(bool)
    current_tracking_finished_signal = pyqtSignal(bool)
    current_progress_signal = pyqtSignal(float)
    total_progress_signal = pyqtSignal(float)
    total_progress_range_signal = pyqtSignal(float)
    current_video_process_signal = pyqtSignal(str)
    current_status_signal = pyqtSignal(str)
    total_time_elapsed_signal = pyqtSignal(float)
    processing_video_number_signal = pyqtSignal(int)
    current_progress_range_signal = pyqtSignal(float)

    def __init__(self):
        super(TrackAllVideosThread, self).__init__()
        self.initialize_class_variables()

    def initialize_class_variables(self):
        self.loaded_videos_and_parameters_dict = None

        self.video_path = None
        self.background = None
        self.colours = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.save_background = None
        self.tracking_method = None
        self.initial_pixel_search = None
        self.n_tail_points = None
        self.dist_tail_points = None
        self.dist_eyes = None
        self.dist_swim_bladder = None
        self.range_angles = None
        self.median_blur = None
        self.pixel_threshold = None
        self.frame_change_threshold = None
        self.heading_line_length = None
        self.extended_eyes_calculation = None
        self.eyes_threshold = None
        self.invert_threshold = None
        self.save_video = None
        self.starting_frame = None
        self.n_frames = None
        self.save_path = None
        self.video_fps = None

        self.periods = None
        self.start_time = None
        self.total_time_elapsed = None
        self.current_status = None
        self.i = None
        self.total_progress_range = None

        self.timer_thread = None

    def update_current_status(self, value):
        if self.current_status is not None:
            if self.periods is None:
                self.periods = '.'
            elif len(self.periods) == 6:
                self.periods = '.'
            else:
                self.periods += '.'
            self.current_status_signal.emit(self.current_status + self.periods)
        if self.start_time is None:
            self.start_time = value
            self.total_time_elapsed = self.start_time
        else:
            self.total_time_elapsed = value - self.start_time
        self.total_time_elapsed_signal.emit(self.total_time_elapsed)

    def run(self):
        self.timer_thread = TimerThread()
        self.timer_thread.start()
        self.timer_thread.time_signal.connect(self.update_current_status)

        all_videos_to_track = list(self.loaded_videos_and_parameters_dict.keys())
        self.total_progress_range = 0

        for i in range(len(all_videos_to_track)):
            if self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['background'] is None:
                if self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['tracking_parameters']['background_calculation_method'] == 'mode':
                    self.total_progress_range += self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['descriptors']['video_n_frames'] * 10
                else:
                    self.total_progress_range += self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['descriptors']['video_n_frames']
            if self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['tracking_parameters']['n_frames'] == 'All':
                self.total_progress_range += self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['descriptors']['video_n_frames'] * 10
            else:
                self.total_progress_range += self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['tracking_parameters']['n_frames'] * 10

        self.total_progress_range_signal.emit(self.total_progress_range)

        for i in range(len(all_videos_to_track)):
            self.i = i
            self.processing_video_number_signal.emit(self.i)

            self.video_n_frames = self.loaded_videos_and_parameters_dict[all_videos_to_track[i]]['descriptors']['video_n_frames']

            self.video_path = all_videos_to_track[i]
            self.current_video_process_signal.emit(self.video_path)

            self.background = self.loaded_videos_and_parameters_dict[self.video_path]['background']

            self.colours = self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters']

            self.background_calculation_method = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_method']
            self.background_calculation_frame_chunk_width = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frame_chunk_width']
            self.background_calculation_frame_chunk_height = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frame_chunk_height']
            self.background_calculation_frames_to_skip = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frames_to_skip']
            self.tracking_method = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['tracking_method']
            self.initial_pixel_search = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['initial_pixel_search']
            self.n_tail_points = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['n_tail_points']
            self.dist_tail_points = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['dist_tail_points']
            self.dist_eyes = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['dist_eyes']
            self.dist_swim_bladder = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['dist_swim_bladder']
            self.range_angles = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['range_angles']
            self.median_blur = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['median_blur']
            self.pixel_threshold = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['pixel_threshold']
            self.frame_change_threshold = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['frame_change_threshold']
            self.heading_line_length = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['heading_line_length']
            self.extended_eyes_calculation = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['extended_eyes_calculation']
            self.eyes_threshold = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['eyes_threshold']
            self.invert_threshold = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['invert_threshold']
            self.save_video = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['save_video']
            self.starting_frame = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['starting_frame']
            self.n_frames = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['n_frames']
            self.save_path = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['save_path']
            self.video_fps = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['video_fps']
            self.save_background = True

            self.current_progress_range_signal.emit(self.video_n_frames)

            if self.background is None:
                self.background = self.calculate_background(self.video_path, self.background_calculation_method, [self.background_calculation_frame_chunk_width, self.background_calculation_frame_chunk_height],
                                self.background_calculation_frames_to_skip, self.save_path, self.save_background)

            if self.n_frames == 'All':
                self.current_progress_range_signal.emit(self.video_n_frames)
            else:
                self.current_progress_range_signal.emit(self.n_frames)

            self.track_video(self.video_path, self.background, self.colours, self.tracking_method, self.initial_pixel_search, self.n_tail_points, self.dist_tail_points, self.dist_eyes,
                            self.dist_swim_bladder, self.range_angles, self.median_blur, self.pixel_threshold, self.frame_change_threshold, self.heading_line_length, self.extended_eyes_calculation, self.eyes_threshold,
                            self.invert_threshold, self.save_video, self.starting_frame, self.n_frames, self.save_path, self.video_fps)

            self.current_tracking_finished_signal.emit(True)

        time.sleep(0.5)
        self.total_tracking_finished_signal.emit(True)

    def calculate_background(self, video_path, method, chunk_size, frames_to_skip, save_path, save_background):
        # Check arguments.
        if not isinstance(video_path, str):
            print('Error: video_path must be formatted as a string.')
            return
        if not isinstance(method, str) or method not in ['brightest', 'darkest', 'mode']:
            print('Error: method must be formatted as a string and must be one of the following: brightest, darkest, or mode.')
            return
        if not isinstance(save_background, bool):
            print('Error: save_background must be formatted as a boolean (True/False).')
            return
        if not isinstance(chunk_size, list):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if len(chunk_size) != 2:
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(chunk_size[0], int) or not isinstance(chunk_size[1], int):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(frames_to_skip, int):
            print('Error: frames_to_skip must be formatted as an integer.')
            return

        self.current_status = 'Calculating Background'

        frame_size = ut.get_frame_size_from_video(video_path)
        video_n_frames = ut.get_total_frame_number_from_video(video_path)

        try:
            # Load the video.
            capture = cv2.VideoCapture(video_path)
            # Retrieve total number of frames in video.
            frames_to_skip += 1

            if method == 'mode':
                background = np.zeros(frame_size)
                pix = []
                width_iterations = int(frame_size[0]/chunk_size[0])
                if frame_size[0] % chunk_size[0] != 0:
                    width_iterations += 1
                height_iterations = int(frame_size[1] / chunk_size[1])
                if frame_size[1] % chunk_size[1] != 0:
                    height_iterations += 1
                for i in range(height_iterations):
                    for j in range(width_iterations):
                        for frame_num in range(video_n_frames):
                            self.current_progress_signal.emit((frame_num + 1 + (j * video_n_frames) + (video_n_frames * width_iterations * i)) / (width_iterations * height_iterations * video_n_frames) * video_n_frames)
                            self.total_progress_signal.emit(10)
                            success, frame = capture.read()
                            if success:
                                if frame_num % frames_to_skip == 0:
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    if i == height_iterations - 1 and j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : ])
                                    elif i == height_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                                    elif j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ])
                                    else:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                        bg_pix = stats.mode(pix)[0]
                        if i == height_iterations - 1 and j == width_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : ] = bg_pix
                        elif i == height_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        elif j == width_iterations - 1:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ] = bg_pix
                        else:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        pix = []
                        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                background = background.astype(np.uint8)
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
            else:
                # Iterate through each frame in the video.
                for frame_num in range(video_n_frames):
                    self.current_progress_signal.emit(frame_num + 1)
                    self.total_progress_signal.emit(1)
                    # Load frame into memory.
                    success, frame = capture.read()
                    # Check if frame was loaded successfully.
                    if success:
                        if frame_num % frames_to_skip == 0:
                            # Convert frame to grayscale.
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # Copy frame into background if this is the first frame.
                            if frame_num == 0:
                                background = frame.copy().astype(np.float32)
                            elif method == 'brightest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.less(background, frame)
                                # Update the background image where all of the pixels in the new frame are brighter than the background image.
                                background[mask] = frame[mask]
                            elif method == 'darkest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.greater(background, frame)
                                # Update the background image where all of the pixels in the new frame are darker than the background image.
                                background[mask] = frame[mask]
                background = background.astype(np.uint8)
                # Save the background into an external file if requested.
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
        except:
            # Errors that may occur during the background calculation are handled.
            print('Error calculating background')
            if capture.isOpened():
                capture.release()
            return None
        if capture.isOpened():
            # Unload video from memory.
            capture.release()
        # Return the calculated background.
        time.sleep(0.5)
        return background

    def track_video(self, video_path, background, colours, tracking_method, initial_pixel_search, n_tail_points, dist_tail_points, dist_eyes,
                    dist_swim_bladder, range_angles, median_blur, pixel_threshold, frame_change_threshold, heading_line_length, extended_eyes_calculation, eyes_threshold,
                    invert_threshold, save_video, starting_frame, n_frames, save_path, video_fps):

        # print(video_path, background, colours, tracking_method, initial_pixel_search, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, range_angles, median_blur, pixel_threshold, frame_change_threshold, heading_line_length, extended_eyes_calculation, eyes_threshold, invert_threshold, save_video, starting_frame, n_frames, save_path, video_fps)
        self.current_status = 'Tracking Video'
        colours = [[colours[i][2], colours[i][1], colours[i][0]] for i in range(len(colours))]

        if heading_line_length == 0:
            heading_line_length = dist_eyes

        if extended_eyes_calculation and eyes_line_length == 0:
            eyes_line_length = heading_line_length

        if save_path == None:
            save_path = os.path.dirname(video_path)

        video_n_frames = ut.get_total_frame_number_from_video(video_path)
        frame_size = ut.get_frame_size_from_video(video_path)

        # Get the fps.
        if video_fps is None:
            video_fps = get_fps_from_video(video_path)

        # Get the total number of frames.
        if n_frames == 'All':
            n_frames = video_n_frames

        if n_frames > video_n_frames:
            print('The number of frames requested to track exceeds the total number of frames in the video.')
            n_frames = video_n_frames

        if starting_frame >= video_n_frames:
            print('Starting frame number provided exceeds the total number of frames in the video. Setting the starting frame number to 0.')
            starting_frame = 0
            n_frames = video_n_frames

        if starting_frame + n_frames > video_n_frames:
            print('The number of frames requested to track plus the number of initial frames to offset exceeds the total number of frames in the video. Keeping the initial frames to offset and tracking the remaining frames.')
            n_frames = video_n_frames - starting_frame

        # Open the video path.
        capture = cv2.VideoCapture(video_path)

        # Set the frame position to start.
        capture.set(cv2.CAP_PROP_POS_FRAMES, starting_frame)

        if save_video:
            # Create a path for the video once it is tracked.
            save_video_path = "{0}\\{1}_tracked.avi".format(save_path, os.path.basename(video_path)[:-4])

            # Create video writer.
            writer = cv2.VideoWriter(save_video_path, 0, video_fps, frame_size)

        # Initialize variables for data.
        eye_coord_array = []
        eye_angle_array = []
        tail_coord_array = []
        body_coord_array = []
        heading_angle_array = []
        prev_frame = None
        prev_eye_angle = None

        range_angles = np.radians(range_angles)

        if tracking_method == 'free_swimming':
            # Iterate through each frame.
            for n in range(n_frames):
                self.current_progress_signal.emit(n + 1)
                self.total_progress_signal.emit(10)
                # Load a frame into memory.
                success, original_frame = capture.read()
                # Checks if the frame was loaded successfully.
                if success:
                    # Initialize variables for each frame.
                    first_eye_coords = [np.nan, np.nan]
                    second_eye_coords = [np.nan, np.nan]
                    first_eye_angle = np.nan
                    second_eye_angle = np.nan
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    swim_bladder_coords = [np.nan, np.nan]
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                    tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    # Convert the frame into the absolute difference between the frame and the background.
                    frame = cv2.absdiff(frame, background)
                    # Apply a median blur filter to the frame.
                    frame = cv2.medianBlur(frame, median_blur)
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.max(frame) > pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                swim_bladder_coords = tail_coord_array[len(tail_coord_array) - 1][0]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1][1:]
                            else:
                                # Return the coordinate of the brightest pixel.
                                first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                second_eye_coords = ut.calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Calculate the angle between the two eyes.
                                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Check if this is the first frame.
                                    if prev_eye_angle is not None:
                                        # Check if the difference between the current eye angle and previous eye angle is somwehere around pi, meaning the first and second eye coordiantes have reversed. Occasionally, the coordinates of the eyes will switch between one and the other. This method is useful for keeping the positions of the left and right eye the same between frames.
                                        if eye_angle - prev_eye_angle > np.pi / 2 or eye_angle - prev_eye_angle < -np.pi / 2:
                                            if eye_angle - prev_eye_angle < np.pi * 3 / 2 and eye_angle - prev_eye_angle > -np.pi * 3 / 2:
                                                # Switch the first and second eye coordinates.
                                                coords = first_eye_coords
                                                first_eye_coords = second_eye_coords
                                                second_eye_coords = coords
                                                # Calculate the new eye angle.
                                                eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Apply a threshold to the frame.
                                    thresh = ut.apply_threshold_to_frame(frame, eyes_threshold, invert = invert_threshold)
                                    # Find the contours of the binary regions in the thresholded frame.
                                    contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]
                                    # Iterate through each contour in the list of contours.
                                    for i in range(len(contours)):
                                        # Check if the first eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (first_eye_coords[1], first_eye_coords[0]), False) == 1:
                                            # Set the first eye coordinates to the centroid of the binary region and calculate the first eye angle.
                                            M = cv2.moments(contours[i])
                                            first_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            first_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                        # Check if the second eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (second_eye_coords[1], second_eye_coords[0]), False) == 1:
                                            # Set the second eye coordinates to the centroid of the binary region and calculate the second eye angle.
                                            M = cv2.moments(contours[i])
                                            second_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            second_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                # Find the midpoint of the line that connects both eyes.
                                heading_coords = [(first_eye_coords[0] + second_eye_coords[0]) / 2, (first_eye_coords[1] + second_eye_coords[1]) / 2]
                                # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                swim_bladder_coords = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                body_coords = [int(round((swim_bladder_coords[0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((swim_bladder_coords[1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                    body_contour = np.array([np.array([swim_bladder_coords[1], swim_bladder_coords[0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([second_eye_coords[1], second_eye_coords[0]])])
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (first_eye_coords[1] + (dist_eyes / 2 * np.cos(first_eye_angle)), first_eye_coords[0] + (dist_eyes / 2 * np.sin(first_eye_angle))), False) == 1:
                                        # Flip the first eye angle.
                                        if first_eye_angle > 0:
                                            first_eye_angle -= np.pi
                                        else:
                                            first_eye_angle += np.pi
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (second_eye_coords[1] + (dist_eyes / 2 * np.cos(second_eye_angle)), second_eye_coords[0] + (dist_eyes / 2 * np.sin(second_eye_angle))), False) == 1:
                                        # Flip the second eye angle.
                                        if second_eye_angle > 0:
                                            second_eye_angle -= np.pi
                                        else:
                                            second_eye_angle += np.pi
                                # Calculate the initial tail angle as the angle opposite to the heading angle.
                                if heading_angle > 0:
                                    tail_angle = heading_angle - np.pi
                                else:
                                    tail_angle = heading_angle + np.pi
                                # Iterate through the number of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point.
                                    if m == 0:
                                        # Calculate the first tail point using the swim bladder as the first set of coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                    else:
                                        # Check if this is the second tail point.
                                        if m == 1:
                                            # Calculate the next tail angle as the angle between the first tail point and the swim bladder.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - swim_bladder_coords[0], tail_point_coords[m - 1][1] - swim_bladder_coords[1])
                                        # Check if the number of tail points calculated is greater than 2.
                                        else:
                                            # Calculate the next tail angle as the angle between the last two tail points.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                        # Calculate the next set of tail coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                # Set the previous frame to the current frame.
                                prev_frame = frame
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Set the previous eye angle to the current eye angle.
                                    prev_eye_angle = eye_angle

                            if save_video:
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a line representing the first eye angle.
                                    original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (eyes_line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (eyes_line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                                    # Draw a circle around the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                    # Draw a line representing the second eye angle.
                                    original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (eyes_line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (eyes_line_length * np.sin(second_eye_angle))))), colours[-2], 1)
                                else:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a circle arround the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                # Iterate through each set of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point
                                    if m == 0:
                                        # For the first tail point, draw around the midpoint of the line that connects the swim bladder to the first tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((swim_bladder_coords[1] + tail_point_coords[m][1]) / 2)), int(round((swim_bladder_coords[0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                    else:
                                        # For all subsequent tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        swim_bladder_coords = [np.nan, np.nan]
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                        tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Iterate through the number of tail points, including the swim bladder coordinates.
                    for m in range(n_tail_points + 1):
                        # Check if this is the first tail point.
                        if m == 0:
                            # Add the swim bladder to a list that will contain all of the tail points, including the swim bladder.
                            tail_points[m] = swim_bladder_coords
                        else:
                            # Add all of the tail points to the list.
                            tail_points[m] = tail_point_coords[m - 1]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    tail_coord_array.append(tail_points)
                    body_coord_array.append(body_coords)
                    heading_angle_array.append(heading_angle)
                    if save_video:
                        # Write the new frame that contains the annotated frame with tracked points to a new video.
                        writer.write(original_frame)
        elif tracking_method == 'head_fixed':
            # Iterate through each frame.
            for n in range(n_frames):
                self.current_progress_signal.emit(n + 1)
                self.total_progress_signal.emit(10)
                # Load a frame into memory.
                success, original_frame = capture.read()
                # Checks if the frame was loaded successfully.
                if success:
                    # Initialize variables for each frame.
                    first_eye_coords = [np.nan, np.nan]
                    second_eye_coords = [np.nan, np.nan]
                    first_eye_angle = np.nan
                    second_eye_angle = np.nan
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    swim_bladder_coords = [np.nan, np.nan]
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                    tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.min(frame) < pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                swim_bladder_coords = tail_coord_array[len(tail_coord_array) - 1][0]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1][1:]
                            else:
                                if initial_pixel_search == 'darkest':
                                    # Return the coordinate of the brightest pixel.
                                    first_eye_coords = [np.where(frame == np.min(frame))[0][0], np.where(frame == np.min(frame))[1][0]]
                                elif initial_pixel_search == 'brightest':
                                    first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                second_eye_coords = ut.calculate_next_coords(first_eye_coords, dist_eyes, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Calculate the angle between the two eyes.
                                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Check if this is the first frame.
                                    if prev_eye_angle is not None:
                                        # Check if the difference between the current eye angle and previous eye angle is somwehere around pi, meaning the first and second eye coordiantes have reversed. Occasionally, the coordinates of the eyes will switch between one and the other. This method is useful for keeping the positions of the left and right eye the same between frames.
                                        if eye_angle - prev_eye_angle > np.pi / 2 or eye_angle - prev_eye_angle < -np.pi / 2:
                                            if eye_angle - prev_eye_angle < np.pi * 3 / 2 and eye_angle - prev_eye_angle > -np.pi * 3 / 2:
                                                # Switch the first and second eye coordinates.
                                                coords = first_eye_coords
                                                first_eye_coords = second_eye_coords
                                                second_eye_coords = coords
                                                # Calculate the new eye angle.
                                                eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                                    # Apply a threshold to the frame.
                                    thresh = ut.apply_threshold_to_frame(frame, eyes_threshold, invert = invert_threshold)
                                    # Find the contours of the binary regions in the thresholded frame.
                                    contours = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)[1]
                                    # Iterate through each contour in the list of contours.
                                    for i in range(len(contours)):
                                        # Check if the first eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (first_eye_coords[1], first_eye_coords[0]), False) == 1:
                                            # Set the first eye coordinates to the centroid of the binary region and calculate the first eye angle.
                                            M = cv2.moments(contours[i])
                                            first_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            first_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                        # Check if the second eye coordinate are within the current contour.
                                        if cv2.pointPolygonTest(contours[i], (second_eye_coords[1], second_eye_coords[0]), False) == 1:
                                            # Set the second eye coordinates to the centroid of the binary region and calculate the second eye angle.
                                            M = cv2.moments(contours[i])
                                            second_eye_coords = [int(round(M['m01']/M['m00'])), int(round(M['m10']/M['m00']))]
                                            second_eye_angle = cv2.fitEllipse(contours[i])[2] * np.pi / 180
                                # Find the midpoint of the line that connects both eyes.
                                heading_coords = [(first_eye_coords[0] + second_eye_coords[0]) / 2, (first_eye_coords[1] + second_eye_coords[1]) / 2]
                                # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                swim_bladder_coords = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Convert the frame into the absolute difference between the frame and the background.
                                frame = cv2.absdiff(frame, background)
                                # Apply a median blur filter to the frame.
                                frame = cv2.medianBlur(frame, median_blur)
                                # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                body_coords = [int(round((swim_bladder_coords[0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((swim_bladder_coords[1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                    body_contour = np.array([np.array([swim_bladder_coords[1], swim_bladder_coords[0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([second_eye_coords[1], second_eye_coords[0]])])
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (first_eye_coords[1] + (dist_eyes / 2 * np.cos(first_eye_angle)), first_eye_coords[0] + (dist_eyes / 2 * np.sin(first_eye_angle))), False) == 1:
                                        # Flip the first eye angle.
                                        if first_eye_angle > 0:
                                            first_eye_angle -= np.pi
                                        else:
                                            first_eye_angle += np.pi
                                    # Check to see if the point that is created by drawing a line from the first eye coordinates with a length equal to half of the distance between the eyes is within the body contour. Occasionally, the angle of the eye is flipped to face towards the body instead of away. This is to check whether or not the eye angle should be flipped.
                                    if cv2.pointPolygonTest(body_contour, (second_eye_coords[1] + (dist_eyes / 2 * np.cos(second_eye_angle)), second_eye_coords[0] + (dist_eyes / 2 * np.sin(second_eye_angle))), False) == 1:
                                        # Flip the second eye angle.
                                        if second_eye_angle > 0:
                                            second_eye_angle -= np.pi
                                        else:
                                            second_eye_angle += np.pi
                                # Calculate the initial tail angle as the angle opposite to the heading angle.
                                if heading_angle > 0:
                                    tail_angle = heading_angle - np.pi
                                else:
                                    tail_angle = heading_angle + np.pi
                                # Iterate through the number of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point.
                                    if m == 0:
                                        # Calculate the first tail point using the swim bladder as the first set of coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                    else:
                                        # Check if this is the second tail point.
                                        if m == 1:
                                            # Calculate the next tail angle as the angle between the first tail point and the swim bladder.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - swim_bladder_coords[0], tail_point_coords[m - 1][1] - swim_bladder_coords[1])
                                        # Check if the number of tail points calculated is greater than 2.
                                        else:
                                            # Calculate the next tail angle as the angle between the last two tail points.
                                            tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                        # Calculate the next set of tail coordinates.
                                        tail_point_coords[m] = ut.calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                # Set the previous frame to the current frame.
                                prev_frame = frame
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Set the previous eye angle to the current eye angle.
                                    prev_eye_angle = eye_angle

                            if save_video:
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a line representing the first eye angle.
                                    original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (eyes_line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (eyes_line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                                    # Draw a circle around the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                    # Draw a line representing the second eye angle.
                                    original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (eyes_line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (eyes_line_length * np.sin(second_eye_angle))))), colours[-2], 1)
                                else:
                                    # Draw a circle arround the first eye coordinates.
                                    original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                                    # Draw a circle arround the second eye coordinates.
                                    original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                                # Iterate through each set of tail points.
                                for m in range(n_tail_points):
                                    # Check if this is the first tail point
                                    if m == 0:
                                        # For the first tail point, draw around the midpoint of the line that connects the swim bladder to the first tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((swim_bladder_coords[1] + tail_point_coords[m][1]) / 2)), int(round((swim_bladder_coords[0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                    else:
                                        # For all subsequent tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                        original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        swim_bladder_coords = [np.nan, np.nan]
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points)]
                        tail_points = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Iterate through the number of tail points, including the swim bladder coordinates.
                    for m in range(n_tail_points + 1):
                        # Check if this is the first tail point.
                        if m == 0:
                            # Add the swim bladder to a list that will contain all of the tail points, including the swim bladder.
                            tail_points[m] = swim_bladder_coords
                        else:
                            # Add all of the tail points to the list.
                            tail_points[m] = tail_point_coords[m - 1]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    tail_coord_array.append(tail_points)
                    body_coord_array.append(body_coords)
                    heading_angle_array.append(heading_angle)
                    if save_video:
                        # Write the new frame that contains the annotated frame with tracked points to a new video.
                        writer.write(original_frame)

        # Unload the video and writer from memory.
        capture.release()
        if save_video:
            writer.release()

        # Create a dictionary that contains all of the results.
        results =   {   'eye_coord_array' : eye_coord_array,
                        'eye_angle_array' : eye_angle_array,
                        'tail_coord_array' : tail_coord_array,
                        'body_coord_array' : body_coord_array,
                        'heading_angle_array' : heading_angle_array,
                        'video_path' : video_path,
                        'video_n_frames' : video_n_frames,
                        'video_fps' : video_fps,
                        'dist_tail_points' : dist_tail_points,
                        'dist_eyes' : dist_eyes,
                        'dist_swim_bladder' : dist_swim_bladder,
                        'eyes_threshold' : eyes_threshold,
                        'pixel_threshold' : pixel_threshold,
                        'frame_change_threshold' : frame_change_threshold,
                        'colours' : colours
                    }

        # Create a path that will contain all of the results from tracking.
        data_path = "{0}\\{1}_results.npy".format(save_path, os.path.basename(video_path)[:-4])

        # Save the results to a npz file.
        np.save(data_path, results)

class CalculateBackgroundProgressWindow(QMainWindow):

    background_calculation_completed_signal = pyqtSignal(bool)

    # Defining Initialization Functions
    def __init__(self):
        super(CalculateBackgroundProgressWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.initialize_class_variables()
        self.add_processing_video_label()
        self.add_current_status_label()
        self.add_background_calculation_progress_bar()
        self.add_total_time_elapsed_label()
        self.add_cancel_background_calculation_button()
        self.setWindowTitle('Background Calculation in Progress')
        self.setFixedSize(500, 200)

    def initialize_class_variables(self):
        self.video_path = None
        self.background = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.save_path = None
        self.save_background = None
        self.calculate_background_thread = None

        self.video_n_frames = None

    def add_processing_video_label(self):
        self.processing_video_label = QLabel(self)
        self.processing_video_label.move(40, 10)
        self.processing_video_label.resize(400, 20)

    def add_current_status_label(self):
        self.current_status_label = QLabel(self)
        self.current_status_label.move(40, 40)
        self.current_status_label.resize(400, 20)

    def add_background_calculation_progress_bar(self):
        self.background_calculation_progress_bar = QProgressBar(self)
        self.background_calculation_progress_bar.move(50, 70)
        self.background_calculation_progress_bar.resize(400, 30)
        self.background_calculation_progress_bar.setMinimum(0)

    def add_total_time_elapsed_label(self):
        self.total_time_elapsed_label = QLabel(self)
        self.total_time_elapsed_label.move(40, 110)
        self.total_time_elapsed_label.resize(400, 20)

    def add_cancel_background_calculation_button(self):
        self.cancel_background_calculation_button = QPushButton('Cancel', self)
        self.cancel_background_calculation_button.move(150, 140)
        self.cancel_background_calculation_button.resize(200, 50)
        self.cancel_background_calculation_button.clicked.connect(self.close)

    def update_processing_video_label(self):
        self.processing_video_label.setText('Processing Video: {0}'.format(self.video_path))

    def update_current_status_label(self, value):
        self.current_status_label.setText('Current Status: {0}'.format(value))

    def update_progress_bar_range(self):
        self.background_calculation_progress_bar.setMaximum(self.video_n_frames)

    def update_background_calculation_progress_from_background_calculation_thread(self, value):
        self.background_calculation_progress_bar.setValue(value)

    def update_current_status_label_from_background_calculation_thread(self, value):
        self.current_status_label.setText('Current Status: {0}'.format(value))

    def update_total_time_elapsed_label(self, value):
        elapsed_time = int(round(value, 0))
        hours, minutes, seconds = ut.convert_total_seconds_to_hours_minutes_seconds(elapsed_time)
        elapsed_time_message = 'Total Time Elapsed: '
        if hours != 0:
            if hours == 1:
                elapsed_time_message += '{0} hour '.format(hours)
            else:
                elapsed_time_message += '{0} hours '.format(hours)
        if minutes != 0:
            if minutes == 1:
                elapsed_time_message += '{0} minute '.format(minutes)
            else:
                elapsed_time_message += '{0} minutes '.format(minutes)
        if seconds != 0:
            if seconds == 1:
                elapsed_time_message += '{0} second '.format(seconds)
            else:
                elapsed_time_message += '{0} seconds '.format(seconds)
        if hours != 0 or minutes != 0 or seconds != 0:
            elapsed_time_message = elapsed_time_message[:-1] + '.'
        self.total_time_elapsed_label.setText(elapsed_time_message)

    def update_background_calculation_completed_signal(self):
        self.background = self.calculate_background_thread.background
        self.background_calculation_completed_signal.emit(True)
        self.close()

    def trigger_calculate_background(self):
        self.calculate_background_thread = CalculateBackgroundThread()
        self.calculate_background_thread.video_path = self.video_path
        self.calculate_background_thread.background_calculation_method = self.background_calculation_method
        self.calculate_background_thread.background_calculation_frame_chunk_width = self.background_calculation_frame_chunk_width
        self.calculate_background_thread.background_calculation_frame_chunk_height = self.background_calculation_frame_chunk_height
        self.calculate_background_thread.background_calculation_frames_to_skip = self.background_calculation_frames_to_skip
        self.calculate_background_thread.save_path = self.save_path
        self.calculate_background_thread.save_background = self.save_background
        self.calculate_background_thread.start()
        self.calculate_background_thread.progress_signal.connect(self.update_background_calculation_progress_from_background_calculation_thread)
        self.calculate_background_thread.current_status_signal.connect(self.update_current_status_label)
        self.calculate_background_thread.total_time_elapsed_signal.connect(self.update_total_time_elapsed_label)
        self.calculate_background_thread.background_calculation_finished_signal.connect(self.update_background_calculation_completed_signal)

    def closeEvent(self, event):
        if self.calculate_background_thread is not None:
            # if self.calculate_background_thread.timer_thread is not None:
            #     if self.calculate_background_thread.timer_thread.isRunning():
            #         self.calculate_background_thread.timer_thread.terminate()
            if self.calculate_background_thread.isRunning():
                self.calculate_background_thread.timer_thread.terminate()
                self.calculate_background_thread.terminate()
        event.accept()

class CalculateBackgroundThread(QThread):

    background_calculation_finished_signal = pyqtSignal(bool)
    progress_signal = pyqtSignal(float)
    current_status_signal = pyqtSignal(str)
    total_time_elapsed_signal = pyqtSignal(float)

    def __init__(self):
        super(CalculateBackgroundThread, self).__init__()
        self.initialize_class_variables()

    def initialize_class_variables(self):
        self.background = None
        self.video_path = None
        self.background_calculation_method = None
        self.background_calculation_frame_chunk_width = None
        self.background_calculation_frame_chunk_height = None
        self.background_calculation_frames_to_skip = None
        self.timer_thread = None
        self.periods = None
        self.current_status = None
        self.start_time = None
        self.total_time_elapsed = None

    def update_current_status(self, value):
        if self.current_status is not None:
            if self.periods is None:
                self.periods = '.'
            elif len(self.periods) == 6:
                self.periods = '.'
            else:
                self.periods += '.'
            self.current_status_signal.emit(self.current_status + self.periods)
        if self.start_time is None:
            self.start_time = value
            self.total_time_elapsed = self.start_time
        else:
            self.total_time_elapsed = value - self.start_time
        self.total_time_elapsed_signal.emit(self.total_time_elapsed)

    def run(self):
        self.timer_thread = TimerThread()
        self.timer_thread.start()
        self.timer_thread.time_signal.connect(self.update_current_status)
        self.background = self.calculate_background(self.video_path, self.background_calculation_method, [self.background_calculation_frame_chunk_width, self.background_calculation_frame_chunk_height], self.background_calculation_frames_to_skip, self.save_path, self.save_background)
        self.background_calculation_finished_signal.emit(True)

    def calculate_background(self, video_path, method, chunk_size, frames_to_skip, save_path, save_background):
        # Check arguments.
        if not isinstance(video_path, str):
            print('Error: video_path must be formatted as a string.')
            return
        if not isinstance(method, str) or method not in ['brightest', 'darkest', 'mode']:
            print('Error: method must be formatted as a string and must be one of the following: brightest, darkest, or mode.')
            return
        if not isinstance(save_background, bool):
            print('Error: save_background must be formatted as a boolean (True/False).')
            return
        if not isinstance(chunk_size, list):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if len(chunk_size) != 2:
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(chunk_size[0], int) or not isinstance(chunk_size[1], int):
            print('Error: chunk_size must be formatted as a list containing 2 integer values.')
            return
        if not isinstance(frames_to_skip, int):
            print('Error: frames_to_skip must be formatted as an integer.')
            return

        self.current_status = 'Calculating Background'

        frame_size = ut.get_frame_size_from_video(video_path)
        video_n_frames = ut.get_total_frame_number_from_video(video_path)

        try:
            # Load the video.
            capture = cv2.VideoCapture(video_path)
            # Retrieve total number of frames in video.
            frames_to_skip += 1

            if method == 'mode':
                background = np.zeros(frame_size)
                pix = []
                width_iterations = int(frame_size[0]/chunk_size[0])
                if frame_size[0] % chunk_size[0] != 0:
                    width_iterations += 1
                height_iterations = int(frame_size[1] / chunk_size[1])
                if frame_size[1] % chunk_size[1] != 0:
                    height_iterations += 1
                for i in range(height_iterations):
                    for j in range(width_iterations):
                        for frame_num in range(video_n_frames):
                            self.progress_signal.emit((frame_num + 1 + (j * video_n_frames) + (video_n_frames * width_iterations * i)) / (width_iterations * height_iterations * video_n_frames) * video_n_frames)
                            success, frame = capture.read()
                            if success:
                                if frame_num % frames_to_skip == 0:
                                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                                    if i == height_iterations - 1 and j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : ])
                                    elif i == height_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                                    elif j == width_iterations - 1:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ])
                                    else:
                                        pix.append(frame[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]])
                        bg_pix = stats.mode(pix)[0]
                        if i == height_iterations - 1 and j == width_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : ] = bg_pix
                        elif i == height_iterations - 1:
                            background[i * chunk_size[1] : , j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        elif j == width_iterations - 1:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : ] = bg_pix
                        else:
                            background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                        pix = []
                        capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                background = background.astype(np.uint8)
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
            else:
                # Iterate through each frame in the video.
                for frame_num in range(video_n_frames):
                    self.progress_signal.emit(frame_num + 1)
                    # Load frame into memory.
                    success, frame = capture.read()
                    # Check if frame was loaded successfully.
                    if success:
                        if frame_num % frames_to_skip == 0:
                            # Convert frame to grayscale.
                            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                            # Copy frame into background if this is the first frame.
                            if frame_num == 0:
                                background = frame.copy().astype(np.float32)
                            elif method == 'brightest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.less(background, frame)
                                # Update the background image where all of the pixels in the new frame are brighter than the background image.
                                background[mask] = frame[mask]
                            elif method == 'darkest':
                                # Create a mask where the background is compared to the frame in the loop and used to update the background where the frame is.
                                mask = np.greater(background, frame)
                                # Update the background image where all of the pixels in the new frame are darker than the background image.
                                background[mask] = frame[mask]
                background = background.astype(np.uint8)
                # Save the background into an external file if requested.
                if save_background:
                    if save_path != None:
                        background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                    else:
                        background_path = '{0}_background.tif'.format(video_path[:-4])
                    cv2.imwrite(background_path, background)
        except:
            # Errors that may occur during the background calculation are handled.
            print('Error calculating background')
            if capture.isOpened():
                capture.release()
            return None
        if capture.isOpened():
            # Unload video from memory.
            capture.release()
        # Return the calculated background.
        time.sleep(0.5)
        return background

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
            data = np.load(self.tracking_data_path).item()
            self.data_plot = DataPlot()
            self.data_plot.initialize_class_variables(data = data)
            self.data_plot.calculate_variables()
            self.data_plot.update_plots()
            self.update_data_plot_window()
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
                self.video_playback_thread = VideoPlaybackThread()
                self.video_playback_thread.video_fps = self.video_fps
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
        for i in range(1, len(self.tail_angle_frames)):
            if self.tail_angle_frames[i] - self.tail_angle_frames[i - 1] == 2:
                self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 1)
            elif self.tail_angle_frames[i] - self.tail_angle_frames[i - 1] == 3:
                self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 1)
                self.tail_angle_frames = np.append(self.tail_angle_frames, self.tail_angle_frames[i - 1] + 2)

        # for i in range(len(self.tail_angles)):
        #     for j in self.tail_angle_frames:
        #         self.tail_angles[i][j] = 0.0
        self.smoothed_tail_angles = [np.convolve(self.tail_angles[i], np.ones(self.smoothing_factor)/self.smoothing_factor, mode = 'same') for i in range(len(self.tail_angles))]

        j = 0
        if np.isnan(self.heading_angle_array[0]):
            while np.isnan(self.heading_angle_array[0]):
                if not np.isnan(self.heading_angle_array[j]):
                    self.heading_angle_array[0] = self.heading_angle_array[j]
                j += 1

        self.heading_angles = np.array([self.heading_angle_array[i] - self.heading_angle_array[0] for i in range(len(self.heading_angle_array))])

        i = 0
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

        i = 0
        for k in range(len(self.eye_angles)):
            for j in range(len(self.eye_angles[k])):
                if j not in self.tail_angle_frames:
                    i = j
                else:
                    self.eye_angles[k][j] = self.eye_angles[k][i]

        for j in range(len(self.eye_angles)):
            for i in range(1, len(self.eye_angles[j])):
                if self.eye_angles[j][i] - self.eye_angles[j][i - 1] > np.pi * 0.9:
                    self.eye_angles[j][i] -= np.pi * 2
                elif self.eye_angles[j][i] - self.eye_angles[j][i - 1] < -np.pi * 0.9:
                    self.eye_angles[j][i] += np.pi * 2

        for j in range(len(self.eye_angles)):
            for i in range(1, len(self.eye_angles[j])):
                if self.eye_angles[j][i] > np.pi:
                    self.eye_angles[j][i] -= np.pi * 2
                elif self.eye_angles[j][i] < -np.pi:
                    self.eye_angles[j][i] += np.pi * 2

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

class TimerThread(QThread):

    time_signal = pyqtSignal(float)

    def __init__(self):
        super(TimerThread, self).__init__()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            time_now = time.perf_counter()
            self.time_signal.emit(time_now)
            time.sleep(0.5)

class VideoPlaybackThread(QThread):

    time_signal = pyqtSignal(float)

    def __init__(self):
        super(VideoPlaybackThread, self).__init__()
        self.start_thread = True
        self.video_fps = None

    def run(self):
        while self.start_thread:
            time_now = time.perf_counter()
            self.time_signal.emit(time_now)
            time.sleep(0.1)

    def close(self):
        self.start_thread = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
