'''Software Written by Nicholas Guilbeault 2018'''

# Import libraries.
import numpy as np
import cv2
import os
import sys
import multiprocessing as mp
import time
import scipy.stats as stats

def get_total_frame_number_from_video(video_path):
    capture = cv2.VideoCapture(video_path)
    total_frame_number = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()
    return total_frame_number

def get_fps_from_video(video_path):
    capture = cv2.VideoCapture(video_path)
    video_fps = capture.get(cv2.CAP_PROP_FPS)
    capture.release()
    return video_fps

def get_frame_size_from_video(video_path):
    capture = cv2.VideoCapture(video_path)
    frame_size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)), int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    capture.release()
    return frame_size

def get_video_format_from_video(video_path):
    capture = cv2.VideoCapture(video_path)
    video_format = capture.get(cv2.CAP_PROP_FORMAT)
    capture.release()
    return video_format

def calculate_background(video_path, method = 'brightest', save_path = None, save_background = False, chunk_size = [100, 100], frames_to_skip = 1):

    '''
    Function that calculates the background of a video.

    Steps:
        A path to the video is provided.
        OpenCV is used to open the video.
        The first frame is read into memory.
        The first frame is copied as the background.
        Each frame is subsequently iterated through and compared to the current background.
        Pixels in the frame that are either brighter (default) or darker than the background are used to update the existing background.
        The final output is an array of background images that are equally spaced throughout the video.

    Required Arguments:
        video_path (str) - Path to the video.

    Optional Arguments:
        method (str) - Method to use for calculating background. Different types of methods include brightest, darkest and mode. Default = brightest.
        save_background (bool) - Saves the background(s) seperately into external TIFF files. Default = False.
            ** Location of images can be found in path to video.
            ** Name of file will be {name of video}_background.tif
        chunk_size (list(int, int)) - Determines the size of the area of the background to be successively computed if using mode as the method of background calculation. Default = [100, 100].
            ** When calculating the mode, the entire distribution of pixel values across the entire video must be held in memory.
            ** Thus, to preserve memory resources, patches of the background are computed sequentially until the entire background image has been calculated.
            ** Smaller chunk sizes take longer to process but decrease the number of values held in memory at a time.
            ** Larger chunk sizes make processing faster but require more values to be held in memory.
        frames_to_skip (int) - Determines the number of frames to skip when calculating background. Default = 1.
            ** When default is 1, every frame is used when calculating background.
            ** Larger values speed up the background calculation but may provide a less accurate representation of the background.

    Returns:
        background (frame width, frame height) - Calculated background image.
    '''

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

    t0 = time.time()

    try:
        # Load the video.
        capture = cv2.VideoCapture(video_path)
        # Retrieve total number of frames in video.
        video_total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if method == 'mode':
            frame_size = (int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)))
            background = np.zeros(frame_size)
            pix = []
            height_iterations = int(frame_size[1]/chunk_size[1])
            if frame_size[1] % chunk_size[1] != 0:
                height_iterations += 1
            width_iterations = int(frame_size[0] / chunk_size[0])
            if frame_size[0] % chunk_size[0] != 0:
                width_iterations += 1
            for i in range(height_iterations):
                for j in range(width_iterations):
                    print('Calculating background. Processing chunk number: {0}/{1}.'.format((j + 1) + (width_iterations * i), width_iterations * height_iterations), end = '\r')
                    for frame_num in range(video_total_frames):
                        if frame_num % frames_to_skip == 0:
                            success, frame = capture.read()
                            if success:
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
                    background[i * chunk_size[1] : i * chunk_size[1] + chunk_size[1], j * chunk_size[0] : j * chunk_size[0] + chunk_size[0]] = bg_pix
                    pix = []
                    capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            background = background.astype(np.uint8)
            print('Calculating background complete. Processing chunk number: {0}/{1}.'.format((j + 1) + (width_iterations * i), width_iterations * height_iterations))
            if save_background:
                if save_path != None:
                    background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                else:
                    background_path = '{0}_background.tif'.format(video_path[:-4])
                cv2.imwrite(background_path, background)
        else:
            # Iterate through each frame in the video.
            for frame_num in range(video_total_frames):
                print('Calculating background. Processing frame number: {0}/{1}.'.format(frame_num + 1, video_total_frames), end = '\r')
                if frame_num % frames_to_skip == 0:
                    # Load frame into memory.
                    success, frame = capture.read()
                    # Check if frame was loaded successfully.
                    if success:
                        # Convert frame to grayscale.
                        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        # Copy frame into background if this is the first frame.
                        if frame_num == 0:
                            background = frame.copy().astype(np.float32)
                        if method == 'brightest':
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
            print('Calculating background complete. Processing frame number: {0}/{1}.'.format(frame_num + 1, video_total_frames))
            # Save the background into an external file if requested.
            if save_background:
                if save_path != None:
                    background_path = '{0}\\{1}_background.tif'.format(save_path, os.path.basename(video_path)[:-4])
                else:
                    background_path = '{0}_background.tif'.format(video_path[:-4])
                cv2.imwrite(background_path, background)
    except:
        # Errors that may occur during the background calculation are handled.
        print('')
        if capture.isOpened():
            capture.release()
        return None
    if capture.isOpened():
        # Unload video from memory.
        capture.release()
    print('Total processing time: {0} seconds.'.format(time.time() - t0))
    # Return the calculated background.
    return background

