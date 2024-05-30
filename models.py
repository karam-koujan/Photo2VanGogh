import torch.nn as nn 




class ResidualBlock(nn.Module):
    """
    A ResidualBlock class implementing a residual block commonly used in ResNet architectures.

    Attributes:
    -----------
    block : nn.Sequential
        A sequential container holding the layers of the residual block. This block consists of:
        - Reflection padding
        - 2D Convolution
        - Instance normalization
        - ReLU activation
        - Reflection padding
        - 2D Convolution
        - Instance normalization

    Methods:
    --------
    forward(x):
        Defines the forward pass of the residual block. Adds the input tensor to the output of the block.
    """
    def __init__(self, in_features):
        super(ResidualBlock, self).__init__()
        
        self.block = nn.Sequential(
            nn.ReflectionPad2d(1),
            nn.Conv2d(in_features, in_features, 3),
            nn.InstanceNorm2d(in_features), 
            nn.ReLU(inplace=True),
            nn.ReflectionPad2d(1),
            nn.Conv2d(in_features, in_features, 3),
            nn.InstanceNorm2d(in_features)
        )

    def forward(self, x):
        return x + self.block(x)


class GeneratorResNet(nn.Module):
    """
    A GeneratorResNet class implementing a generator model based on the ResNet architecture, commonly used in GANs for image-to-image translation tasks.

    Attributes:
    -----------
    model : nn.Sequential
        A sequential container holding the layers of the generator model. This includes:
        - Initial convolutional block
        - Downsampling layers
        - Multiple residual blocks
        - Upsampling layers
        - Final convolutional block

    Methods:
    --------
    forward(x):
        Defines the forward pass of the generator model.
    """
    def __init__(self, input_shape, num_residual_block):
        super(GeneratorResNet, self).__init__()
        
        channels = input_shape[0]
        
        out_features = 64
        model = [
            nn.ReflectionPad2d(channels),
            nn.Conv2d(channels, out_features, 7),
            nn.InstanceNorm2d(out_features),
            nn.ReLU(inplace=True)
        ]
        in_features = out_features
        
        for _ in range(2):
            out_features *= 2
            model += [
                nn.Conv2d(in_features, out_features, 3, stride=2, padding=1),
                nn.InstanceNorm2d(out_features),
                nn.ReLU(inplace=True)
            ]
            in_features = out_features
        
        # Residual blocks
        for _ in range(num_residual_block):
            model += [ResidualBlock(out_features)]
            
        
        for _ in range(2):
            out_features //= 2
            model += [
                nn.Upsample(scale_factor=2), 
                nn.Conv2d(in_features, out_features, 3, stride=1, padding=1),
                nn.ReLU(inplace=True)
            ]
            in_features = out_features
            
        model += [nn.ReflectionPad2d(channels),
                  nn.Conv2d(out_features, channels, 7),
                  nn.Tanh()
                 ]
        
        # Unpacking
        self.model = nn.Sequential(*model) 
        
    def forward(self, x):
        return self.model(x)
    

class Discriminator(nn.Module):
    """
    A Discriminator class implementing a discriminator model for GANs, designed to distinguish between real and fake images.

    Attributes:
    -----------
    output_shape : tuple
        The shape of the output tensor, typically (1, height//2**4, width//2**4).
    model : nn.Sequential
        A sequential container holding the layers of the discriminator model. This includes:
        - Several discriminator blocks
        - A final convolutional layer

    Methods:
    --------
    forward(img):
        Defines the forward pass of the discriminator model.
    """
    def __init__(self, input_shape):
        super(Discriminator, self).__init__()
        
        channels, height, width = input_shape
        
        self.output_shape = (1, height//2**4, width//2**4)
        
        def discriminator_block(in_filters, out_filters, normalize=True):
            layers = [nn.Conv2d(in_filters, out_filters, 4, stride=2, padding=1)]
            if normalize:
                layers.append(nn.InstanceNorm2d(out_filters))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers
        
        self.model = nn.Sequential(
            *discriminator_block(channels, 64, normalize=False),
            *discriminator_block(64, 128),
            *discriminator_block(128,256),
            *discriminator_block(256,512),
            nn.ZeroPad2d((1,0,1,0)),
            nn.Conv2d(512, 1, 4, padding=1)
        )
        
    def forward(self, img):
        return self.model(img)
