import os
def generate_tracks(path,model):
    for i,video in enumerate(sorted(os.listdir(path))):
        videopath = os.path.join(path,video)
        os.system(f"python /home/admin1/all/demo.py --path {videopath}")

path = "/home/admin1/all/DeepEIoU/DeepEIoU/tools/test_videos"
model = "/media/samar/HDD1T/detection/runs/detect/train2/weights/best.pt"
generate_tracks(path,model)