def calculate_next_coords(init_coords, radius, frame, angle = 0, n_angles = 20, range_angles = np.pi * 2.0 / 3.0, tail_calculation = True):
    '''
    Function that calculates the next set of coordinates provided an initial set of coordinates, radius, and frame.

    Steps:
        Calculates a list of angles provided by the number of angles (n_angles) and range of angles (range_angles).
        Calculates a list of all potential coordinates in the image that lie on the circumference of a circle or arc given by the list of angles, the radius, and the initial coordinates.
        Removes unnecessary duplicated coordinates from the list.
        Computes the brightest coordinates out of the list of potential coordinates.
        Check if more than one set of coordinates had the same, brightest values.
        When the tail is being calculated, use the coordinate that is most stimilar to the previous angle.
        When the tail is not being calculated, use the first set of coordinates that have the minimum distance between the next coordinates and the initial coordinates.

    Required Arguments:
        angle (float) - Initial angle that will be used when drawing a line between the inital coordinates and the next coordinates.
            ** Units in radians.
        init_coords (y, x) - Coordinates to use for initializing search of next coordinates.
        radius (float) - Radius to use for calculating the distance between the initial coordinates and potential next coordinates.
        frame (frame width, frame height) - Video frame to search for coordinates.
            ** Expects a background subtracted frame where objects are brighter than the background.

    Optional Arguments:
        tail_calculation (bool) - Determines which method to use if multiple coordinates are returned. Default = True.
            ** When calculating the tail, compute the angle between each potential next coordinate and the initial coordinate, and take the next coordinates whose angle is closest to the initial search angle.
            ** When not calculating the tail, compute the length between each potential next coordinate and the initial coordinate and take the first set of coordinates whose length is the shortest.
        n_angles (int) - Number of angles used when searching for initial points. Default = 20.
        range_angles (float) - The entire range of angles with which to look for the next pixel. Default = 2 / 3 * pi.
            ** Units in radians.

    Returns:
        next_coords (y, x) - The next coordinates in the frame.
    '''
    # Calculate list of angles.
    angles = np.linspace(angle - range_angles / 2, angle + range_angles / 2, n_angles)
    # Calculate list of all potential next coordinates.
    next_coords = [[int(round(init_coords[0] + (radius * np.sin(angles[i])))), int(round(init_coords[1] + (radius * np.cos(angles[i]))))] for i in range(len(angles))]
    # Remove duplicate coordinates.
    next_coords = [next_coords[i] for i in range(len(next_coords)) if next_coords[i][0] != next_coords[i - 1][0] or next_coords[i][1] != next_coords[i - 1][1]]
    # Get the list of coordinates where the potential next coordinates are the brightest pixels in the frame.
    coords = np.transpose(np.where(frame == np.max([frame[i[0]][i[1]] for i in next_coords])))
    # Get only the coordinates that were in the original list.
    next_coords = [[coords[j] for i in range(len(next_coords)) if coords[j][0] == next_coords[i][0] and coords[j][1] == next_coords[i][1]] for j in range(len(coords))]
    # Convert the coordinates to lists.
    next_coords = [next_coords[i][0].tolist() for i in range(len(next_coords)) if len(next_coords[i]) > 0]
    # Checks if more than one set of coordinates was found. This can occur if there are multiple pixels with the same (maximum) value.
    if len(next_coords) > 1:
        # Method to use for finding the next point if it is searching along the tail. For tail calculation, if multiple points are returned, then take the point whose angle is most similar to the previous angle.
        if tail_calculation:
            # Calculate the minimum difference between the angle of the next coordinates and the initial coordinates and the previous angle that was given.
            min_value = np.min([abs(angle - np.arctan2(next_coords[i][0] - init_coords[0], next_coords[i][1] - init_coords[1])) for i in range(len(next_coords))])
            # Take the set of coordinates whose angle matches the minimum difference.
            next_coords = [next_coords[i] for i in range(len(next_coords)) if abs(angle - np.arctan2(next_coords[i][0] - init_coords[0], next_coords[i][1] - init_coords[1])) == min_value]
        else:
            # Calculate the minimum length between the next coordinates and the initial coordinates.
            min_value = np.min([np.hypot(next_coords[i][0] - init_coords[0], next_coords[i][1] - init_coords[1]) for i in range(len(next_coords))])
            # Take the set of coordinates whose length between the next coordinates and previous coordinates matches the minimum length.
            next_coords = [next_coords[i] for i in range(len(next_coords)) if np.hypot(next_coords[i][0] - init_coords[0], next_coords[i][1] - init_coords[1]) == min_value]
    # Return the first set of coordinates.
    return np.array(next_coords[0])

