'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import sys
from tracking_window import TrackingWindow
from plotting_window import PlottingWindow

from PyQt5.QtWidgets import QMainWindow, QTabWidget, QApplication, QDesktopWidget, QMenuBar, QAction
from PyQt5.QtCore import Qt

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

    def get_main_window_attributes(self):
        self.main_window_width = QDesktopWidget().availableGeometry().width()
        self.main_window_height = QDesktopWidget().availableGeometry().height()

    def add_menubar(self):
        self.menubar = QMenuBar()
        self.menubar.resize(self.main_window_width, self.menubar.height())
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
