import random 
import glob
import os 
from PIL import Image 
from torch.utils.data import Dataset
from torchvision.transforms import transforms 



class ImageDataset(Dataset):
    """
    A custom dataset class for loading and transforming images from two different domains (A and B).

    Args:
        root (str): Root directory where the image folders are located.
        transforms_ (list): A list of torchvision transforms to be applied to the images.
        unaligned (bool, optional): If True, allows loading images from the domains in an unaligned manner. Default is False.
        mode (str, optional): Mode in which the dataset is used, typically 'train' or 'test'. Default is 'train'.

    Attributes:
        transform (Compose): A composition of torchvision transforms to be applied to the images.
        unaligned (bool): Indicates whether to load images in an unaligned manner.
        mode (str): Mode in which the dataset is used ('train' or 'test').
        files_A (list): List of file paths for images in domain A.
        files_B (list): List of file paths for images in domain B.
        len_data (int): Minimum length between files_A and files_B to ensure aligned datasets.

    Methods:
        _load_files(path): Loads and shuffles image file paths from the given directory.
        __getitem__(index): Retrieves and transforms a pair of images (one from each domain) at the specified index.
        _to_rgb(image): Converts an image to RGB mode if it is not already in RGB mode.
        __len__(): Returns the length of the dataset, which is the minimum length of files_A and files_B.
    """
    def __init__(self, root, transforms_=None,unaligned=False, mode='train'):
        self.transform = transforms.Compose(transforms_)
        self.unaligned = unaligned
        self.mode = mode
        self.files_A = self._load_files(os.path.join(root, f"{mode}A"))
        self.files_B = self._load_files(os.path.join(root, f"{mode}B"))
        self.len_data = min(len(self.files_A),len(self.files_B))
        self.files_A = self.files_A[:self.len_data]
        self.files_B = self.files_B[:self.len_data]

    
    def _load_files(self, path):

        files = glob.glob(os.path.join(path, "*.*"), recursive=True)
        random.shuffle(files)
        return files
    
    
    def __getitem__(self, index):
        image_A = Image.open(self.files_A[index % len(self.files_A)])
        image_B = Image.open(self.files_B[index % len(self.files_B)])
        
        if image_A.mode != 'RGB':
            image_A = self._to_rgb(image_A)
        if image_B.mode != 'RGB':
            image_B = self._to_rgb(image_B)
            
        item_A = self.transform(image_A)
        item_B = self.transform(image_B)
        return {'A': item_A, 'B': item_B}
    
    def _to_rgb(self, image):
        return image.convert('RGB')
    
    def __len__(self):
        return self.len_data
    

class EvalImageDataset(Dataset):
        
        """Dataset class for evaluating image data.

        Args:
            root (str): Root directory containing the image files.
            transforms_ (callable, optional): A function/transform to apply to the image data. Default is None.
            singleImg (bool, optional): Indicates if only a single image is used for evaluation. Default is False.

        Attributes:
            files_A (list): List of file paths to the image files.
            singleImg (bool): Indicates if only a single image is used for evaluation.
            root (str): Root directory containing the image files.
            transforms_ (callable): A function/transform to apply to the image data.
    
        """

        
        def __init__(self,root,transforms_=None,singleImg = False):
              super(EvalImageDataset).__init__()
              self.files_A = self._load_files(os.path.join(root))
              self.singleImg =  singleImg
              self.root = root 
              self.transforms_ = transforms_
        def __getitem__(self, index):
                image = Image.open(self.files_A[index % len(self.files_A)]) if self.singleImg == False else  Image.open(self.root)
                
                if image.mode != 'RGB':
                    image = self._to_rgb(image)
                
                item = self.transform(image)
                return  item
        def __len__(self) : 
                 if self.singleImg : 
                       return 1 
                 else : 
                      return len(self.files_A)  