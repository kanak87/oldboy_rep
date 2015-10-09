from nn import *
from nn2 import *
from image import *

# left_eye_center_x,left_eye_center_y,right_eye_center_x,right_eye_center_y,left_eye_inner_corner_x,left_eye_inner_corner_y,left_eye_outer_corner_x,left_eye_outer_corner_y,right_eye_inner_corner_x,right_eye_inner_corner_y,right_eye_outer_corner_x,right_eye_outer_corner_y,left_eyebrow_inner_end_x,left_eyebrow_inner_end_y,left_eyebrow_outer_end_x,left_eyebrow_outer_end_y,right_eyebrow_inner_end_x,right_eyebrow_inner_end_y,right_eyebrow_outer_end_x,right_eyebrow_outer_end_y,nose_tip_x,nose_tip_y,mouth_left_corner_x,mouth_left_corner_y,mouth_right_corner_x,mouth_right_corner_y,mouth_center_top_lip_x,mouth_center_top_lip_y,mouth_center_bottom_lip_x,mouth_center_bottom_lip_y,Image
'''
net = loadNet('net1.pickle')
X = read_sample(
    ['./data/iu.jpeg', './data/1.png', './data/2.png', './data/3.png', './data/4.png', './data/5.png', './data/6.png', './data/7.png',
     './data/8.png'])
y = predcit(net, X)
'''

#net = loadNet2('test.pickle')
net = loadNet('net1.pickle')
X = read_sample(
    ['./data2/iu.jpeg', './data2/1.png', './data2/2.png', './data2/3.png', './data2/4.png', './data2/5.png',
     './data2/6.png', './data2/7.png', './data2/8.png'])
y = predcit(net, X)
#y = predcit2(net, X)

draw_result(X, y)
'''
retraining(net1, X, y)

X = read_sample(['test.png'])
y = predcit(net1, X)

drawResult(X, y)

pyplot.figure()
pyplot.imshow(iuImage, cmap='gray')
pyplot.show()
'''
