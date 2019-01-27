import face_recognition
import cv2
import os
from multiprocessing import Queue, Value

known_face_encodings = []
# Load a sample picture and learn how to recognize it.
for file in os.listdir('dataset'):
	image = face_recognition.load_image_file("dataset/{}".format(file))
	encoding = face_recognition.face_encodings(image)[0]
	known_face_encodings.append(encoding)

# Initialize some variables
face_locations = []
face_encodings = []


def present(frame):
	global face_locations, face_encodings

	# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
	rgb_frame = frame[:, :, ::-1]

	# Find all the faces and face encodings in the current frame of video
	face_locations = face_recognition.face_locations(rgb_frame)
	face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

	for face_encoding in face_encodings:
		# See if the face is a match for the known face(s)
		matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

		# If a match was found in known_face_encodings, just use the first one.
		if True in matches:
			return True
	return False


def recognition_loop(frame_queue: Queue, is_present: Value, stop_all: Value):
	while True:
		frame = frame_queue.get()
		is_present.value = present(frame)
