import os
import numpy as np
import torch
import torch.utils.data as data
from torch.utils.data import Dataset
from PIL import Image
from copy import deepcopy
import shutil
import json

def InfiniteSampler(n):
    """Data sampler"""
    i = n - 1
    order = np.random.permutation(n)
    while True:
        yield order[i]
        i += 1
        if i >= n:
            np.random.seed()
            order = np.random.permutation(n)
            i = 0


class InfiniteSamplerWrapper(data.sampler.Sampler):
    """Data sampler wrapper"""
    def __init__(self, data_source):
        self.num_samples = len(data_source)

    def __iter__(self):
        return iter(InfiniteSampler(self.num_samples))

    def __len__(self):
        return 2 ** 31


def copy_G_params(model):
    flatten = deepcopy(list(p.data for p in model.parameters()))
    return flatten
    

def load_params(model, new_param):
    for p, new_p in zip(model.parameters(), new_param):
        p.data.copy_(new_p)


def get_dir(args):
    task_name = 'train_results/' + args.name
    if not os.path.exists('train_results/'):
        os.mkdir('train_results/')
    if not os.path.exists(task_name):
        os.mkdir(task_name)
    saved_model_folder = os.path.join( task_name, 'models')
    saved_image_folder = os.path.join( task_name, 'images')

    if not os.path.exists(saved_model_folder):
        os.mkdir(saved_model_folder)
    if not os.path.exists(saved_image_folder):
        os.mkdir(saved_image_folder)

    # for f in os.listdir('./'):
    #     if '.py' in f:
    #         shutil.copy(f, task_name+'/'+f)
    
    with open( os.path.join(saved_model_folder, '../args.txt'), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    return saved_model_folder, saved_image_folder


class  ImageFolder(Dataset):
    """docstring for ArtDataset"""
    def __init__(self, root, transform=None):
        super( ImageFolder, self).__init__()
        self.root = root
        self.path_imagelist_txt=root
        self.frame = self._parse_frame()
        self.transform = transform

    def _parse_frame(self):
        filenames = open(self.path_imagelist_txt).readlines()
        filenames = list(map(lambda x: x.strip('\n'), filenames))
        self.names = list(map(lambda x: x.split('/')[-1], filenames))
        return filenames

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, idx):
        file = self.frame[idx]
        img = Image.open(file).convert('RGB')
            
        if self.transform:
            img = self.transform(img) 

        return img



# from io import BytesIO
# import lmdb
# from torch.utils.data import Dataset
#
#
# class MultiResolutionDataset(Dataset):
#     def __init__(self, path, transform, resolution=256):
#         self.env = lmdb.open(
#             path,
#             max_readers=32,
#             readonly=True,
#             lock=False,
#             readahead=False,
#             meminit=False,
#         )
#
#         if not self.env:
#             raise IOError('Cannot open lmdb dataset', path)
#
#         with self.env.begin(write=False) as txn:
#             self.length = int(txn.get('length'.encode('utf-8')).decode('utf-8'))
#
#         self.resolution = resolution
#         self.transform = transform
#
#     def __len__(self):
#         return self.length
#
#     def __getitem__(self, index):
#         with self.env.begin(write=False) as txn:
#             key = '{self.resolution}-{str(index).zfill(5)}'.encode('utf-8')
#             img_bytes = txn.get(key)
#             #key_asp = f'aspect_ratio-{str(index).zfill(5)}'.encode('utf-8')
#             #aspect_ratio = float(txn.get(key_asp).decode())
#
#         buffer = BytesIO(img_bytes)
#         img = Image.open(buffer)
#         img = self.transform(img)
#
#         return img

