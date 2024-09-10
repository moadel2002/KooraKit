"""
1 - video -> player_tracklets and ball_tracklets
"""
from argparse import Namespace
import base64
import os
import os.path as osp
import numpy as np
import time
import cv2
import torch
import sys
sys.path.append('all')
from DeepEIoU.DeepEIoU.tools.tracker.Deep_EIoU import Deep_EIoU
from DeepEIoU.DeepEIoU.tools.torchreid.utils import FeatureExtractor
from speed_and_distance_estimator import SpeedAndDistance_Estimator
import torchvision.transforms as T
from ultralytics import YOLO
from homogrophy_circle_sift import get_homography
import matplotlib.pyplot as plt
from encode import encoder
from joblib import Parallel,delayed 
from sklearn.cluster import KMeans
import seaborn as sns
from PIL import Image
import numpy as np
import io




TRACKER_ARGS = {'with_reid':True,'proximity_thresh':0.5,'appearance_thresh':0.25,'track_high_thresh':0.6,'track_low_thresh':0.1,'new_track_thresh':0.7,'track_buffer':60,'match_thresh':0.8,'aspect_ratio_thresh':1.6,'min_box_area':10,'nms_thres':0.7,'mot20':False}
TRACKER_ARGS = Namespace(**TRACKER_ARGS)
extractor = FeatureExtractor(
        model_name='osnet_x1_0',
        model_path = 'all/DeepEIoU/DeepEIoU/tools/checkpoints/sports_model.pth.tar-60',
        device='cpu'
    )  
player_detector = YOLO("all/playermodel/weights/best.pt")
ball_detector = YOLO("all/ballmodel/weights/best.pt") 

def imageflow_demo(frames,frame_height,frame_width,fps):
    tracker = Deep_EIoU(TRACKER_ARGS, frame_rate=fps)
    frame_id = 1
    results = []
    player_results = dict()
    ball_results = dict()
    homography_points = dict()
    track_bboxes = dict()
    for frame in frames:
        print(frame_id)
        playeroutputs = player_detector.predict(frame, conf=0.5,iou=0.45,imgsz=1024,verbose=False)
        balloutputs = ball_detector.predict(frame,conf=0.005,imgsz=1920,verbose=False)
        playerdet = playeroutputs[0].boxes.xyxy.cpu().numpy()
        balldet = balloutputs[0].boxes.xyxy.cpu().numpy()
        if playerdet.shape[0] != 0:
            playerconf = playeroutputs[0].boxes.conf.cpu().numpy()
            playerdet = np.hstack([playerdet,np.expand_dims(playerconf,axis=1)])
            rows_to_remove = np.any(playerdet[:, 0:4] < 1, axis=1) # remove edge playerdetection
            playerdet = playerdet[~rows_to_remove]
            cropped_imgs = [frame[max(0,int(y1)):min(frame_height,int(y2)),max(0,int(x1)):min(frame_width,int(x2))] for x1,y1,x2,y2,_ in playerdet]
            embs = extractor(cropped_imgs)
            embs = embs.cpu().detach().numpy()
            online_targets = tracker.update(playerdet, embs)
            online_tlwhs = []
            online_ids = []
            online_scores = []
            for t in online_targets:
                tlwh = t.last_tlwh
                tid = t.track_id
                if tlwh[2] * tlwh[3] > TRACKER_ARGS.min_box_area:
                    online_tlwhs.append(tlwh)
                    online_ids.append(tid)
                    online_scores.append(t.score)
                    results.append(
                        f"{frame_id},{tid},{tlwh[0]:.2f},{tlwh[1]:.2f},{tlwh[2]:.2f},{tlwh[3]:.2f},{t.score:.2f},-1,-1,-1\n"
                    )
        
        if balldet.shape[0] != 0:
            ballconf = balloutputs[0].boxes.conf.cpu().numpy()
            balldet = np.hstack([balldet,np.expand_dims(ballconf,axis=1)])
            mostconfidenceballdet = balldet[np.argmax(balldet[:,4])]
            ball_results[frame_id] = mostconfidenceballdet
        
        prev_frame = None if frame_id == 1 else frames[frame_id-2]
        next_frame = None if frame_id == len(frames) else frames[frame_id]
        frame_homography =  get_homography(frame,prev_frame,next_frame)
        homography_points[frame_id] = frame_homography

        frame_id += 1
    
    for result in results:
        result = result.strip().split(',')
        frame_id = int(result[0])
        track_id = int(result[1])
        x1 = float(result[2])
        y1 = float(result[3])
        w = float(result[4])
        h = float(result[5])
        x2 = x1+w
        y2 = y1+h
        if player_results.get(track_id) == None:
            player_results[track_id] = {}
        player_results[track_id][frame_id] = np.array([x1,y1,x2,y2])
    
    for track_id in player_results.keys():
        for frame in player_results[track_id].keys():
            bbox = player_results[track_id][frame]
            player = frames[frame-1][int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])]
            if track_bboxes.get(track_id) == None:
                track_bboxes[track_id] = {}
            track_bboxes[track_id][frame] = player
    return player_results,ball_results,homography_points,track_bboxes

