import cv2
from time import sleep
from multiprocessing import Process


def diffImg(t0, t1, t2):
	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)


def motion(frameQueue):
	img1 = frameQueue.get()
	img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
	img1 = cv2.GaussianBlur(img1, (21, 21), 0)

	img2 = frameQueue.get()
	frameQueue.put(img2.copy())
	img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
	img2 = cv2.GaussianBlur(img2, (21, 21), 0)

	img3 = frameQueue.get()
	frameQueue.put(img3.copy())
	img3 = cv2.cvtColor(img3, cv2.COLOR_RGB2GRAY)
	img3 = cv2.GaussianBlur(img3, (21, 21), 0)

	diff = diffImg(img1, img2, img3)

	movement = 0

	(_, cnts, _) = cv2.findContours(diff.copy(),
									cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	for contour in cnts:
		if cv2.contourArea(contour) < 10000:
			continue
		movement += 1

		(x, y, w, h) = cv2.boundingRect(contour)
		# making green rectangle arround the moving object
		cv2.rectangle(diff, (x, y), (x + w, y + h), (0, 255, 0), 3)

	return movement
