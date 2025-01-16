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
     VideoPhotographicImageStorage                                          ,
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

    """Returns an association with the PACS"""
    return ae.associate(addr=server['ip'], port= server['port'],ae_title=server['aet'], ext_neg=roles, evt_handlers=handlers )


def execute_echo (local_scu, remote_scp):
    ass = get_association(local_scu, remote_scp)
    return ass
 
def execute_c_find(local_scu, remote_scp, query_retrieve_level,payload):
    ae = AE(ae_title=local_scu)
    ae.requested_contexts= QueryRetrievePresentationContexts[:]
    d =dcm.Dataset()
    for key in payload.keys():
        element = payload[key]
        dcm_group = int(element['group'],16)
        dcm_element = int(element['element'],16)
        vr = element['vr']
        value = element['value']
        d.add_new([dcm_group,dcm_element],vr,value)

    # #get all patients
    # #d.PatientName = 'P*'
    # d.add_new([0x0010,0x0010],"PN","Pr*")#given filter
    # d.add_new([0x0010,0x0020],"CS",None)
    # d.add_new([0x0010,0x0030],"DA",None)
    # d.add_new([0x0010,0x0040],"CS",None)
    d.QueryRetrieveLevel = query_retrieve_level
    items_found = []
    assoc =  ae.associate(addr= remote_scp['host'],port= remote_scp['port'], ae_title=remote_scp['aetitle'])
    count = 0
    if assoc.is_established:
    # Send the C-FIND request
        responses = assoc.send_c_find(d, StudyRootQueryRetrieveInformationModelFind)
        
        for (status, identifier) in responses:
            if status:
                #print('C-FIND query status: 0x{0:04X}'.format( status.Status))
                if status.Status == 0xFF00:#pending
                    count+=1

                    item = {}
                    for key in payload.keys():
                        item[key]=str(identifier[int(payload[key]['group'],16),int(payload[key]['element'],16)].value)
                    items_found.append(item)    
            else:

                print('Connection timed out, was aborted or received invalid response')
                return {'message': 'Connection timed out, was aborted or received invalid response'}
                

        # Release the association
        assoc.release()

        print('Elements found', str(count))
        return {'message': '', 'response' : items_found}
    else:
        print('Association rejected, aborted or never connected')
        return {'message': 'Association rejected, aborted or never connected'}
       
