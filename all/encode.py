#!/usr/bin/env python

import argparse

from PIL import Image

import torch
from torchvision.transforms import transforms

import sys

from utils import init_seeds, load_dict
import models.builer as builder

import os

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def encode(model, img):

    with torch.no_grad():

        code = model.module.encoder(img).cpu().numpy()

    return code

def encoder(img):
    
    init_seeds(1, cuda_deterministic=False)

    model = builder.BuildAutoEncoder()     
    load_dict("all/004.pth", model)
    trans = transforms.Compose([
                    transforms.Resize(256),                   
                    transforms.CenterCrop(224),
                    transforms.ToTensor()
                  ])

    img = Image.fromarray(img)
    img = trans(img).unsqueeze(0)#.cuda()
    model.eval()
    code = encode(model, img)
    code = code.flatten()
    return code


