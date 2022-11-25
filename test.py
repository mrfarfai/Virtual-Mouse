import cv2

camera = 0
ans = True 

while ans:
	cap = cv2.VideoCapture(camera)
	ans, img = cap.read()
	if ans:
		camera += 1

fun = 0

def func(cur_camera):
	cap = cv2.VideoCapture(int(cur_camera))
	cur = 0
	while True:
		success, img = cap.read()
		cur += 1
		print(cur)
		if cur == 150:
			print("ok")
			cur_camera += 1
			print(camera)
			cur_camera %= camera
			cap.release()
			return cur_camera

		cv2.imshow("1", img)

		if cv2.waitKey(1) & 0xff == ord('q') or (cv2.getWindowProperty('1',cv2.WND_PROP_VISIBLE)) == 0:
			return -1

while fun != -1:
	fun = func(fun)

	print(fun)