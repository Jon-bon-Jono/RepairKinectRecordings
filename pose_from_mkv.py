import time
import traceback 

import cv2
import ctypes
from pykinect_azure.k4a import _k4a
from pykinect_azure.k4a.image import Image
import pykinect_azure as pykinect

#addapted from examplePlaybackBodyTracker.py

#run `k4arecorder.exe -l 10 C:\Users\GSBME\Videos\output.mkv` to get an uncorrupted mkv recording

#run `k4abt_simple_3d_viewer.exe OFFLINE output.mkv` to perform the 3D pose estimation or run this Python script

#not sure if the initial mkv files were corrupted due to not ending the recording properly or due to frames being lost or both


if __name__ == "__main__":

	#video_filename = "C:\\Users\\GSBME\\Videos\\output.mkv"
	video_filename = "C:\\Users\\z5162987\\OneDrive - UNSW\\fall_detection\\backup_data\\kinect_tests\\clean_recordings\\output.mkv"

	# Initialize the library, if the library is not found, add the library path as argument
	pykinect.initialize_libraries(track_body=True)
	print("Pykinect initialized")
	# Start playback
	playback = pykinect.start_playback(video_filename)

	playback_config = playback.get_record_configuration()
	# print(playback_config)

	playback_calibration = playback.get_calibration()

	# Start body tracker
	bodyTracker = pykinect.start_body_tracker(calibration=playback_calibration)
	print("Body tracker started")
	while True:

		# Get camera capture
		capture = playback.update()

		if not capture:
			break

		# Get body tracker frame
		try:
			body_frame = bodyTracker.update(capture=capture) 
		except:
			#traceback.print_exc() 
			continue

		body_num = body_frame.get_num_bodies()

		for b in range(body_num): #iterate through detected poses
			joints = body_frame.get_body(b).joints
			for joint in joints:
				print(f"({joint.position.x},{joint.position.y},{joint.position.z})")
			print("\n\n")