import logging
import os
from pynetdicom import AE, evt, build_role,debug_logger
from django.core.files.storage import FileSystemStorage  
import time
from django.conf import settings
from  api.launch_dicom2fhir import process_study
import base64
from pynetdicom.sop_class import (
    PatientRootQueryRetrieveInformationModelFind,
    PatientRootQueryRetrieveInformationModelGet,
    StudyRootQueryRetrieveInformationModelGet,
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

from api.models import LocalConfig

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
from .serializers import DicomServerSerializers, LocalConfigSerializers
import pydicom as dcm
logger = logging.getLogger('backenddjango')

def get_local_aetitle():
        configs = LocalConfig.objects.values()
        serializer = LocalConfigSerializers(configs, many = True)
        return serializer.instance[0]['aetitle']

class DcmCommunication:
    '''Defines an object that execites the dciom command'''

    def __init__(self):
        self.get_file_list = []

        self.local_aetitle = get_local_aetitle()
    
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

    def __get_association(self,local_scu, remote_scp,store_scu, handlers =[]):
        ae = AE(ae_title=local_scu)
        roles =[]
        if store_scu :
            ae.requested_contexts = StoragePresentationContexts
        else:
            ae.requested_contexts= QueryRetrievePresentationContexts[:]
            ae.add_requested_context("1.2.840.10008.1.1")
         
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
          
            logger.debug('Echo request to : %s %s:%s',remote_scp['aetitle'],remote_scp['host'],remote_scp['port']) 
            assoc= self.__get_association(self.local_aetitle, remote_scp, False)
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
            value_error =  f'An error occurred: {e.args[0]}'
            logger.exception(value_error)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)
    
    def execute_c_find(self,request):

        try:    
        
            dcm_server = request.data['remotescp']
            query_retrieve_level=request.data['queryretrievelevel']
            payload = request.data['payload']
            servserializer = DicomServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            logger.debug('Find request %s to : %s %s:%s',query_retrieve_level, remote_scp['aetitle'],remote_scp['host'],remote_scp['port']) 
            st= time.time()
            req_dataset =dcm.Dataset()
            for key in payload.keys():
                dcm_tag = payload[key]
                req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
            req_dataset.QueryRetrieveLevel = query_retrieve_level

            assoc= self.__get_association(self.local_aetitle, remote_scp, False)
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
            value_error =  f'An error occurred: {e.args[0]}'
            logger.exception(value_error)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)

    def execute_c_get(self,request):
        try:

            dcm_server = request.data['remotescp']
            query_retrieve_level=request.data['queryretrievelevel']
            payload = request.data['payload']
            servserializer = DicomServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            handlers =[(evt.EVT_C_STORE, self.__handle_store)]
            st= time.time()
            req_dataset =dcm.Dataset()
            for key in payload.keys():
                dcm_tag = payload[key]
                req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
            req_dataset.QueryRetrieveLevel = query_retrieve_level

            assoc= self.__get_association(self.local_aetitle, remote_scp,False, handlers=handlers)
            self.get_file_list.clear() 

            nr_sub_completed = 0
            nr_sub_remaining = 0 
            nr_sub_warning = 0
            nr_sub_failed = 0

            if assoc.is_established:
                responses = assoc.send_c_get(req_dataset, StudyRootQueryRetrieveInformationModelGet)
            
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
            value_error =  f'An error occurred: {e.args[0]}'
            logger.exception(value_error)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)



    def __handle_uploaded_file_to_store(self,file,file_name, remote_scp, store_path):
  
        response = { 'status':True, 'message':'', 'filename':file_name}
        try:
            # store_root = settings.DCM_PATH
            # store_path =os.path.join(store_root,'temp')
            if not os.path.exists(store_path):
                os.makedirs(store_path)
                
            FileSystemStorage(location=store_path).save(file_name, file)
            file_path = os.path.join(store_path,file_name)          
            assoc= self.__get_association(self.local_aetitle, remote_scp, True)
            ds = dcm.dcmread(file_path)
            if assoc.is_established:
                # Use the C-STORE service to send the dataset
                # returns the response status as a pydicom Dataset
                status = assoc.send_c_store(ds)

                # Check the status of the storage request
                if status:
                    # If the storage request succeeded this will be 0x0000
                    logger.debug ('C-STORE request status: 0x{0:04x}'.format(status.Status))
                else:
                    logger.debug('Connection timed out, was aborted or received invalid response')
                    response['status']= False
                    response['message']= 'Connection timed out, was aborted or received invalid response'

                # Release the association
                assoc.release()
            else:
                logger.debug('Association rejected, aborted or never connected')
                response['status']= False
                response['message']= 'Association rejected, aborted or never connected'
            return response
        except Exception as e:       
            value_error =  f'An error occurred: {e.args[0]}'
            logger.exception(value_error)       
            response['status']= False
            response['message']= value_error
            
            
        finally:
            # if os.path.exists(file_path):
            #     os.remove(file_path)
            return response



    def __send_fhir(self, file_path, fhir_server):
        response = False
        try:                
            print('################### STARTING SEND TO FHIR #################')
            process_study(root_path=file_path,include_instances=True,  build_bundle=True, output_path= '',create_device=True ,save_json_file= False,fhir_server= fhir_server)
            response = True
        except Exception as e:
            value_error =  f'An error occurred by send to fhir: {e.args[0]}'

            logger.exception(value_error)       
            print(value_error)
        finally:
            return response



    def execute_c_store(self,request):
        try:
            print(f'📝current session_key {request.session._session_key}')
            store_path = os.path.join(settings.DCM_PATH,'temp', request.session._session_key) 
            #self.__delete_path(file_path)
            fhir_server = None
            response = []
            resp = {}
            key ='file'
            if key in request.FILES:
                files = request.FILES.getlist(key)
                for file in files:
                    try:
                        remote_scp_data = file.name.split(';')
                        remote_scp = {}
                        remote_scp['aetitle'] = remote_scp_data[0]
                        remote_scp['port'] = int(remote_scp_data[1])
                        remote_scp['host']= remote_scp_data[2]

                        if (len(remote_scp_data)>4):
                            file_name = remote_scp_data[4]
                            fhir_server = base64.b64decode(remote_scp_data[3]).decode("utf-8")   
                        else:
                            file_name = remote_scp_data[3]
                        result = self.__handle_uploaded_file_to_store(file,file_name,remote_scp, store_path)
                        response.append(result)
                    except Exception as e:
                        value_error =  f'An error occurred by c-store: {e.args[0]}'
                        logger.exception(value_error)

                if fhir_server is not None:
                    fhir_sent = self.__send_fhir(store_path, fhir_server)
                    
                    resp['fhir']= fhir_sent
                    print(f'Sent to fhir server {fhir_server} was {fhir_sent}')

                self.__delete_path(store_path)

            resp['message']= ''
            resp['response'] = response   
            return resp

        except Exception as e:
  
            self.__delete_path(store_path)
            value_error =  f'An error occurred by c-store: {e.args[0]}'
            logger.exception(value_error)
            raise  Exception(e)
        

    def __delete_path(self,path):
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                os.remove(  os.path.join(path,file))


   

    def execute_c_move(self,request):

        try:    
            html_response ={}
            dcm_server = request.data['remotescp']
            query_retrieve_level=request.data['queryretrievelevel']
            payload = request.data['payload']
            destination_aetitle = request.data['destinationaetitle']
            servserializer = DicomServerSerializers(data=dcm_server)
            remote_scp = servserializer.initial_data      
            logger.debug('Find request %s to : %s %s:%s',query_retrieve_level, remote_scp['aetitle'],remote_scp['host'],remote_scp['port']) 
            st= time.time()
            req_dataset =dcm.Dataset()
            for key in payload.keys():
                dcm_tag = payload[key]
                req_dataset.add_new([int(dcm_tag['group'],16),int(dcm_tag['element'],16)],dcm_tag['vr'],dcm_tag['value'])
            req_dataset.QueryRetrieveLevel = query_retrieve_level

            assoc= self.__get_association(self.local_aetitle, remote_scp, False)
            if assoc.is_established:
            # Send the C-MOVE request

                responses = assoc.send_c_move(req_dataset, destination_aetitle, StudyRootQueryRetrieveInformationModelMove)
                # count = 0
                nr_completed_sub_operation = 0
                nr_failed_sub_operation = 0
                nr_warning_sub_operation = 0
                move_completed = True
                for (status, identifier) in responses:
                  
                    if status and status.Status in [0xFF00, 0xFF01]:
                        # count +=1
                        # `identifier` is a pydicom Dataset containing a query
                        
                        # print('C-MOVE query status: 0x{0:04X}'.format( status.Status))
                        nr_completed_sub_operation = status.NumberOfCompletedSuboperations
                        nr_warning_sub_operation = status.NumberOfWarningSuboperations
                        nr_failed_sub_operation = status.NumberOfFailedSuboperations                 
                        msg = f"Suboperations {status.NumberOfRemainingSuboperations}/{status.NumberOfCompletedSuboperations}"
                        print(msg)
                        logger.debug('C-MOVE query status: 0x{0:04X}'.format( status.Status)) 

                    else:
                        logger.debug('Connection timed out, was aborted or received invalid response')
                        move_completed =  status.Status == 0x0000
                    
                    # html_response.append('C-MOVE query status: 0x{0:04X}'.format( status.Status))
                # Release the association
                assoc.release()

                if move_completed:
                    msg = f"Nr. of completed sub operations {status.NumberOfCompletedSuboperations}"
                    logger.debug(f'C-MOVE {msg}') 

                    msg = f"Nr. of warning sub operations {status.NumberOfWarningSuboperations}"
                    logger.debug(f'C-MOVE {msg}') 
                    
                    msg = f"Nr. of failed sub operations {status.NumberOfFailedSuboperations}"
                    logger.debug(f'C-MOVE {msg}') 

                    html_response["Nr. completed sub operation"] = nr_completed_sub_operation
                    html_response["Nr. failed sub operation"] = nr_failed_sub_operation
                    html_response["Nr. warning sub operation"] = nr_warning_sub_operation
                

                    elapsed_time = time.time()-st

                    logger.debug('C-MOVE Completed in %s sec', elapsed_time)
                
                    return {'message': '', 'response' : html_response}
                else:
                    return {'message': 'Connection timed out, was aborted or received invalid response'}

            else:
                logger.info('Association rejected, aborted or never connected')
                return {'message': 'Association rejected, aborted or never connected'}
        except Exception as e:
            logger.exception('An error occurred: %s', e)
            error = str(list(servserializer.errors.values())[0][0])
            raise  Exception(error)