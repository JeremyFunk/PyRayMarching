from abc import ABCMeta, abstractmethod
import numpy as np

# def _gaussian_kernel(l=9, sig=1.):
#     """\
#     creates gaussian kernel with side length `l` and a sigma of `sig`
#     """
#     ax = np.linspace(-(l - 1) / 2., (l - 1) / 2., l)
#     gauss = np.exp(-0.5 * np.square(ax) / np.square(sig))
#     kernel = np.outer(gauss, gauss)
#     kernel = kernel / np.sum(kernel)
#     kernel_color = np.zeros((l, l, 3))

#     for x in range(l):
#         for y in range(l):
#             kernel_color[x,y] = [kernel[x,y], kernel[x,y], kernel[x,y]]
#     print(kernel_color)
#     return kernel_color

# def _blur(image, kernel, average=False):
#     kernel_size = len(kernel)
#     image_row, image_col, color = image.shape
#     kernel_row, kernel_col, kernel_color = kernel.shape
 
#     output = np.zeros(image.shape)
#     pad_height = int((kernel_row - 1) / 2)
#     pad_width = int((kernel_col - 1) / 2)
 
#     padded_image = np.zeros((image_row + (2 * pad_height), image_col + (2 * pad_width), color))

#     padded_image[pad_height:padded_image.shape[0] - pad_height, pad_width:padded_image.shape[1] - pad_width] = image
#     for row in range(image_row):
#         for col in range(image_col):
#             output[row, col] = np.sum(kernel * padded_image[row:row + kernel_row, col:col + kernel_col])
#             if average:
#                 output[row, col] /= kernel.shape[0] * kernel.shape[1]

#     return output


def _blur3x3(data):
    kernel = np.array([[1.0,2.0,1.0], [2.0,4.0,2.0], [1.0,2.0,1.0]])
    kernel = kernel / np.sum(kernel)
    arraylist = []
    for y in range(3):
        temparray = np.copy(data)
        temparray = np.roll(temparray, y - 1, axis=0)
        for x in range(3):
            temparray_X = np.copy(temparray)
            temparray_X = np.roll(temparray_X, x - 1, axis=1)*kernel[y,x]
            arraylist.append(temparray_X)

    arraylist = np.array(arraylist)
    arraylist_sum = np.sum(arraylist, axis=0)
    return arraylist_sum

def _cut_data(data, threshhold):
    new_data = np.copy(data)
    for x in range(len(data)):
        for y in range(len(data[x])):
            col = data[x][y]
            if(col[0] + col[1] + col[2] < threshhold):
                new_data[x][y] = 0
    return new_data

class PostProcessor(metaclass=ABCMeta):
    
    @abstractmethod
    def __init__(self):
        pass
    
    @abstractmethod
    def process_image(self, data):
        pass
    
    @abstractmethod
    def evaluate(self, t):
        pass


class BloomPostProcessor(PostProcessor):
    def __init__(self):
        pass
    
    def process_image(self, data):
        bright = _cut_data(data, .3)
        blur_bright = _blur3x3(_blur3x3(_blur3x3(_blur3x3(bright))))
        
        return np.add(data, blur_bright)

    
    def evaluate(self, t):
        pass