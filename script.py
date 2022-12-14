#Importing the required modules
from PIL import Image
from matplotlib import image
import numpy as np
import cv2
import itertools
import warnings
import pyqrcode 
import png
from pyqrcode import QRCode 
import matplotlib.pylab as plt
warnings.filterwarnings("ignore")

def encode(image, file_name='compressed_image.txt', bits=15):

    count_list = []
    count = 0
    prev = None
    fimage = image.flatten()
    size = 2**(bits+1) - 2**bits #32768 = 8000H
    
    for pixel in fimage:
        
        if prev == None:
            prev = pixel 
            count += 1
        else:
            if prev != pixel:
                if count >= 3:
                    count_list.append((size+count, [prev]))
                else:
                    if count_list == []:
                        count_list.append((count, [prev]*count))
                    else: 
                        c, color = count_list[-1]
                        if c > size:
                            count_list.append((count, [prev]*count))
                        else:
                            if c+count <= (2**bits)-1:
                                count_list[-1] = (c+count, color+[prev]*count)
                            else:
                                count_list.append((count, [prev]*count))
                prev = pixel
                count = 1
            else:
                if count < (2**bits)-1:
                    count += 1                    
                else:
                    count_list.append((size+count, [prev]))
                    prev = pixel
                    count = 1

    if count >= 3:
        count_list.append((size+count, [prev]))
    else:
        c, color = count_list[-1]
        if c > size:
            count_list.append((count, [prev]*count))
        else:
            if c+count <= (2**bits)-1:
                count_list[-1] = (c+count, color+[prev]*count)
            else:
                count_list.append((count, [prev]*count))

    # Hexa encoding
    with open(file_name,"w") as file:
        hexa_encoded = "".join(map(lambda x: "{0:04x}".format(x[0])+"".join(map(lambda y: "{0:02x}".format(y), x[1])), count_list))
        file.write(hexa_encoded)
        file.close()

    # Compression rate
    rate = (1-(len(hexa_encoded)/2)/len(fimage))*100
    
    return hexa_encoded, rate

def decode(code, bits=15):
    # Loop through the code and get the color of the pixels
    size = 2**(bits+1) - 2**bits 
    i = 0
    data = []

    while i < len(code):
        count = code[i:i+4]
        count = int(count, 16)
        i += 4

        if count > size: # The most significant bit is set to 1
            # Here the color is repeated 3 times or more
            count -= size
            color = code[i:i+2]
            color = int(color, 16)            
            data += [color]*count
            i += 2

        else: # The most significant bit is set to 0
            # Here each color is repeated less than 3 times
            color_seq = code[i:i+count*2]
            colors = [int(color_seq[idx:idx+2], 16) for idx in range(0, len(color_seq), 2)]
            data += colors
            i += count*2

    return data


def QrCodeGeneration(encoded):
    
    # Create and save the png file naming "QRcode.png" 
    # Generate QR code 
    url = pyqrcode.create(encoded) 

    # The second parameter is the scale which represents the size of the QR Code
    QRCode=url.png('QRcode.png', scale = 4)

    # Dispalaying the QR Code
    url.show()
    return url

def QRCodeDecoding():
    # Reading the image QRcode.png that we created before
    #
    # Read the QRCODE image
    img = cv2.imread("QRcode.png")
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(img)
    return data
 

# Read the image 
path='cablecar_2.bmp'
image = Image.open(path)
new_image = image.resize((16,16))
new_image.save('SmallNewImage.png')
img_gray = cv2.imread('SmallNewImage.png', cv2.IMREAD_GRAYSCALE)
_, img_bw = cv2.threshold(img_gray, 100, 255, cv2.THRESH_BINARY)
cv2.imwrite('newImage.png', img_bw)
height, width = img_bw.shape # 512x480 = 245760
encoded, rate = encode(img_bw, file_name='cablecar_compressed.txt', bits=15)
print()
print (f'Compression rate :{rate:.02f}%') # 1- 22927/245760 = 90.67%

# Storage of the code obtained after compression in a QR code:
test= QrCodeGeneration(encoded)
print()

# Read the QR code and get the inserted text:
code=QRCodeDecoding()
print(QRCodeDecoding())

# Generate the corresponding image:
data = decode(code)
image = np.zeros((height, width)).astype(np.uint8)
for k, (i, j) in enumerate(itertools.product(range(height), range(width))):image[i, j] = data[k]
compressed_image = Image.fromarray(image, mode='L')
compressed_image.show()
compressed_image.save('decompressed.png')

# This has to be equal to 0
error_rate = np.count_nonzero(image - img_bw)
print()
print (f'Error Rate: {error_rate}') 
print()