#ball smoothing and linear interpolation
#gsi and AFlink

def transfer_playerpoints_to_plane(player_results,homography_points):
    transformed_player_results = {}
    for track_id in player_results.keys():
        frames_positions = player_results[track_id]
        for frame in frames_positions.keys():
            frame_position = frames_positions[frame]
            x1 = frame_position[0]
            y1 = frame_position[1]
            x2 = frame_position[2]
            y2 = frame_position[3]
            topleft = np.array([x1,y1])
            bottomright = np.array([x2,y2])
            if not isinstance(homography_points[frame]['homography'],np.ndarray):
                nearest_forward = None
                nearest_backward = None
                for nearest_frame_forward in range(frame+1,len(homography_points.keys())):
                    if isinstance(homography_points[nearest_frame_forward]['homography'],np.ndarray):
                        nearest_forward = nearest_frame_forward
                        break
                for nearest_frame_backward in range(frame-1,-1,-1):
                    if isinstance(homography_points[nearest_frame_backward]['homography'],np.ndarray):
                        nearest_backward = nearest_frame_backward
                        break 
                forward_distance = 2e9 if nearest_forward == None else abs(frame-nearest_frame_forward)
                backward_distance = 2e9 if nearest_backward == None else abs(frame-nearest_frame_backward)
                if forward_distance < backward_distance:
                    nearest_frame = nearest_frame_forward
                else:
                    nearest_frame = nearest_frame_backward
                for frame_homography in range(frame,nearest_frame+1) if nearest_frame == nearest_frame_forward else range(frame,nearest_frame-1,-1):
                    
                    if frame_homography == nearest_frame:
                        h = homography_points[frame_homography]['homography']
                    else:
                        h = homography_points[frame_homography]['next_homography'] if nearest_frame == nearest_frame_forward else homography_points[frame_homography]['prev_homography']
                    transformed_topleft = cv2.perspectiveTransform(topleft.reshape(-1,1,2),h)
                    transformed_bottomright = cv2.perspectiveTransform(bottomright.reshape(-1,1,2),h)
                    topleft = transformed_topleft[0][0]
                    bottomright = transformed_bottomright[0][0]

            else:    
                h = homography_points[frame]['homography']
                transformed_topleft = cv2.perspectiveTransform(topleft.reshape(-1,1,2),h)
                transformed_bottomright = cv2.perspectiveTransform(bottomright.reshape(-1,1,2),h)
            if transformed_player_results.get(track_id) == None:
                transformed_player_results[track_id] = {}
            transformed_topleft = transformed_topleft[0][0]
            transformed_bottomright = transformed_bottomright[0][0]
            
            if transformed_topleft[0] < 0:
                transformed_topleft[0] = 0
            if transformed_topleft[0] > 582:
                transformed_topleft[0] = 582
            if transformed_bottomright[0] < 0:
                transformed_bottomright[0] = 0
            if transformed_bottomright[0] > 582:
                transformed_bottomright[0] = 582
            if transformed_topleft[1] < 0:
                transformed_topleft[1] = 0
            if transformed_topleft[1] > 378:
                transformed_topleft[1] = 378
            if transformed_bottomright[1] < 0:
                transformed_bottomright[1] = 0
            if transformed_bottomright[1] > 378:
                transformed_bottomright[1] = 378
                
            transformed_player_results[track_id][frame] = np.array([float(transformed_topleft[0]),float(transformed_topleft[1]),float(transformed_bottomright[0]),float(transformed_bottomright[1])])
    return transformed_player_results

