import logging
import os
from dotenv import load_dotenv

from django.conf import settings

import pydicom as dcm
from pydicom import config
config.settings.reading_validation_mode = config.IGNORE
import logging
from PIL import Image
import numpy as np  
import base64
from io import BytesIO
import shutil

__logger = logging.getLogger('backenddjango')

def get_binaryimage(request):

    try:
        payload = request.data['payload']
        studyuid = payload['studyuid']
        serieyuid = payload['serieuid']
        instanceuid = payload['instanceuid']
        store_root = settings.DCM_PATH
        file_name = os.path.join(store_root,studyuid,serieyuid,instanceuid)
        if os.path.isfile(file_name):
            return open(file_name, 'rb')
        else:
            raise  Exception('File not  %s found',file_name)
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        raise  Exception(e)

    

def get_base64image(request):
    try:
        payload = request.data['payload']
        studyuid = payload['studyuid']
        serieyuid = payload['serieuid']
        instanceuid = payload['instanceuid']
        store_root = settings.DCM_PATH
        sessionkey = None
        dicom_folder = store_root
        if 'sessionkey' in payload: 
            sessionkey = payload['sessionkey']
            dicom_folder =os.path.join(store_root,sessionkey) 
        dicom_folder =os.path.join(dicom_folder,studyuid)
        file_name = os.path.join(dicom_folder,instanceuid)
        ds = dcm.dcmread(file_name)
        if 'PixelData' in ds:
            image_array = ds.pixel_array
            
            # If the image is 3D, take the middle slice
            if image_array.ndim == 3:
                middle_slice_index = image_array.shape[0] // 2
                image_array = image_array[middle_slice_index]
            # Normalize pixel values to 0-255
            image_array = ((image_array - image_array.min()) / (image_array.max() - image_array.min())) * 255.0
            image_array = image_array.astype(np.uint8)
            
            # Create PIL Image object from numpy array
            image = Image.fromarray(image_array, 'L')
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            os.remove(file_name)
            if(len(os.listdir(dicom_folder)) == 0):
                 shutil.rmtree(dicom_folder)

            return  base64.b64encode(buffered.getvalue()).decode('utf-8')
        else:
            raise  ''
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        if os.path.exists(file_name):
            shutil.rmtree(file_name)

        raise  Exception(e)

 


def get_dcm_filelist(request):
    try:
        sessionkey = None
        payload = request.data['payload']
        studyuid = payload['studyuid']
        serieyuid = payload['serieuid']
        if sessionkey in payload: 
            sessionkey = payload['sessionkey']
        store_root =  os.path.join(settings.DCM_PATH,studyuid,serieyuid)
        files = os.listdir(store_root)
        files = [f for f in files if os.path.isfile(store_root+'/'+f)] #Filtering only the files.
        return files
    except Exception as e:
        __logger.exception('An error occurred: %s', e)
        raise  Exception(e)