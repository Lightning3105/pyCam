import cv2
from recognition import present
from multiprocessing import Process, Value, Queue
from motion_detection import motion
from datetime import datetime, timedelta
import atexit
import signal
import os
from subprocess import Popen

def _present(small_frame, isPresent):
	isPresent.value = present(small_frame)


def _motion(frame, isMoving, frameQueue):
	frameQueue.put(frame)
	isMoving.value = motion(frameQueue)


def store(isMoving, frame, output, force=False):
	if isMoving.value > 800 or force:
		#cv2.imwrite('storage/{}.jpg'.format(str(datetime.now())), frame)
		output.write(frame)
		return 1
	return 0

def archive():
	DRIVE = '/dev/sda'
	if os.path.exists(DRIVE):
		if 9 <= datetime.now().hour <= 22:
			for file in [f for f in os.listdir('storage') if f != 'video.mp4']:
				os.rename('storage/' + file, '/mnt/storage/' + file)



def save_video(video_out, frame, start, captures, force=False, recreate=True):
	if (datetime.now() - start).seconds >= 60 * 60 * 6 or force:
		video_out.release()
		try:
			os.rename('storage/video.mp4', 'storage/{}_{}_({}).mp4'.format(start.strftime("%Y-%m-%d--%H-%M-%S"), datetime.now().strftime("%Y-%m-%d--%H-%M-%S"), captures))
		except FileNotFoundError:
			print('Video file non-existent')
		archive()
		if recreate:
			height, width, channels = frame.shape
			fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
			video_out = cv2.VideoWriter('storage/video.mp4', fourcc, 15.0, (width, height))
			start = datetime.now()

	return video_out, start


def camera_loop():
	video_capture = cv2.VideoCapture("http://192.168.1.10/stream/video.mjpeg")
	process = 0
	isPresent = Value('i', 0)
	isMoving = Value('i', 0)
	frameQueue = Queue()

	frameQueue.put(video_capture.read()[1])

	height, width, channels = video_capture.read()[1].shape
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Be sure to use lower case
	if not os.path.exists('storage'):
		os.mkdir('storage')
	if os.path.exists('storage/video.mp4'):
		os.rename('storage/video.mp4', 'storage/{}_{}.mp4'.format("UNKNOWN",
		                                                          datetime.now().strftime("%Y-%m-%d--%H-%M-%S")))
	video_out = cv2.VideoWriter('storage/video.mp4', fourcc, 15.0, (width, height))

	processes = []

	stopping = []

	def stop(*_):
		stopping.append(1)

	atexit.register(stop)
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)

	start = datetime.now()
	captures = 0

	while True:
		ret, frame = video_capture.read()
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

		if process % 30 == 0:
			processes.append(Process(target=_present, name="present", args=[small_frame, isPresent]))
			processes[-1].start()

			processes.append(Process(target=_motion, name="motion", args=[frame, isMoving, frameQueue]))
			processes[-1].start()

			print("Am I here?", isPresent.value)
			print("Am I moving?", isMoving.value)

			captures += store(isMoving, frame, video_out)

			video_out, start = save_video(video_out, frame, start, captures)

		process += 1

		if stopping:
			break

	while not frameQueue.empty():
		frameQueue.get()

	for process in processes:
		if process.is_alive():
			process.join()
	video_capture.release()
	save_video(video_out, frame, start, force=True, recreate=False)
	cv2.destroyAllWindows()

if __name__ == "__main__":
	camera_loop()
