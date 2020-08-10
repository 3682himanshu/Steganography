import cv2
import os
import sys
import numpy as np
HEADER_FILENAME_LENGTH= 30
HEADER_FILESIZE_LENGTH= 20
HEADER_LENGTH= HEADER_FILENAME_LENGTH+HEADER_FILESIZE_LENGTH

getBits= lambda n:[n>>5,(n&0x1C)>>2,n&0x3]
l=getBits(104)

getByte= lambda  bits:((bits[0]<<5)|(bits[1]<<2)|(bits[2]))

def get_file_size(filename):
    try:
        return os.stat(filename).st_size
    except:
        return 0
def generate_header(filename):
    qty=get_file_size(filename)
    if qty==0:
        return None
    # compose header for fileName
    # fileName: 'd:/images/work.jpg
    # splitted: [d:, images, work.jpg]

    name = filename.split('/')[-1]
    name_extension=name.split('.')
    ext_len=len(name_extension[1])+1
    name_len=HEADER_FILENAME_LENGTH-ext_len
    name=name_extension[0][:name_len]+'.'+name_extension[1]
    # adds padding to the right of string to make its length equal to header_filename_length
    name=name.ljust(HEADER_FILENAME_LENGTH,"*")

    qty=str(qty).ljust(HEADER_FILESIZE_LENGTH,"*")
    return name+qty

def embed(resultant_img,source_img,file_to_embed):
    # load the image as numpy.ndarray
    image=cv2.imread(source_img,1)
    if image is None:
        print(source_img,"not found")
        return
    # check the file to embed
    fs=get_file_size(file_to_embed)
    if fs==0:
        print(file_to_embed,'not found')
        return

    h,w,_=image.shape

    # capacity check
    if h*w<fs+HEADER_LENGTH:
        print("Insufficient Embedding Capacity")
        return
    print("size of one dimension of image in bytes", sys.getsizeof(image[0, 0, 0]))
    print("Shape of image wrt to ndarray", image.shape)
    print('max value of pixel in image = ', np.max(image), 'min value of pixel in image = ', np.min(image))

    # embed
    # order : header, file
    header=generate_header(file_to_embed)
    fh=open(file_to_embed,'rb')
    i=0
    cnt=0
    data=0

    keepEmbeeding=True
    while i<h and keepEmbeeding:
        j=0
        while j<w:
            # get the data
            if cnt<HEADER_LENGTH:#either from header
                data=ord(header[cnt])
            else:#or from file
                data=fh.read(1)#read one byte from the file
                if data:
                    # as the file is opened in binary mode
                    # so we get byte objects on read
                    # the byte object dont support bitwise operations
                    # hence they are to be converted to int
                    data=int.from_bytes(data,byteorder='big')
                else:#EOF
                    keepEmbeeding=False
                    break
            bits=getBits(data)
            image[i,j,2]=((image[i,j,2]&(~0x7))|bits[0])#embed in red band
            image[i,j,1]=((image[i,j,1]&(~0x7))|bits[1])#embed in green band
            image[i,j,0]=((image[i,j,0]&(~0x3))|bits[2])#embed in blue band
            cnt+=1
            j+=1
        i+=1
    # close the file
    fh.close()
    # save back the image
    cv2.imwrite(resultant_img,image)
    print("Embeeding Done")
def extract(resultant_img,target_folder):
    # load the image as numpy.ndarray
    image=cv2.imread(resultant_img,1)
    if image is None:
        print(resultant_img,"not found")
        return
    h,w,_=image.shape
    # extract
    # order : header, file
    header=''
    fh=None
    i=0
    cnt=0
    keepExtracting=True
    while i<h and keepExtracting:
        j=0
        while j<w:#get the data
            bit1=image[i,j,2]&0x7# extract from red band
            bit2=image[i,j,1]&0x7 # extract from green band
            bit3=image[i,j,0]&0x3# extract from blue band

            data=getByte([bit1,bit2,bit3])
            # put the data
            if cnt<HEADER_LENGTH:#either into header
                header=header+chr(data)
            else:#or into file
                if cnt==HEADER_LENGTH:
                    filename=target_folder+'/'+header[:HEADER_FILENAME_LENGTH].strip("*")
                    filesize=int(header[HEADER_FILENAME_LENGTH:].strip('*'))+cnt
                    fh=open(filename,'wb')
                if cnt<filesize:
                    data=int.to_bytes(int(data),1,byteorder='big')
                    fh.write(data)
                else:
                    fh.close()
                    keepExtracting=False
                    break
            cnt+=1
            j+=1
        i+=1
    print('Extracting Done')

#start here
embed("F:/Project_Data/res.png","F:/Project_Data/shivji.jpg","F:/Project_Data/fav.txt")


extract('F:/Project_Data/res.png',"f:")