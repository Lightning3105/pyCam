import cv2
from recognition import recognition_loop as _recognition_loop
from multiprocessing import Process, Value, Queue
from motion_detection import motion_loop as _motion_loop
from datetime import datetime, timedelta
import atexit
import signal
import os
import shutil


def recognition_loop(stop_all):
	frame_queue = Queue()
	is_present = Value('i', 0)
	p = Process(target=_recognition_loop, args=[frame_queue, is_present, stop_all])
	p.start()
	return frame_queue, is_present, p


def motion_loop(stop_all):
	frame_queue = Queue()
	is_moving = Value('i', 0)
	p = Process(target=_motion_loop, args=[frame_queue, is_moving, stop_all])
	p.start()
	return frame_queue, is_moving, p


def store(is_moving, is_present, frame, force=False):
	if is_moving.value > 800 or force:
		now = datetime.now().strftime("%Y/%m/%d/%H:%M:%S")
		os.makedirs('storage/' + now[:10], exist_ok=True)
		cv2.imwrite('storage/{}-{}-{}.jpg'.format(now, str(is_moving.value).zfill(5), is_present.value), frame,
		            [cv2.IMWRITE_JPEG_QUALITY, 90])
		return 1
	return 0


def archive():
	def _archive():
		DRIVE = 'external'  # '/dev/sda'
		if os.path.exists(DRIVE):
			if 9 <= datetime.now().hour <= 22:
				for dirpath, dirnames, filenames in os.walk('storage', topdown=False):
					for file in filenames:
						os.makedirs(DRIVE + '/camera/' + dirpath.replace('storage', ''), exist_ok=True)
						os.rename(dirpath + '/' + file, DRIVE + '/camera' + dirpath.replace('storage', '') + '/' + file)
					if not os.listdir(dirpath) and dirpath != 'storage':
						os.rmdir(dirpath)

	p = Process(target=_archive)
	p.start()
	return p


def frame_push(frame, rec_frame_queue: Queue, mot_frame_queue: Queue):
	rec_frame_queue.put(frame)
	mot_frame_queue.put(frame)


def camera_loop():
	video_capture = cv2.VideoCapture("http://192.168.1.10/stream/video.mjpeg")
	process = 0

	stop_all = Value('i', 0)

	rec_frame_queue, is_present, rec_p = recognition_loop(stop_all)
	mot_frame_queue, is_moving, mot_p = motion_loop(stop_all)

	height, width, _ = video_capture.read()[1].shape
	# video_out, start = start_writing(width, height)

	stopping = []

	def stop(*_):
		stopping.append(1)

	atexit.register(stop)
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)

	current_frame = None

	archiver = archive()

	while True:
		ret, frame = video_capture.read()

		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

		if process % 30 == 0:
			frame_push(small_frame, rec_frame_queue, mot_frame_queue)

			print("Am I here?", is_present.value)
			print("Am I moving?", is_moving.value)

			if current_frame is not None:
				store(is_moving, is_present, current_frame)

			current_frame = frame

		if process >= 30 * 60 * 60:
			process = 1
			archiver = archive()

		process += 1

		if stopping:
			break

	# while not frameQueue.empty():
	#	frameQueue.get()
	archiver.join()

	"""
	rec_p.terminate()
	rec_p.join()
	mot_p.terminate()
	mot_p.join()"""
	video_capture.release()


if __name__ == "__main__":
	camera_loop()