def save_background_to_file(background, background_path):
    cv2.imwrite(background_path, background.astype(np.uint8))

def subtract_background_from_frame(frame, background):
    background_subtracted_frame = cv2.absdiff(frame, background)
    return background_subtracted_frame

def annotate_tracking_results_onto_frame(frame, results, colours, line_length, extended_eyes_calculation, eyes_line_length):

    first_eye_coords, second_eye_coords, first_eye_angle, second_eye_angle, heading_coords, body_coords, heading_angle, tail_point_coords = results
    annotated_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB).astype(np.uint8)
    # Check whether to to an additional process to calculate eye angles.
    if extended_eyes_calculation:
        # Draw a circle arround the first eye coordinates.
        annotated_frame = cv2.circle(annotated_frame, (int(round(first_eye_coords[1])), int(round(first_eye_coords[0]))), 1, colours[-2], -1)
        if not np.isnan(first_eye_angle):
            # Draw a line representing the first eye angle.
            annotated_frame = cv2.line(annotated_frame, (int(round(first_eye_coords[1])), int(round(first_eye_coords[0]))), (int(round(first_eye_coords[1] + (eyes_line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (eyes_line_length * np.sin(first_eye_angle))))), colours[-2], 1)
        # Draw a circle around the second eye coordinates.
        annotated_frame = cv2.circle(annotated_frame, (int(round(second_eye_coords[1])), int(round(second_eye_coords[0]))), 1, colours[-3], - 1)
        if not np.isnan(second_eye_angle):
            # Draw a line representing the second eye angle.
            annotated_frame = cv2.line(annotated_frame, (int(round(second_eye_coords[1])), int(round(second_eye_coords[0]))), (int(round(second_eye_coords[1] + (eyes_line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (eyes_line_length * np.sin(second_eye_angle))))), colours[-3], 1)
    else:
        # Draw a circle arround the first eye coordinates.
        annotated_frame = cv2.circle(annotated_frame, (int(round(first_eye_coords[1])), int(round(first_eye_coords[0]))), 1, colours[-2], -1)
        # Draw a circle arround the second eye coordinates.
        annotated_frame = cv2.circle(annotated_frame, (int(round(second_eye_coords[1])), int(round(second_eye_coords[0]))), 1, colours[-3], - 1)
    for i in range(1, len(tail_point_coords)):
        annotated_frame = cv2.circle(annotated_frame, (int(round((tail_point_coords[i - 1][1] + tail_point_coords[i][1]) / 2)), int(round((tail_point_coords[i - 1][0] + tail_point_coords[i][0]) / 2))), 1, colours[i - 1], -1)
    annotated_frame = cv2.arrowedLine(annotated_frame, (int(round(heading_coords[1] - (line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
    return annotated_frame

def apply_median_blur_to_frame(frame, value = 3):
    median_blur_frame = cv2.medianBlur(frame, value)
    return median_blur_frame

def apply_threshold_to_frame(frame, value = 100):
    threshold_frame = cv2.threshold(frame, value, 255, cv2.THRESH_BINARY)[1].astype(np.uint8)
    return threshold_frame

def load_background_into_memory(background_path, convert_to_grayscale = True):

    if convert_to_grayscale:
        background = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE).astype(np.uint8)
    else:
        background = cv2.imread(background_path).astype(np.uint8)

    return background

def load_frame_into_memory(video_path, frame_number = 0, convert_to_grayscale = True):

    video_n_frames = get_total_frame_number_from_video(video_path)

    if frame_number > video_n_frames:
        frame_number = video_n_frames

    capture = cv2.VideoCapture(video_path)

    # Set the frame number to load.
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    success, original_frame = capture.read()
    frame = None
    if success:
        if convert_to_grayscale:
            frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8).copy()
        else:
            frame = original_frame.astype(np.uint8).copy()

    return success, frame

def subtract_background_from_frames(frame_array, background):
    frame_array = [[success, cv2.absdiff(frame, background)] if success else [success, frame] for success, frame in frame_array]
    return frame_array

def apply_median_blur_to_frames(frame_array):
    frame_array = [[success, cv2.medianBlur(frame, 3)] if success else [success, frame] for success, frame in frame_array]
    return frame_array

def load_frames_into_memory(video_path, starting_frame = 0, frame_batch_size = 50, convert_to_grayscale = True):

    # Open the video path.
    capture = cv2.VideoCapture(video_path)

    # Get the total number of frames in the video.
    video_n_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    # Set the frame position to start.
    capture.set(cv2.CAP_PROP_POS_FRAMES, starting_frame)

    frame_array = []
    # Load frames into memory.
    for i in range(frame_batch_size):
        success, original_frame = capture.read()
        frame = original_frame.astype(np.uint8).copy()
        if success and convert_to_grayscale:
            frame = cv2.cvtColor(original_frame, cv2.COLOR_BGR2GRAY).astype(np.uint8)
        frame_array.append([success, frame])

    capture.release()

    return frame_array

def preview_tracking_results(video_path, colours, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, save_path = None, background_path = None, save_background = False, extended_eyes_calculation = False, eyes_threshold = None, line_length = 0, frame_number = 0, pixel_threshold = 100):
    '''
    Previews tracking for a video.

    Required Arguments:
        video_path (str) - Path to the video.
        colours (list([B, G, R])) - List of colours that will be used for annotating tracking results onto video.
            ** Each colour is a list consisting of blue, green, and red.
            ** Values go from 0 - 255.
            ** The length of the list of colours must be greater than the number of tail points + heading angle + eyes. The heading angle counts as 1. For extended eyes calculation, eyes count as 2, otherwise count as 1.
        n_tail_points (int) - Number of points to track along the tail.
        dist_tail_points (int) - The distance between successive tail points, measured in number of pixels.
        dist_eyes (int) - The distance between the two eyes, measured in number of pixels.
        dist_swim_bladder (int) - The distance between the eyes and the swim bladder, measured in number of pixels.

    Optional Arguments:
        save_path (str) - Path to save the tracked video and data. Default = None.
            ** When save_path is None, the save_path becomes the video_path.
        background_path (str) - Path to the background. Default = None.
        save_background (bool) - Boolean to determine whether or not to save the background into an external TIFF file. Default = False.
            ** Only use if background_path has not been provided.
        extended_eyes_calculation (bool) - Boolean to determine whether or not the extended eyes calculation method should be used. Default = False.
        eyes_threshold (int) - Threshold that is used for finding the binary regions that contain the eye coordinates. Default = None.
            ** Only use if extended_eyes_calculation is set to True, otherwise set to None.
        line_length (int) - The length of the line used for drawing the heading angle and eye angles. Default = 0.
            ** When line_length is 0, line_length = dist_eyes.
        frame_number (int) - Frame number for which to preview the tracking results. Default = 0.
        video_fps (float) - FPS of the tracked video. Default = None.
            ** When video_fps is None, video_fps = fps of video.
        video_n_frames (int) - Number of frames to track. Default = None.
            ** When video_n_frames is None, video_n_frames = total number of frames in video.
        pixel_threshold (int) - Threshold used to determine whether to track the frame. Default = 100.
            ** Used to compare the pixel_threshold to the maximum pixel value in the frame.
            ** If the maximum pixel value in the frame is less than pixel_threshold, then skip tracking that frame.
            ** Useful for when the fish is out of the frame. Thus, frames in which the fish is not in it will not be tracked.

    Returns:
        preview_tracking_results - A window will display the tracking results annotated on the video frame requested.
            ** Points of interest (i.e. tail points, heading angle, and eye coordinates) are annotated on the frame.
    '''
    # Create or load background image.
    if background_path is None:
        background = calculate_background(video_path, save_path = save_path, save_background = save_background)[0].astype(np.uint8)
    else:
        background = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE).astype(np.uint8)

    if line_length == 0:
        line_length = dist_eyes

    if not extended_eyes_calculation and eyes_threshold is not None:
        eyes_threshold = None

    if save_path == None:
        save_path = os.path.dirname(video_path)

    # Open the video path.
    capture = cv2.VideoCapture(video_path)

    # Get the total number of frames in the video.
    video_n_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_number >= video_n_frames:
        print('Frame number provided exceeds the total number of frames in the video. Setting the frame number to 0.')
        frame_number = 0

    # Set the frame position to start.
    capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    print('Calculating tracking results.')
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
        frame = cv2.medianBlur(frame, 3)
        try:
            # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
            if np.max(frame) > pixel_threshold:
                # Return the coordinate of the brightest pixel.
                first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                second_eye_coords = calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                # Check whether to to an additional process to calculate eye angles.
                if extended_eyes_calculation:
                    # Calculate the angle between the two eyes.
                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                    # Apply a threshold to the frame.
                    thresh = cv2.threshold(frame, eyes_threshold, 255, cv2.THRESH_BINARY)[1]
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
                swim_bladder_coords = calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
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
                        tail_point_coords[m] = calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle)
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
                        tail_point_coords[m] = calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle)
            # Check whether to to an additional process to calculate eye angles.
            if extended_eyes_calculation:
                # Draw a circle arround the first eye coordinates.
                original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-3], -1)
                # Draw a line representing the first eye angle.
                original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                # Draw a circle around the second eye coordinates.
                original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                # Draw a line representing the second eye angle.
                original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (line_length * np.sin(second_eye_angle))))), colours[-2], 1)
            else:
                # Draw a circle arround the first eye coordinates.
                original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-2], -1)
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
            original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
            print('Previewing tracking results.')
            cv2.imshow('Preview Tracked Frame', original_frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except:
            # Handles any errors that occur throughout tracking.
            print('Error: something went wrong during tracking!')

    # Unload the video from memory.
    capture.release()

def track_tail_in_frame(tracking_params):

    frame, success, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, pixel_threshold, extended_eyes_calculation, eyes_threshold = tracking_params
    first_eye_coords = [np.nan, np.nan]
    second_eye_coords = [np.nan, np.nan]
    first_eye_angle = np.nan
    second_eye_angle = np.nan
    heading_coords = [np.nan, np.nan]
    body_coords = [np.nan, np.nan]
    heading_angle = np.nan
    tail_point_coords = [[np.nan, np.nan] for m in range(n_tail_points + 1)]
    try:
        if success:
            if np.max(frame) > pixel_threshold:
                # Return the coordinate of the brightest pixel.
                first_eye_coords = [np.where(frame == np.max(frame))[0][0], np.where(frame == np.max(frame))[1][0]]
                # Calculate the next brightest pixel that lies on the circle drawn around the first eye coordinates and has a radius equal to the distance between the eyes.
                second_eye_coords = calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
                if extended_eyes_calculation:
                    # Calculate the angle between the two eyes.
                    eye_angle = np.arctan2(second_eye_coords[0] - first_eye_coords[0], second_eye_coords[1] - first_eye_coords[1])
                    # Apply a threshold to the frame.
                    thresh = cv2.threshold(frame, eyes_threshold, 255, cv2.THRESH_BINARY)[1]
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
                tail_point_coords[0] = calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
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
                    # Calculate the next set of tail coordinates.
                    tail_point_coords[m] = calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle)
                tracking_results = np.array([np.array(first_eye_coords), np.array(second_eye_coords), first_eye_angle, second_eye_angle, np.array(heading_coords), np.array(body_coords), heading_angle, np.array(tail_point_coords)])
                # if not np.isnan(np.hstack(tracking_results).any()):
                return tracking_results
                # else:
                    # return None
            else:
                return None
        else:
            return None
    except:
        return None

