import face_recognition
import cv2
import os


# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)

known_face_encodings = []
# Load a sample picture and learn how to recognize it.
for file in os.listdir('dataset'):
	image = face_recognition.load_image_file(f"dataset/{file}")
	encoding = face_recognition.face_encodings(image)[0]
	known_face_encodings.append(encoding)

# Initialize some variables
face_locations = []
face_encodings = []


def present(small_frame):
	global face_locations, face_encodings

	# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	rgb_small_frame = small_frame[:, :, ::-1]

	# Find all the faces and face encodings in the current frame of video
	face_locations = face_recognition.face_locations(rgb_small_frame)
	face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

	for face_encoding in face_encodings:
		# See if the face is a match for the known face(s)
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

		# If a match was found in known_face_encodings, just use the first one.
		if True in matches:
			return True
	return False
