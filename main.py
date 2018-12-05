import cv2
from recognition import present
from multiprocessing import Process, Value, Queue
from motion_detection import motion


def _present(small_frame):
	global isPresent
	isPresent.value = present(small_frame)

def _motion(frame):
	global frameQueue
	frameQueue.put(frame)
	isMoving.value = motion(frameQueue)


if __name__ == "__main__":
	video_capture = cv2.VideoCapture("http://192.168.1.6:5200/stream/video.mjpeg")
	process = 0
	isPresent = Value('i', 0)
	isMoving = Value('i', 0)
	frameQueue = Queue()

	frameQueue.put(video_capture.read()[1])
	frameQueue.put(video_capture.read()[1])

	while True:
		ret, frame = video_capture.read()
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

		if process % 30 == 0:
			p = Process(target=_present, args=[small_frame])
			p.start()

			#p = Process(target=_motion, args=[frame])
			#p.start()
			_motion(frame)

			print("Am I here?", isPresent.value)
			print("Am I moving?", isMoving.value)

		process += 1

		cv2.imshow('Video', frame)

		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	video_capture.release()
	cv2.destroyAllWindows()
