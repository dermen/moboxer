# Define LeNet model
import torch.nn as nn
import torchvision
import torch.nn.functional as F
import torch

class LeNet(nn.Module):
    def __init__(self, dev=None):
        """
        :param dev: pytorch device
        """
        super().__init__()
        if dev is None:
            self.dev = "cuda:0"
        else:
            self.dev = dev
        #self.res = torchvision.models.resnet18()
        #self.res.conv1 = nn.Conv2d(3, 64, kernel_size=(7, 7), stride=(2, 2), padding=(3, 3), bias=False)
        #self.fc1 = nn.Linear(1000,100, device=self.dev)
        #self.fc2 = nn.Linear(100, 1, device=self.dev)

        self.conv1 = nn.Conv2d(3, 6, 3, device=self.dev)
        self.conv2 = nn.Conv2d(6, 16, 3, device=self.dev)
        self.conv3 = nn.Conv2d(16, 32, 3, device=self.dev)

        self.fc1 = nn.Linear(1152, 100, device=self.dev)
        self.fc2 = nn.Linear(100, 1, device=self.dev)
        self.relu = nn.ReLU()

    def forward(self, x):
        #x = self.res(x)
        #x = torch.flatten(x, 1)
        #x = F.relu(self.fc1(x))
        #x = self.fc2(x)
        #return x
        x = F.max_pool2d(F.relu(self.conv1(x)), (2, 2))
        x = F.max_pool2d(F.relu(self.conv2(x)), 2)
        x = F.max_pool2d(F.relu(self.conv3(x)), 2)

        x = torch.flatten(x, 1)

        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def main():
    import torch
    from torch.utils.data import random_split, DataLoader
    from torch.optim import Adam
    import os
    from scipy.stats import pearsonr
    from moboxer.data_loader import Loader
    bs = 16
    dev = "cpu"
    odir = "out"
    if not os.path.exists(odir):
        os.makedirs(odir)
    #dev = "cuda:0"

    ds = Loader("train_4d.hdf5")
    #ds_test = Loader("test_4d.hdf5")
    lr=1e-1
    nepoch=100

    ntot = len(ds)
    nval =  int(0.1*len(ds))
    ntest = int(0.1*len(ds))

    ds_train, ds_val, ds_test = random_split(ds, lengths=[ntot-nval-ntest, nval, ntest])
    train_dl = DataLoader(ds_train,batch_size=bs, shuffle=True, num_workers=0)
    val_dl = DataLoader(ds_val, batch_size=bs)
    test_dl = DataLoader(ds_test, batch_size=bs)

    model = LeNet(dev=dev)
    optim = Adam(model.parameters(), lr=lr)
    #calc_loss = torch.nn.BCELoss()
    calc_loss = torch.nn.L1Loss()

    #rs = Resize((32,32), antialias=True)
    #sig = torch.nn.Sigmoid()

    for i_ep in range(nepoch):
        model.train()
        for i_batch, (imgs, labs) in enumerate(train_dl):
            optim.zero_grad()
            #imgs = rs(imgs)
            imgs = imgs.to(dev)
            labs = labs.to(dev)
            preds = model(imgs)
            #preds = sig(preds)
            loss = calc_loss(preds, labs)
            loss.backward()
            optim.step()
            print(f"Ep{i_ep+1}; batch {i_batch+1}/{len(train_dl)}, loss={loss.item():.5f}", end="\r", flush=True)
        print(f"\nDone with Epoch {i_ep+1}/{nepoch}")
        model.eval()
        val_preds = []
        val_labs = []
        test_preds = []
        test_labs = []
        with torch.no_grad():
            for i, (imgs, labs) in enumerate(val_dl):
                #imgs = rs(imgs)
                imgs = imgs.to(dev)
                labs = labs.to(dev)
                preds = model(imgs)
                val_preds += [p.item() for p in preds[:, 0]]
                val_labs += [l.item() for l in labs[:,0]]
                print(f"val batch {i+1}/{len(test_dl)}", end="\r",flush=True )
            print("")
            for i, (imgs, labs) in enumerate(test_dl):
                #imgs = rs(imgs)
                imgs = imgs.to(dev)
                labs = labs.to(dev)
                preds = model(imgs)
                test_preds += [p.item() for p in preds[:, 0]]
                test_labs += [l.item() for l in labs[:,0]]
                print(f"test batch {i+1}/{len(test_dl)}", end="\r", flush=True)
            print("")
            val_cc = pearsonr(val_labs, val_preds)[0]
            test_cc = pearsonr(test_labs, test_preds)[0]
            #val_acc = val_nmatch / len(val_ds)
            #test_acc = test_nmatch / len(test_ds)
            print(f"cc at Ep {i_ep+1} ; valcc: {val_cc:.4f} , testcc: {test_cc:.4f} ")
            # save the model weights
            model_file = os.path.join(odir, f"state_ep{i_ep+1}.net")
            if not os.path.exists(odir):
                os.makedirs(odir)
            torch.save(model.state_dict(), model_file)

if __name__=="__main__":
    main()