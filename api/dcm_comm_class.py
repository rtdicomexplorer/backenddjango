import logging
import os
from pynetdicom import AE, evt, build_role,debug_logger
import time
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

from pynetdicom.presentation import StoragePresentationContexts,  QueryRetrievePresentationContexts
from .serializers import DicomServerSerializers
import pydicom as dcm
logger = logging.getLogger('backenddjango')

class DcmCommunication:
    '''Defines an object that execites the dciom command'''

    def __init__(self):
        self.get_file_list = []
    
    def __handle_store(self,event):

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

        file_name = ds.SOPInstanceUID + ".dcm"
        file_path_name = os.path.join(store_path,file_name)
        # Save the dataset using the SOP Instance UID as the filename
        ds.save_as(file_path_name, write_like_original=False)
        logger.debug(f'file saved: {file_path_name}')
        # Return a 'Success' status
        self.get_file_list.append(file_name)
        return 0x0000

    def __get_association(self,local_scu, remote_scp, handlers =[]):
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
    
    def execute_echo (self,request):

        try:
            servserializer = DicomServerSerializers(data=request.data)
            remote_scp = servserializer.initial_data
            local_ae = settings.LOCAL_AET

            logger.debug('Echo request to : %s %s:%s',remote_scp['aetitle'],remote_scp['host'],remote_scp['port']) 
            assoc= self.__get_association(local_ae, remote_scp)
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


        except Exception as e:
            logger.exception('An error occurred: %s', e)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)
    
    def execute_c_find(self,request):

        try:    
        
            dcm_server = request.data['remotescp']
            query_retrieve_level=request.data['queryretrievelevel']
            payload = request.data['payload']
            servserializer = DicomServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            local_ae = settings.LOCAL_AET
            logger.debug('Find request %s to : %s %s:%s',query_retrieve_level, remote_scp['aetitle'],remote_scp['host'],remote_scp['port']) 
            st= time.time()
            req_dataset =dcm.Dataset()
            for key in payload.keys():
                dcm_tag = payload[key]
                req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
            req_dataset.QueryRetrieveLevel = query_retrieve_level

            assoc= self.__get_association(local_ae, remote_scp)
            if assoc.is_established:
            # Send the C-FIND request
                responses = assoc.send_c_find(req_dataset, StudyRootQueryRetrieveInformationModelFind)
                items_found = []
                for (status, identifier) in responses:
                    if status:
                        logger.debug('C-FIND query status: 0x{0:04X}'.format( status.Status))
                        if status.Status == 0xFF00:#pending
                            item = {}
                            for key in payload.keys():
                                rq_group = int(payload[key]['group'],16)
                                rq_element = int(payload[key]['element'],16)
                                if [rq_group, rq_element] in identifier:
                                    item[key]=str(identifier[rq_group,rq_element].value)
                                else:
                                    logger.debug("Server does not return %s",key)
                            items_found.append(item)    
                    else:
                        logger.debug('Connection timed out, was aborted or received invalid response')
                        return {'message': 'Connection timed out, was aborted or received invalid response'}
                # Release the association
                assoc.release()

                elapsed_time = time.time()-st

                logger.debug('Elements found %s in %s sec', len(items_found), elapsed_time)
                return {'message': '', 'response' : items_found}
            else:
                logger.info('Association rejected, aborted or never connected')
                return {'message': 'Association rejected, aborted or never connected'}
        except Exception as e:
            logger.exception('An error occurred: %s', e)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)

    def execute_c_get(self,request):
        try:

            dcm_server = request.data['remotescp']
            query_retrieve_level=request.data['queryretrievelevel']
            payload = request.data['payload']
            servserializer = DicomServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            local_ae = settings.LOCAL_AET


            handlers =[(evt.EVT_C_STORE, self.__handle_store)]
            st= time.time()
            req_dataset =dcm.Dataset()
            for key in payload.keys():
                dcm_tag = payload[key]
                req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
            req_dataset.QueryRetrieveLevel = query_retrieve_level

            assoc= self.__get_association(local_ae, remote_scp,handlers=handlers)
            self.get_file_list.clear() 

            nr_sub_completed = 0
            nr_sub_remaining = 0 
            nr_sub_warning = 0
            nr_sub_failed = 0

            if assoc.is_established:
                responses = assoc.send_c_get(req_dataset, PatientRootQueryRetrieveInformationModelGet)
            
                for  (status, identifier)  in responses:

                    if status:
                        print('C-GET query status: 0x{0:04X}'.format( status.Status))

                        if status.Status == 0xFF00:#pending
                            nr_sub_completed = status.NumberOfCompletedSuboperations
                            nr_sub_remaining = status.NumberOfRemainingSuboperations
                            nr_sub_warning = status.NumberOfWarningSuboperations
                            nr_sub_failed = status.NumberOfFailedSuboperations
                            logger.debug('Nr. of remaining sub operation %s: ',nr_sub_remaining)

                            # yield {'message': '', 'response' : nr_sub_remaining}
                    else:
                        logger.debug('Connection timed out, was aborted or received invalid response')
                # Release the association
                assoc.release()
                elapsed_time = time.time()-st
                logger.debug(f"GET Execution time: {elapsed_time} sec  for ")
                logger.debug("Suboperations completed %s, warning %s, failed %s:", nr_sub_completed, nr_sub_warning, nr_sub_failed)
                return {'message': '', 'response' : self.get_file_list}

            else:
                logger.info('Association rejected, aborted or never connected')
                return {'message': 'Association rejected, aborted or never connected'}
        except Exception as e:
            logger.exception('An error occurred: %s', e)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)