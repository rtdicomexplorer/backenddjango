import logging
import os
from pynetdicom import AE, evt, build_role,debug_logger
from dotenv import load_dotenv
import time
import json 
from django.conf import settings
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

file_list={}
print('file_list')

def __handle_store(event):
    """Handle a C-STORE request event to store in existing folder."""
    store_root = settings.DCM_PATH
    ds = event.dataset
    ds.file_meta = event.file_meta
    store_path =os.path.join(store_root,ds.StudyInstanceUID)
    if not os.path.exists(store_path):
        os.makedirs(store_path)

    store_path =os.path.join(store_path,ds.SeriesInstanceUID)
    if not os.path.exists(store_path):
        os.makedirs(store_path)

    file_name = os.path.join(store_path,ds.SOPInstanceUID + ".dcm")
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(file_name, write_like_original=False)
    __logger.debug(f'file saved: {file_name}')
    # Return a 'Success' status
    file_list [ds.SOPInstanceUID]=file_name
    return 0x0000


def __get_association(local_scu, remote_scp, handlers =[]):
    ae = AE(ae_title=local_scu)
    ae.requested_contexts= QueryRetrievePresentationContexts[:]
    ae.add_requested_context("1.2.840.10008.1.1")
 
    roles =[]
    if len(handlers)>0:
        for c in StoragePresentationContexts :
            if c.abstract_syntax not in _exclusiions:
                ae.add_requested_context(c.abstract_syntax)
                roles.append(build_role(c.abstract_syntax, scp_role=True))
    return ae.associate(
                        addr= remote_scp['host'],
                        port= remote_scp['port'], 
                        ae_title=remote_scp['aetitle'],
                        ext_neg=roles, 
                        evt_handlers=handlers
                        )


def execute_echo (local_scu, remote_scp):
    assoc= __get_association(local_scu, remote_scp)
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

    assoc= __get_association(local_scu, remote_scp)
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
    handlers =[(evt.EVT_C_STORE, __handle_store)]
    st= time.time()
    req_dataset =dcm.Dataset()
    for key in payload.keys():
        dcm_tag = payload[key]
        req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
    req_dataset.QueryRetrieveLevel = query_retrieve_level

    assoc= __get_association(local_scu, remote_scp,handlers=handlers)
    file_list.clear() 

    nr_sub_completed = 0
    nr_sub_remaining = 0 
    nr_sub_warning = 0
    nr_sub_failed = 0

    if assoc.is_established:
        responses = assoc.send_c_get(req_dataset, PatientRootQueryRetrieveInformationModelGet)
    
        for  (status, identifier)  in responses:

            if status:
                print('C-FIND query status: 0x{0:04X}'.format( status.Status))

                if status.Status == 0xFF00:#pending
                    nr_sub_completed = status.NumberOfCompletedSuboperations
                    nr_sub_remaining = status.NumberOfRemainingSuboperations
                    nr_sub_warning = status.NumberOfWarningSuboperations
                    nr_sub_failed = status.NumberOfFailedSuboperations
                    __logger.debug('Nr. of remaining sub operation %s: ',nr_sub_remaining)

                    # yield {'message': '', 'response' : nr_sub_remaining}
            else:
                __logger.debug('Connection timed out, was aborted or received invalid response')
        # Release the association
        assoc.release()

        print(file_list)
        elapsed_time = time.time()-st
        __logger.debug(f"GET Execution time: {elapsed_time} sec  for ")
        __logger.debug("Suboperations completed %s, warning %s, failed %s:", nr_sub_completed, nr_sub_warning, nr_sub_failed)
        return {'message': '', 'response' : nr_sub_completed}

    else:
        __logger.info('Association rejected, aborted or never connected')
        return {'message': 'Association rejected, aborted or never connected'}
       
