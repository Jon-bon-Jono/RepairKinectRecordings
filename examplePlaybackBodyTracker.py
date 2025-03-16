import time

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

	video_filename = "C:\\Users\\GSBME\\Videos\\output.mkv"

	# Initialize the library, if the library is not found, add the library path as argument
	pykinect.initialize_libraries(track_body=True)

	# Start playback
	playback = pykinect.start_playback(video_filename)

	playback_config = playback.get_record_configuration()
	# print(playback_config)

	playback_calibration = playback.get_calibration()

	# Start body tracker
	bodyTracker = pykinect.start_body_tracker(calibration=playback_calibration)

	cv2.namedWindow('Depth image with skeleton',cv2.WINDOW_NORMAL)
	while True:

		# Get camera capture
		capture = playback.update()

		if not capture:
			break

		# Get body tracker frame
		try:
			body_frame = bodyTracker.update(capture=capture)
		except:
			continue

		body_num = body_frame.get_num_bodies()

		for b in range(body_num):
			joints = body_frame.get_body(b).joints
			for joint in joints:
				print(f"({joint.position.x},{joint.position.y},{joint.position.z})")
			print("\n\n")
		continue
		# Get color image
		ret_color, color_image = capture.get_transformed_color_image()

		cv2.imshow('Depth image with skeleton',color_image)
		bgra = cv2.cvtColor(color_image, cv2.COLOR_BGR2BGRA)
		bgra_image_handle = _k4a.k4a_image_t()
		image_format = _k4a.K4A_IMAGE_FORMAT_COLOR_BGRA32
		buffer = bgra.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
		_k4a.VERIFY(_k4a.k4a_image_create_from_buffer(image_format, bgra.shape[1], bgra.shape[0], bgra.shape[1]*4, buffer, bgra.nbytes, ctypes.c_void_p(0), ctypes.c_void_p(0), bgra_image_handle), "MJPG to BGRA32 ERROR")
		bgra_image = Image(bgra_image_handle)

		# Get the colored depth
		ret_depth, depth_color_image = capture.get_colored_depth_image()

		# Get the colored body segmentation
		ret_seg, body_image_color = body_frame.get_segmentation_image()
		
		if not ret_color or not ret_depth or not ret_seg:
			continue
			
		# Combine both images
		combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)
		combined_image = cv2.addWeighted(color_image[:, :, :3], 0.7, combined_image, 0.3, 0)

		# Draw the skeletons
		#combined_image = body_frame.draw_bodies(combined_image)

		# Overlay body segmentation on depth image
		#cv2.imshow('Depth image with skeleton',combined_image)
		time.sleep(0.5)
		# Press q key to stop
		if cv2.waitKey(1) == ord('q'):
			break