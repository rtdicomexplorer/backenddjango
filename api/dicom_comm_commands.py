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


def get_association(local_scu, remote_scp, roles=[], handlers =[]):
    ae = AE(ae_title=local_scu)
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
    ae = AE(ae_title=local_scu)
    ae.requested_contexts= QueryRetrievePresentationContexts[:]
    req_dataset =dcm.Dataset()
    for key in payload.keys():
        dcm_tag = payload[key]
        req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])

    # #get all patients
    # #d.PatientName = 'P*'
    # d.add_new([0x0010,0x0010],"PN","Pr*")#given filter
    # d.add_new([0x0010,0x0020],"CS",None)
    # d.add_new([0x0010,0x0030],"DA",None)
    # d.add_new([0x0010,0x0040],"CS",None)
    req_dataset.QueryRetrieveLevel = query_retrieve_level
 
    assoc =  ae.associate(addr= remote_scp['host'],port= remote_scp['port'], ae_title=remote_scp['aetitle'])

    if assoc.is_established:
    # Send the C-FIND request
        responses = assoc.send_c_find(req_dataset, StudyRootQueryRetrieveInformationModelFind)
        items_found = []
        for (status, identifier) in responses:
            if status:
                #print('C-FIND query status: 0x{0:04X}'.format( status.Status))
                if status.Status == 0xFF00:#pending
                    item = {}
                    for key in payload.keys():
                        rq_group = int(payload[key]['group'],16)
                        rq_element = int(payload[key]['element'],16)
                        if [rq_group, rq_element] in identifier:
                            item[key]=str(identifier[rq_group,rq_element].value)
                        else:
                             print("Server does not return "+str(key))
                    items_found.append(item)    
            else:
                print('Connection timed out, was aborted or received invalid response')
                return {'message': 'Connection timed out, was aborted or received invalid response'}
                

        # Release the association
        assoc.release()

        print('Elements found', len(items_found))
        return {'message': '', 'response' : items_found}
    else:
        print('Association rejected, aborted or never connected')
        return {'message': 'Association rejected, aborted or never connected'}
       
