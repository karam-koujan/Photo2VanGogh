import torch 
import random 
import matplotlib.pyplot as plt 
from torchvision.utils import make_grid
import wandb
import os 





class ReplayBuffer():
    """
    ReplayBuffer is a class used to store and manage a buffer of tensors with a fixed maximum size.
    It supports adding new data to the buffer and retrieving a mix of new and old data.

    Attributes:
    -----------
    max_size : int
        The maximum number of elements the buffer can hold.
    data : list
        The list storing the tensors in the buffer.

    Methods:
    --------
    __init__(self, max_size=50):
        Initializes the ReplayBuffer with a specified maximum size.

    push_and_pop(self, data):
        Adds new data to the buffer and returns a tensor containing either
        the new data or a mix of new and randomly selected old data from the buffer.
    """

    def __init__(self, max_size=50):
        assert (max_size > 0), 'Empty buffer or trying to create a black hole. Be careful.'
        self.max_size = max_size
        self.data = []

    def push_and_pop(self, data):
        to_return = []
        for element in data.data:
            element = torch.unsqueeze(element, 0)
            if len(self.data) < self.max_size:
                self.data.append(element)
                to_return.append(element)
            else:
                if random.uniform(0,1) > 0.5:
                    i = random.randint(0, self.max_size-1)
                    to_return.append(self.data[i].clone())
                    self.data[i] = element
                else:
                    to_return.append(element)
        return torch.cat(to_return)


def weights_init_normal(m):
    """
    Initializes the weights of a given module using a normal distribution. The initialization
    behavior depends on the type of the module.

    Parameters:
    -----------
    m : torch.nn.Module
        The module whose weights are to be initialized. This can be a convolutional layer,
        a batch normalization layer, or any other module with weights.

    Notes:
    ------
    - For convolutional layers (modules whose class name contains 'Conv'):
        - The weights are initialized from a normal distribution with mean 0.0 and standard deviation 0.02.
        - If the layer has a bias term, it is initialized to 0.0.
    - For batch normalization layers (modules whose class name contains 'BatchNorm2d'):
        - The weights are initialized from a normal distribution with mean 1.0 and standard deviation 0.02.
        - The bias is initialized to 0.0.
    """
    classname = m.__class__.__name__
    if classname.find('Conv') != -1:
        torch.nn.init.normal_(m.weight.data, 0.0, 0.02) 
        if hasattr(m, 'bias') and m.bias is not None:
            torch.nn.init.constant_(m.bias.data, 0.0) 
        elif classname.find('BatchNorm2d') != -1:
            torch.nn.init.normal_(m.weight.data, 1.0, 0.02) 
            torch.nn.init.constant_(m.bias.data, 0.0) 


class LambdaLR:
    """
    LambdaLR is a learning rate scheduler that linearly decays the learning rate after a specified epoch.

    Attributes:
    -----------
    n_epochs : int
        Total number of epochs for training.
    offset : int
        Offset to add to the current epoch when calculating the decay.
    decay_start_epoch : int
        The epoch at which to start the linear decay of the learning rate.

    Methods:
    --------
    __init__(self, n_epochs, offset, decay_start_epoch):
        Initializes the LambdaLR with the total number of epochs, offset, and decay start epoch.

    step(self, epoch):
        Calculates the learning rate multiplier for a given epoch.
    """

    def __init__(self, n_epochs, offset, decay_start_epoch):
        assert (n_epochs - decay_start_epoch) > 0, "Decay must start before the training session ends!"
        self.n_epochs = n_epochs
        self.offset = offset
        self.decay_start_epoch = decay_start_epoch
        
    def step(self, epoch):
        return 1.0 - max(0, epoch+self.offset - self.decay_start_epoch)/(self.n_epochs - self.decay_start_epoch)




class ShowImages():
      """
    A class to handle the display and logging of generated images using two Generative Adversarial Networks (GANs).

    Attributes:
    -----------
    G_AB : torch.nn.Module
        The generator model that translates images from domain A to domain B.
    G_BA : torch.nn.Module
        The generator model that translates images from domain B to domain A.
    dataloader : torch.utils.data.DataLoader
        A PyTorch DataLoader providing batches of images from both domains A and B.
    device : torch.device
        The device (CPU or GPU) on which the models and data are loaded.

    Methods:
    --------
    sample_images():
        Generates a grid of real and fake images and displays them using matplotlib.
    log_generated_images(epoch: int):
        Logs the generated images to Weights and Biases (wandb) with appropriate captions for the specified epoch.
      """
      def __init__(self,G_AB,G_BA,dataloader,device): 
             self.dataloader = dataloader 
             self.G_AB = G_AB 
             self.G_BA = G_BA
             self.device = device
      def sample_images(self):
            imgs = next(iter(self.dataloader))
            self.G_AB.eval()
            self.G_BA.eval()
            real_A = imgs['A'].to(self.device)
            real_B = imgs['B'].to(self.device) 
            fake_B = self.G_AB(real_A).detach()
            fake_A = self.G_BA(real_B).detach()
            real_A = make_grid(real_A, nrow=5, normalize=True)
            fake_B = make_grid(fake_B, nrow=5, normalize=True)
            real_B = make_grid(real_B, nrow=5, normalize=True)
            fake_A = make_grid(fake_A, nrow=5, normalize=True)
            image_grid = torch.cat((real_A, fake_B, real_B, fake_A), 1)
            plt.imshow(image_grid.cpu().permute(1,2,0))
            plt.title('Real A vs Fake B | Real B vs Fake A')
            plt.axis('off')
            plt.show(); 
      def log_generated_images(self,epoch) : 

            imgs = next(iter(self.dataloader))
            self.G_AB.eval()
            self.G_BA.eval()
            real_A = imgs['A'].to(self.device)
            real_B = imgs['B'].to(self.device) 
            fake_B = self.G_AB(real_A).detach()
            fake_A = self.G_BA(real_B).detach()
            # Arange images along x-axis
            real_A = make_grid(real_A, nrow=5, normalize=True)
            real_B = make_grid(real_B, nrow=5, normalize=True)
            fake_A = make_grid(fake_A, nrow=5, normalize=True)
            real_A = real_A.permute(1, 2, 0).cpu().numpy()
            real_A = (real_A * 255).astype(np.uint8)  # Optional: scale to [0, 255]
            fake_A = fake_A.permute(1, 2, 0).cpu().numpy()
            fake_A = (fake_A * 255).astype(np.uint8)
            real_B = real_B.permute(1, 2, 0).cpu().numpy()
            real_B = (real_B * 255).astype(np.uint8)
            # Optional: scale to 
            wandb.log({"generated_images": [wandb.Image(fake_A, caption=f"van gogh paintings Epoch {epoch}"),wandb.Image(real_B, caption=f" real images  Epoch {epoch}"),wandb.Image(real_A, caption=f" real van gogh paintings  Epoch {epoch}")]})
        





