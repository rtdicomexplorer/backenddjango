import logging
import os
from pynetdicom import AE, evt, build_role,debug_logger
from dotenv import load_dotenv
import time
import json 
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelGet,
    PatientRootQueryRetrieveInformationModelMove,
    StudyRootQueryRetrieveInformationModelMove, 
    StudyRootQueryRetrieveInformationModelFind,
    RoutineScalpElectroencephalogramWaveformStorage,
    MultichannelRespiratoryWaveformStorage,
    General32bitECGWaveformStorage,
     VLEndoscopicImageStorage												,
     VideoEndoscopicImageStorage                                            ,
     VLMicroscopicImageStorage                                              ,
     VideoMicroscopicImageStorage                                           ,
     VLSlideCoordinatesMicroscopicImageStorage                              ,
     VLPhotographicImageStorage                                             ,
     VideoPhotographicImageStorage                                          ,
     OphthalmicPhotography8BitImageStorage                                  ,
     OphthalmicPhotography16BitImageStorage                                 ,
     StereometricRelationshipStorage                                        ,
     OphthalmicTomographyImageStorage                                       ,
     WideFieldOphthalmicPhotographyStereographicProjectionImageStorage      ,
     WideFieldOphthalmicPhotography3DCoordinatesImageStorage				,
     OphthalmicOpticalCoherenceTomographyEnFaceImageStorage                 ,
     OphthlamicOpticalCoherenceTomographyBscanVolumeAnalysisStorage 
)

from pynetdicom.presentation import StoragePresentationContexts,  QueryRetrievePresentationContexts


import pydicom as dcm

import logging
__logger = logging.getLogger('backenddjango')
#debug_logger()
#dicom support just 128 pres context, we need to remove some these
_exclusiions =[
    RoutineScalpElectroencephalogramWaveformStorage,
    MultichannelRespiratoryWaveformStorage,
    General32bitECGWaveformStorage,
     VLEndoscopicImageStorage												,
     VideoEndoscopicImageStorage                                            ,
     VLMicroscopicImageStorage                                              ,
     VideoMicroscopicImageStorage                                           ,
     VLSlideCoordinatesMicroscopicImageStorage                              ,
     VLPhotographicImageStorage                                             ,
     VideoPhotographicImageStorage                                         ,
     OphthalmicPhotography8BitImageStorage                                  ,
     OphthalmicPhotography16BitImageStorage                                 ,
     StereometricRelationshipStorage                                        ,
     OphthalmicTomographyImageStorage                                       ,
     WideFieldOphthalmicPhotographyStereographicProjectionImageStorage      ,
     WideFieldOphthalmicPhotography3DCoordinatesImageStorage				,
     OphthalmicOpticalCoherenceTomographyEnFaceImageStorage                 ,
     OphthlamicOpticalCoherenceTomographyBscanVolumeAnalysisStorage 
 
    ]

def handle_store(event,DCM_PATH):
    """Handle a C-STORE request event to store in existing folder."""
    
    ds = event.dataset
    ds.file_meta = event.file_meta
    store_path =os.path.join(DCM_PATH,ds.StudyInstanceUID,ds.SeriesInstanceUID)
    file_name = os.path.join(DCM_PATH,ds.SOPInstanceUID + ".dcm")
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(file_name, write_like_original=False)
    print(f'file saved: {file_name}')
    # Return a 'Success' status
    return 0x0000


def get_association(local_scu, remote_scp, req_context=[], roles=[], handlers =[]):
    ae = AE(ae_title=local_scu)
    ae.requested_contexts= req_context[:]
    ae.add_requested_context("1.2.840.10008.1.1")
    return ae.associate(addr= remote_scp['host'],port= remote_scp['port'], ae_title=remote_scp['aetitle'])

def execute_echo (local_scu, remote_scp):
    assoc= get_association(local_scu, remote_scp)
    status_response = False
    message_response = ""
    if assoc.is_established:
        status = assoc.send_c_echo()
        # Check the status of the verification request
        if status:
            # If the verification request succeeded this will be 0x0000
            message_response ='C-ECHO request status: 0x{0:04x}'.format(status.Status)            
            status_response = True
        else:
            message_response = 'Connection timed out, was aborted or received invalid response'
        # Release the association
        assoc.release()
    else:
        if assoc.is_rejected:
            message_response = ('{0}: {1}'.format(
                assoc.acceptor.primitive.result_str,
                assoc.acceptor.primitive.reason_str
            ))
        else:
            message_response = 'Association aborted or never connected'
    
    return {'status':status_response, 'message': message_response}

    
 
def execute_c_find(local_scu, remote_scp, query_retrieve_level,payload):
    st= time.time()
    req_dataset =dcm.Dataset()
    for key in payload.keys():
        dcm_tag = payload[key]
        req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
    req_dataset.QueryRetrieveLevel = query_retrieve_level

    assoc= get_association(local_scu, remote_scp,QueryRetrievePresentationContexts)
    if assoc.is_established:
    # Send the C-FIND request
        responses = assoc.send_c_find(req_dataset, StudyRootQueryRetrieveInformationModelFind)
        items_found = []
        for (status, identifier) in responses:
            if status:
                __logger.debug('C-FIND query status: 0x{0:04X}'.format( status.Status))
                if status.Status == 0xFF00:#pending
                    item = {}
                    for key in payload.keys():
                        rq_group = int(payload[key]['group'],16)
                        rq_element = int(payload[key]['element'],16)
                        if [rq_group, rq_element] in identifier:
                            item[key]=str(identifier[rq_group,rq_element].value)
                        else:
                             __logger.debug("Server does not return %s",key)
                    items_found.append(item)    
            else:
                __logger.debug('Connection timed out, was aborted or received invalid response')
                return {'message': 'Connection timed out, was aborted or received invalid response'}
        # Release the association
        assoc.release()

        elapsed_time = time.time()-st

        __logger.debug('Elements found %s in %s sec', len(items_found), elapsed_time)
        return {'message': '', 'response' : items_found}
    else:
        __logger.info('Association rejected, aborted or never connected')
        return {'message': 'Association rejected, aborted or never connected'}
       


 
def execute_c_get(local_scu, remote_scp, query_retrieve_level,payload):

    roles =[]
    st= time.time()
    req_dataset =dcm.Dataset()
    for key in payload.keys():
        dcm_tag = payload[key]
        req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
    req_dataset.QueryRetrieveLevel = query_retrieve_level

    assoc= get_association(local_scu, remote_scp,QueryRetrievePresentationContexts,roles,[(evt.EVT_C_STORE, handle_store)])
    count = 0
    if assoc.is_established:
        responses = assoc.send_c_get(req_dataset, PatientRootQueryRetrieveInformationModelGet)
        for (status, identifier) in responses:
            count+=1
            if status:
                __logger.debug('C-FIND query status: 0x{0:04X}'.format( status.Status))
            else:
                __logger.debug('Connection timed out, was aborted or received invalid response')
        # Release the association
        assoc.release()
        elapsed_time = time.time()-st
        __logger.debug(f"GET Execution time: {elapsed_time} sec  for {count}")
        return {'message': '', 'response' : count}

    else:
        __logger.info('Association rejected, aborted or never connected')
        return {'message': 'Association rejected, aborted or never connected'}
       
