import os
import cv2

def make_videos(path,videos_path):

    for folder in sorted(os.listdir(path)):
        if folder == "SNMOT-150" or folder == "SNMOT-187" or folder == "SNMOT-188": 
            imgfolder = os.path.join(path,f"{folder}/img1")
            videopath = os.path.join(videos_path,f"{folder}.avi")
            video = cv2.VideoWriter(videopath,fourcc=0,fps=25,frameSize=(1920,1080))
            print(videopath)
            for img in sorted(os.listdir(imgfolder)):
                im = cv2.imread(os.path.join(imgfolder,img))
                video.write(im)
            video.release()

path = "/home/admin1/all/DeepEIoU/DeepEIoU/tools/tracking/test"
videos_path = "/home/admin1/all/DeepEIoU/DeepEIoU/tools/test_videos"
make_videos(path,videos_path)