def track_tail_in_video_with_multiprocessing(video_path, colours, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, init_frame_batch_size = 50, init_starting_frame = 0, save_path = None, background_path = None, save_background = False, line_length = 0, video_fps = None, n_frames = None, pixel_threshold = 100, frame_change_threshold = 10):

    t0 = time.time()

    # Create or load background image.
    if background_path is None:
        background = calculate_background(video_path, save_path, save_background = save_background)[0].astype(np.uint8)
    else:
        background = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE).astype(np.uint8)

    video_n_frames = get_total_frame_number_from_video(video_path)
    starting_frame = init_starting_frame
    frame_batch_size = init_frame_batch_size

    # Get the total number of frames.
    if n_frames is None:
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

    batch_iterations = int((video_n_frames - starting_frame) / frame_batch_size)
    if (video_n_frames - starting_frame) % frame_batch_size != 0:
        batch_iterations += 1

    # Initialize variables for data.
    eye_coord_array = np.array([])
    heading_coord_array = np.array([])
    body_coord_array = np.array([])
    heading_angle_array = np.array([])
    tail_coord_array = np.array([])

    for i in range(batch_iterations):
        print('Tracking video. Processing frame numbers: {0} - {1} / {2}.'.format(starting_frame, starting_frame + frame_batch_size, video_n_frames), end = '\r')
        frame_array = load_frames_into_memory(video_path, starting_frame = starting_frame, frame_batch_size = frame_batch_size)
        frame_array = subtract_background_from_frames(frame_array, background)
        frame_array = apply_median_blur_to_frames(frame_array)
        tracking_params = [[frame, success, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, pixel_threshold] for success, frame in frame_array]
        pool = mp.Pool(mp.cpu_count())
        tracking_results = np.array(pool.map(track_tail_in_frame, tracking_params))
        pool.close()
        pool.join()

        eye_coord_array = np.append(eye_coord_array, np.array([tracking_results[:,0], tracking_results[:,1]]))
        heading_coord_array = np.append(heading_coord_array, tracking_results[:,2])
        body_coord_array = np.append(body_coord_array, tracking_results[:,3])
        heading_angle_array = np.append(heading_angle_array, tracking_results[:,4])
        tail_coord_array = np.append(tail_coord_array, tracking_results[:,5])

        if starting_frame + frame_batch_size != video_n_frames:
            starting_frame += frame_batch_size
            if starting_frame + frame_batch_size > video_n_frames:
                frame_batch_size = video_n_frames - starting_frame

    print('Tracking video. Processing frame numbers: {0} - {1} / {2}.'.format(starting_frame, starting_frame + frame_batch_size, video_n_frames))

    eye_coord_array = eye_coord_array.reshape((2, video_n_frames))
    starting_frame = init_starting_frame
    frame_batch_size = init_frame_batch_size

    results =   {   'eye_coord_array' : eye_coord_array,
                    'heading_coord_array' : heading_coord_array,
                    'tail_coord_array' : tail_coord_array,
                    'body_coord_array' : body_coord_array,
                    'heading_angle_array' : heading_angle_array,
                    'video_path' : video_path,
                    'video_n_frames' : video_n_frames,
                    'video_fps' : video_fps,
                    'dist_tail_points' : dist_tail_points,
                    'dist_eyes' : dist_eyes,
                    'dist_swim_bladder' : dist_swim_bladder,
                    'pixel_threshold' : pixel_threshold,
                    'frame_change_threshold' : frame_change_threshold
                }

    print('Total processing time: {0} seconds.'.format(time.time() - t0))

    return results

