
from torch.utils.data import Dataset
import torch
import numpy as np
import h5py

class Loader(Dataset):

    def __init__(self, fname):
        self.fname = fname
        self.h = None
        self.data = None
        self.scores = None

    def _open(self):
        self.h = h5py.File(self.fname)
        self.data = self.h['data']
        self.scores = self.h['scores']

    def _check_open(self):
        if self.h is None:
            self._open()

    def __len__(self):
        self._check_open()
        return len(self.data)

    def __getitem__(self, idx):
        self._check_open()
        img = self.data[idx]
        lab = self.scores[idx]
        if not img.dtype==np.float32:
            img = img.astype(np.float32)
        img0, img1 = map( torch.tensor, img)
        contact = torch.dstack([torch.cdist(img0, img0), torch.cdist(img1, img1), torch.cdist(img0, img1)]).T
        lab = torch.tensor(lab[None])
        return contact, lab


if __name__=="__main__":
    d = Loader("train_4d.hdf5")
    img,lab = d[0]
    print(img.shape, d.shape)
