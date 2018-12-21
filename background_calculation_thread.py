'''Software Written by Nicholas Guilbeault 2018'''

# import python modules
import os
import cv2
import numpy as np
import utilities as ut
import time
from timer_thread import TimerThread

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
