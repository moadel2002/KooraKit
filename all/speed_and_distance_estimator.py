import math
import numpy as np
class SpeedAndDistance_Estimator():
    def __init__(self,frame_rate,frame_window):
        self.frame_window=frame_window
        self.frame_rate=frame_rate

    def measure_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)
    
    def add_speed_and_distance_to_tracks(self, tracks):
        total_distance = {}
        speed_distance = tracks.copy()
        for track_id, frames in speed_distance.items():
            number_of_frames = len(frames)
            for frame_num in range(1, number_of_frames+1, self.frame_window):
                last_frame = min(frame_num + self.frame_window-1, number_of_frames)

                if frame_num not in frames or last_frame not in frames:
                    continue

                start_positionx1 = frames[frame_num][0]
                start_positiony1 = frames[frame_num][1]
                start_positionx2 = frames[frame_num][2]
                start_positiony2 = frames[frame_num][3]
                end_positionx1 = frames[frame_num][0]
                end_positiony1 = frames[frame_num][1]
                end_positionx2 = frames[frame_num][2]
                end_positiony2 = frames[frame_num][3] 
                start_position = [(start_positionx1+start_positionx2)/2,(start_positiony1+start_positiony2)/2]
                end_position = [(end_positionx1+end_positionx2)/2,(end_positiony1+end_positiony2)/2]
                if start_position is None or end_position is None:
                    continue
                distance_covered = self.measure_distance(start_position, end_position)
                time_elapsed = (last_frame - frame_num) / self.frame_rate

                if time_elapsed == 0:
                    continue
                speed_pixels_per_frame = distance_covered / time_elapsed
                speed_pixels_per_second = speed_pixels_per_frame*(1/self.frame_rate)
                speed_meters_per_second = speed_pixels_per_second * (105 / 583)
                speed_km_per_hour = speed_meters_per_second * 3.6

                if track_id not in total_distance:
                    total_distance[track_id] = 0
                
                total_distance[track_id] += distance_covered*(105/583)

                for frame_num_batch in range(frame_num, last_frame):
                    if frame_num_batch not in speed_distance[track_id]:
                        continue
                    frames[frame_num_batch] = np.concatenate([frames[frame_num_batch], np.array([speed_km_per_hour]),np.array([total_distance[track_id]])])
        
        return speed_distance
    
    # def draw_speed_and_distance(self,frames,tracks):
    #     output_frames = []
    #     for frame_num, frame in enumerate(frames):
    #         for object, object_tracks in tracks.items():
    #             if object == "ball" or object == "referees":
    #                 continue 
    #             for _, track_info in object_tracks[frame_num].items():
    #                if "speed" in track_info:
    #                    speed = track_info.get('speed',None)
    #                    distance = track_info.get('distance',None)
    #                    if speed is None or distance is None:
    #                        continue
                       
    #                    bbox = track_info['bbox']
    #                    position = get_foot_position(bbox)
    #                    position = list(position)
    #                    position[1]+=40

    #                    position = tuple(map(int,position))
    #                    cv2.putText(frame, f"{speed:.2f} km/h",position,cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)
    #                    cv2.putText(frame, f"{distance:.2f} m",(position[0],position[1]+20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)
    #         output_frames.append(frame)
        
    #     return output_frames