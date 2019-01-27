import cv2
from time import sleep
from multiprocessing import Queue, Value


def diffImg(t0, t1, t2):
	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)


def motion(frame, last_frame):
	last_frame = cv2.cvtColor(last_frame, cv2.COLOR_RGB2GRAY)
	last_frame = cv2.GaussianBlur(last_frame, (21, 21), 0)

	frame = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
	frame = cv2.GaussianBlur(frame, (21, 21), 0)

	frameDelta = cv2.absdiff(last_frame, frame)
	thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

	movement = 0

	(_, cnts, _) = cv2.findContours(thresh.copy(),
									cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for contour in cnts:
		movement += cv2.contourArea(contour)
		"""if cv2.contourArea(contour) < 10000:
			continue
		movement += 1

		(x, y, w, h) = cv2.boundingRect(contour)
		# making green rectangle arround the moving object
		cv2.rectangle(diff, (x, y), (x + w, y + h), (0, 255, 0), 3)"""

	#cv2.imshow("Frame Delta", frameDelta)

	return int(movement)


def motion_loop(frame_queue: Queue, is_moving, stop_all: Value):
	last_frame = None
	while True:
		frame = frame_queue.get()
		if last_frame is not None:
			is_moving.value = motion(frame, last_frame)
		last_frame = frame
