import os
import numpy as np
path = "/media/samar/HDD1T/Deep-EIoU/Deep-EIoU/tools/track_vis"
for file in os.listdir(path):
    filepath = os.path.join(path,file)
    lines = np.loadtxt(filepath,dtype=int,delimiter=' ')
    lines = lines[np.lexsort((lines[:,1],lines[:,0]))]
    np.savetxt(filepath, lines, fmt='%d, %d, %d, %d, %d, %d, %d, %d, %d, %d',delimiter=',')
