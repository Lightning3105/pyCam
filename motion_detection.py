import cv2
from time import sleep
from multiprocessing import Process


def diffImg(t0, t1, t2):
	d1 = cv2.absdiff(t2, t1)
	d2 = cv2.absdiff(t1, t0)
	return cv2.bitwise_and(d1, d2)


def motion(frameQueue):
	lastFrame = frameQueue.get()
	lastFrame = cv2.cvtColor(lastFrame, cv2.COLOR_RGB2GRAY)
	lastFrame = cv2.GaussianBlur(lastFrame, (21, 21), 0)

	thisFrame = frameQueue.get()
	frameQueue.put(thisFrame.copy())
	thisFrame = cv2.cvtColor(thisFrame, cv2.COLOR_RGB2GRAY)
	thisFrame = cv2.GaussianBlur(thisFrame, (21, 21), 0)

	frameDelta = cv2.absdiff(lastFrame, thisFrame)
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