def track_tail_in_video_without_multiprocessing(video_path, colours, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, init_frame_batch_size = 50, init_starting_frame = 0, save_path = None, background_path = None, save_background = False, line_length = 0, video_fps = None, n_frames = None, pixel_threshold = 100, frame_change_threshold = 10):

    t0 = time.time()

    # Create or load background image.
    if background_path is None:
        background = calculate_background(video_path, save_path, save_background = save_background)[0].astype(np.uint8)
    else:
        background = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE).astype(np.uint8)

    video_n_frames = get_total_frame_number_from_video(video_path)
    starting_frame = init_starting_frame
    frame_batch_size = init_frame_batch_size

    # Get the total number of frames.
    if n_frames is None:
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

    batch_iterations = int((video_n_frames - starting_frame) / frame_batch_size)
    if (video_n_frames - starting_frame) % frame_batch_size != 0:
        batch_iterations += 1

    # Initialize variables for data.
    eye_coord_array = np.array([])
    heading_coord_array = np.array([])
    body_coord_array = np.array([])
    heading_angle_array = np.array([])
    tail_coord_array = np.array([])

    for i in range(batch_iterations):
        print('Tracking video. Processing frame numbers: {0} - {1} / {2}.'.format(starting_frame, starting_frame + frame_batch_size, video_n_frames), end = '\r')
        frame_array = load_frames_into_memory(video_path, starting_frame = starting_frame, frame_batch_size = frame_batch_size)
        frame_array = subtract_background_from_frames(frame_array, background)
        frame_array = apply_median_blur_to_frames(frame_array)
        tracking_params = [[frame, success, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, pixel_threshold] for success, frame in frame_array]
        tracking_results = np.array([track_tail_in_frame(i) for i in tracking_params])

        eye_coord_array = np.append(eye_coord_array, np.array([tracking_results[:,0], tracking_results[:,1]]))
        heading_coord_array = np.append(heading_coord_array, tracking_results[:,2])
        body_coord_array = np.append(body_coord_array, tracking_results[:,3])
        heading_angle_array = np.append(heading_angle_array, tracking_results[:,4])
        tail_coord_array = np.append(tail_coord_array, tracking_results[:,5])

        if starting_frame + frame_batch_size != video_n_frames:
            starting_frame += frame_batch_size
            if starting_frame + frame_batch_size > video_n_frames:
                frame_batch_size = video_n_frames - starting_frame

    print('Tracking video. Processing frame numbers: {0} - {1} / {2}.'.format(starting_frame, starting_frame + frame_batch_size, video_n_frames))

    eye_coord_array = eye_coord_array.reshape((2, video_n_frames))
    starting_frame = init_starting_frame
    frame_batch_size = init_frame_batch_size

    results =   {   'eye_coord_array' : eye_coord_array,
                    'heading_coord_array' : heading_coord_array,
                    'tail_coord_array' : tail_coord_array,
                    'body_coord_array' : body_coord_array,
                    'heading_angle_array' : heading_angle_array,
                    'video_path' : video_path,
                    'video_n_frames' : video_n_frames,
                    'video_fps' : video_fps,
                    'dist_tail_points' : dist_tail_points,
                    'dist_eyes' : dist_eyes,
                    'dist_swim_bladder' : dist_swim_bladder,
                    'pixel_threshold' : pixel_threshold,
                    'frame_change_threshold' : frame_change_threshold
                }

    print('Total processing time: {0} seconds.'.format(time.time() - t0))

    return results

