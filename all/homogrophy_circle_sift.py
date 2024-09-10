import cv2
import numpy as np
from ultralytics import YOLO

plane = {
        "Big rect. left bottom_index_0": [2, 300],
    "Big rect. left main_index_0" : [100, 300],
    "Big rect. left main_index_1": [100, 82],
    "Big rect. left top_index_0": [2, 82],
    "Big rect. right bottom_index_1": [580, 300],
    "Big rect. right main_index_0": [482, 82],
    "Big rect. right main_index_1": [482, 300],
    "Big rect. right top_index_1": [580, 82],
    "Middle line_index_0" : [291, 2],
    "Middle line_index_1" : [291, 376],
    "Side line left_index_0" : [2, 376],
    "Side line left_index_1" : [2, 2],
    "Side line right_index_0" : [580, 2],
    "Side line right_index_1" : [580, 376],
    "Small rect. left bottom_index_0" : [2, 240],
    "Small rect. left main_index_0" : [36, 240],
    "Small rect. left main_index_1" : [36, 140],
    "Small rect. left top_index_0" : [2, 140],
    "Small rect. right bottom_index_1" : [580, 240],
    "Small rect. right main_index_0" : [547, 141],
    "Small rect. right main_index_1" : [547, 240],
    "Small rect. right top_index_1" :   [580, 141],
    "circle_bottom_index_0" : [292, 238],
    "circle_left_index_0" : [242, 191],
    "circle_right_index_0" : [340, 191],
    "circle_top_index_0" : [292, 140]

}

original_names = {
       0 : "Big rect. left bottom_index_0",
  1 : "Big rect. left main_index_0",
  2 : "Big rect. left main_index_1",
  3 : "Big rect. left top_index_0",
  4 : "Big rect. right bottom_index_1",
  5 : "Big rect. right main_index_0",
  6 : "Big rect. right main_index_1",
  7 : "Big rect. right top_index_1",
  8 : "Goal left post left _index_0",
  9 : "Goal left post left _index_1",
  10 : "Goal left post right_index_0",
  11 : "Goal left post right_index_1",
  12 : "Goal right post left_index_0",
  13 : "Goal right post left_index_1",
  14 : "Goal right post right_index_0",
  15 : "Goal right post right_index_1",
  16 : "Middle line_index_0",
  17 : "Middle line_index_1",
  18 : "Side line left_index_0",
  19 : "Side line left_index_1",
  20 : "Side line right_index_0",
  21 : "Side line right_index_1",
  22 : "Small rect. left bottom_index_0",
  23 : "Small rect. left main_index_0",
  24 : "Small rect. left main_index_1",
  25 : "Small rect. left top_index_0",
  26 : "Small rect. right bottom_index_1",
  27 : "Small rect. right main_index_0",
  28 : "Small rect. right main_index_1",
  29 : "Small rect. right top_index_1",
  30 : "circle_bottom_index_0",
  31 :  "circle_left_index_0" ,
  32 :  "circle_right_index_0" ,
  33 :  "circle_top_index_0" 
}

goal_points= ["Goal left post left _index_0"
  ,"Goal left post left _index_1"
  ,"Goal left post right_index_0"
  ,"Goal left post right_index_1"
  ,"Goal right post left_index_0"
  ,"Goal right post left_index_1"
  ,"Goal right post right_index_0"
  ,"Goal right post right_index_1"]

field_model = YOLO('all/model_with_circle.pt') 


def get_sift_descriptors(frame1, frame2):
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(frame1, None)
    kp2, des2 = sift.detectAndCompute(frame2, None)

    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks = 50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(des1,des2,k=2)
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    if len(good)>3:
        src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
        h, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    
        return h
    else:
        return None


def get_homography(frame, prev_frame= None, next_frame=None,x=0):
    src_points = []
    dst_points = []
    MIN_MATCH_COUNT = 4
    sift = cv2.SIFT_create()
    frame_dict={}
    results = field_model(frame,verbose=False)

    for result in results:
        keypoints = result.keypoints.data.tolist()
        
        box = result.boxes.cls
        for i in range(len(keypoints)):            
            field_name=original_names[int(box[i])]
            if(field_name in goal_points):
                continue 
            else:

                src_points.append(keypoints[i])

                dst_points.append(plane[field_name])

    if len(src_points) > 3:
        h, status = cv2.findHomography(np.array(src_points), np.array(dst_points),cv2.RANSAC, 5.0)

        frame_dict["homography"]= h
    else:
        frame_dict["homography"]=None

    if (prev_frame is not None):
        
        frame_dict["prev_homography"]=get_sift_descriptors(frame, prev_frame)

    if (next_frame is not None):
        
        frame_dict["next_homography"]=get_sift_descriptors(frame, next_frame)

    return frame_dict