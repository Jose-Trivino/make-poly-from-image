import cv2
import sys

if len(sys.argv) != 3:
    sys.exit(1)

input_path = sys.argv[1]
input_img = cv2.imread(input_path, cv2.COLOR_BGR2GRAY)

if input_img is None:
    sys.exit(1)

try:
    thresh = int(sys.argv[2])
except ValueError:
    print("Error: Valor debe ser un entero.")
    sys.exit(1)

ret, thresh_img = cv2.threshold(input_img, thresh, 255, cv2.THRESH_BINARY)

cv2.imshow("Thresholded image", thresh_img)
cv2.waitKey(0)
cv2.destroyAllWindows()