def track_video(video_path, colours, n_tail_points, dist_tail_points, dist_eyes, dist_swim_bladder, save_video = True, n_frames = None, starting_frame = 0, save_path = None, background_path = None, save_background = True, extended_eyes_calculation = False,  eyes_threshold = None, line_length = 0, video_fps = None, pixel_threshold = 100, frame_change_threshold = 10):
    '''
    Tracks a video.

    Required Arguments:
        video_path (str) - Path to the video.
        colours (list([B, G, R])) - List of colours that will be used for annotating tracking results onto video.
            ** Each colour is a list consisting of blue, green, and red.
            ** Values go from 0 - 255.
            ** The length of the list of colours must be greater than the number of tail points + heading angle + eyes. The heading angle counts as 1. For extended eyes calculation, eyes count as 2, otherwise count as 1.
        n_tail_points (int) - Number of points to track along the tail.
        dist_tail_points (int) - The distance between successive tail points, measured in number of pixels.
        dist_eyes (int) - The distance between the two eyes, measured in number of pixels.
        dist_swim_bladder (int) - The distance between the eyes and the swim bladder, measured in number of pixels.

    Optional Arguments:
        save_path (str) - Path to save the tracked video and data. Default = None.
            ** When save_path is None, the save_path becomes the video_path.
        background_path (str) - Path to the background. Default = None.
        save_background (bool) - Boolean to determine whether or not to save the background into an external TIFF file. Default = True.
            ** Only use if background_path has not been provided.
        extended_eyes_calculation (bool) - Boolean to determine whether or not the extended eyes calculation method should be used. Default = False.
        eyes_threshold (int) - Threshold that is used for finding the binary regions that contain the eye coordinates. Default = None.
            ** Only use if extended_eyes_calculation is set to True, otherwise set to None.
        line_length (int) - The length of the line used for drawing the heading angle and eye angles. Default = 0.
            ** When line_length is 0, line_length = dist_eyes.
        starting_frame (int) - Frame number for which to start in the video. Default = 0.
        video_fps (float) - FPS of the tracked video. Default = None.
            ** When video_fps is None, video_fps = fps of video.
        video_n_frames (int) - Number of frames to track. Default = None.
            ** When video_n_frames is None, video_n_frames = total number of frames in video.
        pixel_threshold (int) - Threshold used to determine whether to track the frame. Default = 100.
            ** Used to compare the pixel_threshold to the maximum pixel value in the frame.
            ** If the maximum pixel value in the frame is less than pixel_threshold, then skip tracking that frame.
            ** Useful for when the fish is out of the frame. Thus, frames in which the fish is not in it will not be tracked.
        frame_change_threshold (int) - Threshold used to compare the absolute difference in pixel values from frame to frame. Default = 10.
            ** Used to determined whether or not the previous data points should be used or whether new points should be calculated.
            ** The larger the frame_change_threshold, the less likely it is that new data points are going to be calculated.
            ** Useful for reducing frame to frame noise in position of coordinates.

    Returns:
        tracked_video - Saved in the path location given by the video path.
            ** Saved in a raw video format.
            ** Points of interest (i.e. tail points, heading angle, and eye coordinates) are annotated on the video.
        data_file - Saved in the path location given by the video path.
            ** Saved as a npz file.
            ** Saved as a dictionary containing arrays of the eye coordinates, heading angle, eye angles, and tail points.
    '''

    t0 = time.time()

    if line_length == 0:
        line_length = dist_eyes

    if not extended_eyes_calculation and eyes_threshold is not None:
        eyes_threshold = None

    if save_path == None:
        save_path = os.path.dirname(video_path)

    # Create or load background image.
    if background_path is None:
        background = calculate_background(video_path, save_path = save_path, save_background = save_background)
    else:
        background = cv2.imread(background_path, cv2.IMREAD_GRAYSCALE).astype(np.uint8)

    video_n_frames = get_total_frame_number_from_video(video_path)
    frame_size = get_frame_size_from_video(video_path)

    # Get the fps.
    if video_fps is None:
        video_fps = get_fps_from_video(video_path)

    # Get the total number of frames.
    if n_frames is None:
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

    # Iterate through each frame.
    for n in range(n_frames):
        print('Tracking video. Processing frame number: {0} / {1}.'.format(n + 1, n_frames), end = '\r')
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
            frame = cv2.medianBlur(frame, 3)
            try:
                # Check to ensure that the maximum pixel value is greater than a certain value. Useful for determining whether or not the at least one of the eyes is present in the frame.
                if np.max(frame) > pixel_threshold:
                    # Check to see if it's not the first frame and check if the sum of the absolute difference between the current frame and the previous frame is greater than a certain threshold. This helps reduce frame to frame noise in the position of the pixels.
                    if prev_frame is not None and np.sum(np.abs(frame.astype(float) - prev_frame.astype(float)) > frame_change_threshold) == 0:
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
                        second_eye_coords = calculate_next_coords(first_eye_coords, dist_eyes, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
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
                            thresh = cv2.threshold(frame, eyes_threshold, 255, cv2.THRESH_BINARY)[1]
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
                        swim_bladder_coords = calculate_next_coords(heading_coords, dist_swim_bladder, frame, n_angles = 100, range_angles = 2 * np.pi, tail_calculation = False)
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
                                tail_point_coords[m] = calculate_next_coords(swim_bladder_coords, dist_tail_points, frame, angle = tail_angle)
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
                                tail_point_coords[m] = calculate_next_coords(tail_point_coords[m - 1], dist_tail_points, frame, angle = tail_angle)
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
                            original_frame = cv2.line(original_frame, (first_eye_coords[1], first_eye_coords[0]), (int(round(first_eye_coords[1] + (line_length * np.cos(first_eye_angle)))), int(round(first_eye_coords[0] + (line_length * np.sin(first_eye_angle))))), colours[-3], 1)
                            # Draw a circle around the second eye coordinates.
                            original_frame = cv2.circle(original_frame, (second_eye_coords[1], second_eye_coords[0]), 1, colours[-2], - 1)
                            # Draw a line representing the second eye angle.
                            original_frame = cv2.line(original_frame, (second_eye_coords[1], second_eye_coords[0]), (int(round(second_eye_coords[1] + (line_length * np.cos(second_eye_angle)))), int(round(second_eye_coords[0] + (line_length * np.sin(second_eye_angle))))), colours[-2], 1)
                        else:
                            # Draw a circle arround the first eye coordinates.
                            original_frame = cv2.circle(original_frame, (first_eye_coords[1], first_eye_coords[0]), 1, colours[-2], -1)
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
                        original_frame = cv2.arrowedLine(original_frame, (int(round(heading_coords[1] - (line_length / 2 * np.cos(heading_angle)))), int(round(heading_coords[0] - (line_length / 2 * np.sin(heading_angle))))), (int(round(heading_coords[1] + (line_length * np.cos(heading_angle)))), int(round(heading_coords[0] + (line_length * np.sin(heading_angle))))), colours[-1], 1, tipLength = 0.2)
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

    print('Tracking video. Processing frame number: {0} / {1}.'.format(n + 1, n_frames))
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

    print('Total processing time: {0} seconds.'.format(time.time() - t0))
