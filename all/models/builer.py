import torch.nn as nn
import torch.nn.parallel as parallel

from . import vgg, resnet

def BuildAutoEncoder():

    configs = vgg.get_configs("vgg16")
    model = vgg.VGGAutoEncoder(configs)
    model = nn.DataParallel(model) #.cuda()

    return model