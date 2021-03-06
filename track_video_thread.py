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

        self.video_path = list(self.loaded_videos_and_parameters_dict.keys())[0]
        self.starting_frame = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['starting_frame']
        self.n_frames = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['n_frames']
        self.video_n_frames = self.loaded_videos_and_parameters_dict[self.video_path]['descriptors']['video_n_frames']

        self.track_video_thread = TrackVideoThread()
        self.track_video_thread.loaded_videos_and_parameters_dict = self.loaded_videos_and_parameters_dict
        self.update_processing_video_label()
        self.update_progress_bar_range()
        self.update_total_tracking_progress_bar_range()
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
        self.recalculate_eye_coords_every_frame = None
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
        self.mask = None

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

        self.video_path = list(self.loaded_videos_and_parameters_dict.keys())[0]
        self.background = self.loaded_videos_and_parameters_dict[self.video_path]['background']
        self.colours = self.loaded_videos_and_parameters_dict[self.video_path]['colour_parameters']
        self.mask = self.loaded_videos_and_parameters_dict[self.video_path]['mask']
        self.video_n_frames = self.loaded_videos_and_parameters_dict[self.video_path]['descriptors']['video_n_frames']
        self.background_calculation_method = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_method']
        self.background_calculation_frame_chunk_width = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frame_chunk_width']
        self.background_calculation_frame_chunk_height = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frame_chunk_height']
        self.background_calculation_frames_to_skip = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['background_calculation_frames_to_skip']
        self.tracking_method = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['tracking_method']
        self.initial_pixel_search = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['initial_pixel_search']
        self.recalculate_eye_coords_every_frame = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['recalculate_eye_coords_every_frame']
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
        self.eyes_line_length = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['eyes_line_length']
        self.invert_threshold = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['invert_threshold']
        self.save_video = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['save_video']
        self.starting_frame = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['starting_frame']
        self.n_frames = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['n_frames']
        self.save_path = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['save_path']
        self.video_fps = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['video_fps']
        self.save_background = self.loaded_videos_and_parameters_dict[self.video_path]['tracking_parameters']['save_background']

        if self.background is None:
            self.background = self.calculate_background(self.video_path, self.background_calculation_method, [self.background_calculation_frame_chunk_width, self.background_calculation_frame_chunk_height],
                            self.background_calculation_frames_to_skip, self.save_path, self.save_background)

        self.track_video(self.video_path, self.background, self.colours, self.tracking_method, self.initial_pixel_search, self.n_tail_points, self.dist_tail_points, self.dist_eyes,
                        self.dist_swim_bladder, self.range_angles, self.median_blur, self.pixel_threshold, self.frame_change_threshold, self.heading_line_length, self.extended_eyes_calculation, self.eyes_threshold,
                        self.eyes_line_length, self.invert_threshold, self.save_video, self.starting_frame, self.n_frames, self.save_path, self.video_fps, self.mask, self.recalculate_eye_coords_every_frame)

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
                    eyes_line_length, invert_threshold, save_video, starting_frame, n_frames, save_path, video_fps, mask, recalculate_eye_coords_every_frame):

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
        heading_coord_array = []
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
                    heading_coords = [np.nan, np.nan]
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    # Convert the frame into the absolute difference between the frame and the background.
                    frame = cv2.absdiff(frame, background)
                    # Apply a median blur filter to the frame.
                    frame = cv2.medianBlur(frame, median_blur)
                    if mask:
                        center_x, center_y, width, height, type = mask
                        if type == 'rectangle':
                            Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                            x_dist_from_center = ((X - center_x) / width) ** 2 + (Y * 0)
                            y_dist_from_center = ((Y - center_y) / height) ** 2 + (X * 0)
                            frame[(x_dist_from_center > 1) | (y_dist_from_center > 1)] = 0
                        elif type == 'ellipse':
                            Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                            dist_from_center = ((X - center_x) / width) ** 2 + ((Y - center_y) / height) ** 2
                            frame[dist_from_center > 1] = 0
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.max(frame) > pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_coords = heading_coord_array[len(heading_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1]
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
                                tail_point_coords[0] = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                body_coords = [int(round((tail_point_coords[0][0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((tail_point_coords[0][1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                # Check whether to to an additional process to calculate eye angles.
                                if extended_eyes_calculation:
                                    # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                    body_contour = np.array([np.array([tail_point_coords[0][1], tail_point_coords[0][0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([int(round(heading_coords[1] + (dist_eyes / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] + (dist_eyes / 2 * np.sin(heading_angle))))]), np.array([second_eye_coords[1], second_eye_coords[0]])])
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
                                    if np.isnan(first_eye_angle) or np.isnan(second_eye_angle):
                                        print('Warning: Extended eyes calculation failed. Proceeding with normal eye tracking.')
                                        # Return the coordinate of the brightest pixel.
                                        first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                        # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                        second_eye_coords = calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                        first_eye_angle, second_eye_angle = [np.nan, np.nan]
                                # Iterate through the number of tail points.
                                for m in range(1, n_tail_points + 1):
                                    # Check if this is the first tail point.
                                    if m == 1:
                                        # Calculate the initial tail angle as the angle opposite to the heading angle.
                                        if heading_angle > 0:
                                            tail_angle = heading_angle - np.pi
                                        else:
                                            tail_angle = heading_angle + np.pi
                                    else:
                                        # Calculate the next tail angle as the angle between the last two tail points.
                                        tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                    # Calculate the first tail point using the swim bladder as the first set of coordinates.
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
                                for m in range(1, n_tail_points + 1):
                                    # For all tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                    original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m - 1], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        print('Error! Could not track tail in frame: {0}.'.format(n))
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        heading_coords = [np.nan, np.nan]
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    heading_coord_array.append(heading_coords)
                    tail_coord_array.append(tail_point_coords)
                    body_coord_array.append(body_coords)
                    heading_angle_array.append(heading_angle)
                    if save_video:
                        print('Writing frame: {0}'.format(n))
                        # Write the new frame that contains the annotated frame with tracked points to a new video.
                        writer.write(original_frame)
        elif tracking_method == 'head_fixed_1' or tracking_method == 'head_fixed_2':
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
                    heading_coords = [np.nan, np.nan]
                    body_coords = [np.nan, np.nan]
                    heading_angle = np.nan
                    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Convert the original frame to grayscale.
                    frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
                    if mask and initial_pixel_search == 'darkest':
                        center_x, center_y, width, height, type = mask
                        if type == 'rectangle':
                            Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                            x_dist_from_center = ((X - center_x) / width) ** 2 + (Y * 0)
                            y_dist_from_center = ((Y - center_y) / height) ** 2 + (X * 0)
                            frame[(x_dist_from_center > 1) | (y_dist_from_center > 1)] = 255
                        elif type == 'ellipse':
                            Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                            dist_from_center = ((X - center_x) / width) ** 2 + ((Y - center_y) / height) ** 2
                            frame[dist_from_center > 1] = 255
                    elif mask and initial_pixel_search == 'brightest':
                        if mask:
                            center_x, center_y, width, height, type = mask
                            if type == 'rectangle':
                                Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                                x_dist_from_center = ((X - center_x) / width) ** 2 + (Y * 0)
                                y_dist_from_center = ((Y - center_y) / height) ** 2 + (X * 0)
                                frame[(x_dist_from_center > 1) | (y_dist_from_center > 1)] = 0
                            elif type == 'ellipse':
                                Y, X = np.ogrid[:frame.shape[0], :frame.shape[1]]
                                dist_from_center = ((X - center_x) / width) ** 2 + ((Y - center_y) / height) ** 2
                                frame[dist_from_center > 1] = 0
                    try:
                        # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                        if np.min(frame) < pixel_threshold:
                            # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                            if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) >= frame_change_threshold) == 0:
                                # If the difference between the current frame and the previous frame is less than a certain threshold, then use the values that were previously calculated.
                                first_eye_coords, second_eye_coords = eye_coord_array[len(eye_coord_array) - 1]
                                first_eye_angle, second_eye_angle = eye_angle_array[len(eye_angle_array) - 1]
                                body_coords = body_coord_array[len(body_coord_array) - 1]
                                heading_coords = heading_coord_array[len(heading_coord_array) - 1]
                                heading_angle = heading_angle_array[len(heading_angle_array) - 1]
                                tail_point_coords = tail_coord_array[len(tail_coord_array) - 1]
                            else:
                                if not recalculate_eye_coords_every_frame and n > 0 and not np.isnan(eye_coord_array[0]).any():
                                    first_eye_coords, second_eye_coords = eye_coord_array[0]
                                    first_eye_angle, second_eye_angle = eye_angle_array[0]
                                    body_coords = body_coord_array[0]
                                    heading_coords = heading_coord_array[0]
                                    heading_angle = heading_angle_array[0]
                                    tail_point_coords[0] = tail_coord_array[0][0]
                                    # Convert the frame into the absolute difference between the frame and the background.
                                    frame = cv2.absdiff(frame, background)
                                    # Apply a median blur filter to the frame.
                                    frame = cv2.medianBlur(frame, median_blur)
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
                                    if tracking_method == 'head_fixed_1':
                                        # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                        tail_point_coords[0] = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                        # Apply mask to frame.
                                        if mask:
                                            if type == 'rectangle':
                                                background[(x_dist_from_center > 1) | (y_dist_from_center > 1)] = frame[(x_dist_from_center > 1) | (y_dist_from_center > 1)]
                                            elif type == 'ellipse':
                                                background[dist_from_center > 1] = frame[dist_from_center > 1]
                                        # Convert the frame into the absolute difference between the frame and the background.
                                        frame = cv2.absdiff(frame, background)
                                        # Apply a median blur filter to the frame.
                                        frame = cv2.medianBlur(frame, median_blur)
                                    if tracking_method == 'head_fixed_2':
                                        # Apply mask to frame.
                                        if mask:
                                            if type == 'rectangle':
                                                background[(x_dist_from_center > 1) | (y_dist_from_center > 1)] = frame[(x_dist_from_center > 1) | (y_dist_from_center > 1)]
                                            elif type == 'ellipse':
                                                background[dist_from_center > 1] = frame[dist_from_center > 1]
                                        # Convert the frame into the absolute difference between the frame and the background.
                                        frame = cv2.absdiff(frame, background)
                                        # Apply a median blur filter to the frame.
                                        frame = cv2.medianBlur(frame, median_blur)
                                        # Find the swim bladder coordinates by finding the next brightest coordinates that lie on a circle around the heading coordinates with a radius equal to the distance between the eyes and the swim bladder.
                                        tail_point_coords[0] = ut.calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                    # Find the body coordinates by finding the center of the triangle that connects the eyes and swim bladder.
                                    body_coords = [int(round((tail_point_coords[0][0] + first_eye_coords[0] + second_eye_coords[0]) / 3)), int(round((tail_point_coords[0][1] + first_eye_coords[1] + second_eye_coords[1]) / 3))]
                                    # Calculate the heading angle as the angle between the body coordinates and the heading coordinates.
                                    heading_angle = np.arctan2(heading_coords[0] - body_coords[0], heading_coords[1] - body_coords[1])
                                    # Check whether to to an additional process to calculate eye angles.
                                    if extended_eyes_calculation:
                                        # Create an array that acts as a contour for the body and contains the swim bladder coordinates and eye coordinates.
                                        body_contour = np.array([np.array([tail_point_coords[0][1], tail_point_coords[0][0]]), np.array([first_eye_coords[1], first_eye_coords[0]]), np.array([int(round(heading_coords[1] + (dist_eyes / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] + (dist_eyes / 2 * np.sin(heading_angle))))]), np.array([second_eye_coords[1], second_eye_coords[0]])])
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
                                        if np.isnan(first_eye_angle) or np.isnan(second_eye_angle):
                                            print('Warning: Extended eyes calculation failed. Proceeding with normal eye tracking.')
                                            if initial_pixel_search == 'darkest':
                                                # Return the coordinate of the brightest pixel.
                                                first_eye_coords = [np.where(frame == np.min(frame))[0][0], np.where(frame == np.min(frame))[1][0]]
                                            elif initial_pixel_search == 'brightest':
                                                first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                                            # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                                            second_eye_coords = ut.calculate_next_coords(first_eye_coords, dist_eyes, frame, method = initial_pixel_search, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                                            first_eye_angle, second_eye_angle = [np.nan, np.nan]
                                        # Set the previous eye angle to the current eye angle.
                                        prev_eye_angle = eye_angle
                                    # Iterate through the number of tail points.
                                for m in range(1, n_tail_points + 1):
                                    # Check if this is the first tail point.
                                    if m == 1:
                                        # Calculate the initial tail angle as the angle opposite to the heading angle.
                                        if heading_angle > 0:
                                            tail_angle = heading_angle - np.pi
                                        else:
                                            tail_angle = heading_angle + np.pi
                                    else:
                                        # Calculate the next tail angle as the angle between the last two tail points.
                                        tail_angle = np.arctan2(tail_point_coords[m - 1][0] - tail_point_coords[m - 2][0], tail_point_coords[m - 1][1] - tail_point_coords[m - 2][1])
                                    # Calculate the first tail point using the swim bladder as the first set of coordinates.
                                    tail_point_coords[m] = ut.calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle, range_angles = range_angles)
                                # Set the previous frame to the current frame.
                                prev_frame = frame
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
                                for m in range(1, n_tail_points + 1):
                                    # For all subsequent tail points, draw around the midpoint of the line that connects the previous tail point to the current tail point.
                                    original_frame = cv2.circle(original_frame, (int(round((tail_point_coords[m - 1][1] + tail_point_coords[m][1]) / 2)), int(round((tail_point_coords[m - 1][0] + tail_point_coords[m][0]) / 2))), 1, colours[m - 1], -1)
                                # Draw an arrow for the heading angle.
                                original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (heading_line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (heading_line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (heading_line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (heading_line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
                    except:
                        # Handles any errors that occur throughout tracking.
                        print('Error! Could not track tail in frame: {0}.'.format(n))
                        first_eye_coords = [np.nan, np.nan]
                        second_eye_coords = [np.nan, np.nan]
                        first_eye_angle = np.nan
                        second_eye_angle = np.nan
                        heading_coords = [np.nan, np.nan]
                        body_coords = [np.nan, np.nan]
                        heading_angle = np.nan
                        tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
                    # Add all of the important features that were tracked into lists.
                    eye_coord_array.append([first_eye_coords, second_eye_coords])
                    eye_angle_array.append([first_eye_angle, second_eye_angle])
                    heading_coord_array.append(heading_coords)
                    tail_coord_array.append(tail_point_coords)
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
                        'heading_coord_array' : heading_coord_array,
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