def transfer_ballpoints_to_plane(homography_points,ball_results):
    transformed_ball_results = {}
    for frame in ball_results.keys():
        frame_position = ball_results[frame]
        x1 = frame_position[0]
        y1 = frame_position[1]
        x2 = frame_position[2]
        y2 = frame_position[3]
        topleft = np.array([x1,y1])
        bottomright = np.array([x2,y2])
        if not isinstance(homography_points[frame]['homography'],np.ndarray):
            nearest_forward = None
            nearest_backward = None
            for nearest_frame_forward in range(frame+1,len(homography_points.keys())):
                if isinstance(homography_points[nearest_frame_forward]['homography'],np.ndarray):
                    nearest_forward = nearest_frame_forward
                    break
            for nearest_frame_backward in range(frame-1,-1,-1):
                if isinstance(homography_points[nearest_frame_backward]['homography'],np.ndarray):
                    nearest_backward = nearest_frame_backward
                    break 
            forward_distance = 2e9 if nearest_forward == None else abs(frame-nearest_frame_forward)
            backward_distance = 2e9 if nearest_backward == None else abs(frame-nearest_frame_backward)
            if forward_distance < backward_distance:
                nearest_frame = nearest_frame_forward
            else:
                nearest_frame = nearest_frame_backward
            for frame_homography in range(frame,nearest_frame+1) if nearest_frame == nearest_frame_forward else range(frame,nearest_frame-1,-1):
                
                if frame_homography == nearest_frame:
                    h = homography_points[frame_homography]['homography']
                else:
                    h = homography_points[frame_homography]['next_homography'] if nearest_frame == nearest_frame_forward else homography_points[frame_homography]['prev_homography']
                transformed_topleft = cv2.perspectiveTransform(topleft.reshape(-1,1,2),h)
                transformed_bottomright = cv2.perspectiveTransform(bottomright.reshape(-1,1,2),h)
                topleft = transformed_topleft[0][0]
                bottomright = transformed_bottomright[0][0]

        else:    
            h = homography_points[frame]['homography']
            transformed_topleft = cv2.perspectiveTransform(topleft.reshape(-1,1,2),h)
            transformed_bottomright = cv2.perspectiveTransform(bottomright.reshape(-1,1,2),h)
            transformed_topleft = transformed_topleft
            transformed_bottomright = transformed_bottomright
        if transformed_ball_results.get(frame) == None:
            transformed_ball_results[frame] = {}
        transformed_topleft = transformed_topleft[0][0]
        transformed_bottomright = transformed_bottomright[0][0]

        if transformed_topleft[0] < 0:
            transformed_topleft[0] = 0
        if transformed_topleft[0] > 582:
            transformed_topleft[0] = 582
        if transformed_bottomright[0] < 0:
            transformed_bottomright[0] = 0
        if transformed_bottomright[0] > 582:
            transformed_bottomright[0] = 582
        if transformed_topleft[1] < 0:
            transformed_topleft[1] = 0
        if transformed_topleft[1] > 378:
            transformed_topleft[1] = 378
        if transformed_bottomright[1] < 0:
            transformed_bottomright[1] = 0
        if transformed_bottomright[1] > 378:
            transformed_bottomright[1] = 378
            
        transformed_ball_results[frame] = np.array([float(transformed_topleft[0]),float(transformed_topleft[1]),float(transformed_bottomright[0]),float(transformed_bottomright[1])])
    return transformed_ball_results

def cae_with_kmeans(transformed_player_results,track_bboxes):
    
    #eliminate goalkeeper boxes
    first_penalty_area = [2, 82,100, 300]
    second_penalty_area = [482, 82,580, 300]
    goalkeeperids = []
    for track_id in transformed_player_results.keys():
        frame_count = 0
        for frame in transformed_player_results[track_id].keys():
            framepositions = transformed_player_results[track_id][frame]
            if (framepositions[0] >= first_penalty_area[0] and framepositions[0] <= first_penalty_area[2] and framepositions[2] >= first_penalty_area[0] and framepositions[2] <= first_penalty_area[2] and framepositions[1] >= first_penalty_area[1] and framepositions[1] <= first_penalty_area[3] and framepositions[3] >= first_penalty_area[1] and framepositions[3] <= first_penalty_area[3]) or (framepositions[0] >= second_penalty_area[0] and framepositions[0] <= second_penalty_area[2] and framepositions[2] >= second_penalty_area[0] and framepositions[2] <= second_penalty_area[2] and framepositions[1] >= second_penalty_area[1] and framepositions[1] <= second_penalty_area[3] and framepositions[3] >= second_penalty_area[1] and framepositions[3] <= second_penalty_area[3]):
                frame_count+=1
        ratio = frame_count / len(transformed_player_results[track_id])
        if ratio >= 0.7:
            goalkeeperids.append(track_id)
    
    features = 0
    print(goalkeeperids)
    for track_id in track_bboxes.keys():
        if track_id in goalkeeperids:
            continue
        feature = np.array(Parallel(n_jobs=4)(delayed(encoder)(track_bboxes[track_id][frame]) for frame in track_bboxes[track_id].keys()))
        if isinstance(features,int):
            features=feature
        else:
            features = np.vstack([features, feature])
    print(features.shape)
    kmeans = KMeans(n_clusters=3, init="k-means++",n_init=10)
    labels = kmeans.fit(features)
    return kmeans

def assign_teams(kmeans,track_bboxes,player_results,transformed_player_results):
    teams = {}
    for track_id in track_bboxes.keys():
        class0 = 0
        class1 = 0
        class2 = 0
        for frame in track_bboxes[track_id].keys():
            bbox = track_bboxes[track_id][frame]
            feature = encoder(bbox)
            team_id=kmeans.predict(feature.reshape(1,-1))[0]
            class0+=(team_id==0)
            class1+=(team_id==1)
            class2+=(team_id==2)
        maxi = max(class0,class1,class2)
        if maxi == class0:
            teams[track_id] = 0
        else:
            teams[track_id] = 1
    return teams

def heatmap(transformed_player_results,track_id):
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    pitch = cv2.imread("all/7oka white.jpg")
    pitch = cv2.cvtColor(pitch,cv2.COLOR_BGR2RGB)
    xcenter = np.array([(points[0]+points[2])/2 for points in transformed_player_results[track_id].values()])
    ycenter = np.array([(points[1]+points[3])/2 for points in transformed_player_results[track_id].values()])
    plt.axis('off')
    sns.kdeplot(x=xcenter,y=ycenter,fill=True,levels=40,cmap='Greens',ax=ax,zorder=1)
    plt.ylim(0, 379)
    plt.xlim(0, 583)
    plt.gca().invert_yaxis()
    ax.imshow(pitch,zorder=2,alpha=0.2)
    fig.canvas.draw()
    buf = fig.canvas.tostring_rgb()
    ncols, nrows = fig.canvas.get_width_height()
    image = np.frombuffer(buf, dtype=np.uint8).reshape(nrows, ncols, 3)
    return image

def distanceandspeed(transformed_player_results,fps,frame_window):
    sb = SpeedAndDistance_Estimator(fps,frame_window)
    speedanddistance = sb.add_speed_and_distance_to_tracks(transformed_player_results)
    return speedanddistance

def getdistance(speedanddistance,track_id):
    sum = 0
    for frames in speedanddistance[track_id].values():
        sum+= 0 if len(frames) == 4 else frames[5]
    avgdis = sum / len(speedanddistance[track_id])
    return avgdis

def getspeed(speedanddistance,track_id):
    sum = 0
    for frames in speedanddistance[track_id].values():
        sum+= 0 if len(frames) == 4 else frames[4]
    avgspeed = sum / len(speedanddistance[track_id])
    return avgspeed

def getall(speedanddistance,teams,transformed_player_results):
    allmetrics = {}
    for track_id in transformed_player_results.keys():
        dist = getdistance(speedanddistance,track_id)
        speed = getspeed(speedanddistance,track_id)
        heat = heatmap(transformed_player_results,track_id)
        img = Image.fromarray(heat)
        img_byte_array = io.BytesIO()
        img.save(img_byte_array, format='PNG')
        # Convert image bytes buffer to base64 string
        img_byte_array.seek(0)
        base64_img = base64.b64encode(img_byte_array.read()).decode('utf-8')

        team = teams[track_id]
        if team!=1 and team!=0:
            team = 1 
        allmetrics[track_id] = {'teams':teams[track_id],'speed':speed,'distance':dist, 'heat':base64_img}
    return allmetrics

cap = cv2.VideoCapture("all/video.avi")
frames = []
i = 1
while(cap.isOpened()):
    ret,frame = cap.read()
    if ret == True:
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        frames.append(frame)
    else:
        break
    # if i > 25:
    #     break
    # i+=1

# print(frames)
# playerresults,ballresults,homography,trackbboxes = imageflow_demo(frames[:1],1080,1920,30)
# transformed_player_points = transfer_playerpoints_to_plane(playerresults,homography)
# transformed_ball_points = transfer_ballpoints_to_plane(homography,ballresults)
# kmeans = cae_with_kmeans(transformed_player_points,trackbboxes)
# teams = assign_teams(kmeans,trackbboxes,playerresults,transformed_player_points)
# alldistanceandspeed = distanceandspeed(transformed_player_points,25,5)
# alldata = getall(alldistanceandspeed,teams,transformed_player_points)
# print(alldata)
#heat = heatmap(transformed_player_points,1)
#avgdis = getdistance(alldistanceandspeed,1)
#avgspeed = getspeed(alldistanceandspeed,1)