import uuid
from typing import List
from fhir.resources.R4B.bundle import Bundle, BundleEntry, BundleEntryRequest
from fhir.resources.R4B.resource import Resource

from .dicom2fhir import dicom2fhir
import requests
import time
# wrapper function to process study
def process_study(root_path, include_instances, build_bundle, output_path, create_device,save_json_file, fhir_server = None):

    result_resource, study_instance_uid, accession_nr, dev_list, patient = dicom2fhir.process_dicom_2_fhir(
        str(root_path), include_instances
    )


    study_id = accession_nr
    if accession_nr is None:
        study_id = str(study_instance_uid)
        if study_instance_uid is None:
            raise ValueError(
                "No suitable ID in DICOM file available to set the identifier")



    # build imagingstudy bundle
    if build_bundle:
        result_list = []
        result_list.append(result_resource)
        result_list.append(patient)
        devs = [x[0] for x in dev_list]
        result_list = result_list + devs
        result_bundle = build_from_resources(result_list, study_instance_uid)
        # need to sent to FHIR
        if fhir_server is not None:


          
            response = requests.post(url=f'{fhir_server}',
                          data=  result_bundle.json(),              
                           headers= {
                    "Content-type": "application/fhir+json",
                }, verify=False)

            print(response)
            # session = requests.Session()
            # response = session.post(
            #     fhir_server,
            #     result_bundle.json() ,
            #     headers={
            #         "Content-type": "application/fhir+json",
            #     }
            # )
                # now we extract the patient_id that was returned to us
            response.raise_for_status()
            time.sleep(1)


        if save_json_file == True:
            try:
                jsonfile = output_path + str(study_id) + "_bundle.json"
                with open(jsonfile, "w+") as outfile:
                    outfile.write(result_bundle.json())
            except Exception:
                print("Unable to create ImagingStudy JSON-file (probably missing identifier)")
    else:
        if save_json_file == True:
            try:
                jsonfile = output_path + str(id) + "_imagingStudy.json"
                with open(jsonfile, "w+") as outfile:
                    outfile.write(result_resource.json())
            except Exception:
                print("Unable to create ImagingStudy JSON-file (probably missing identifier)")
    #build device
    if create_device and save_json_file == True:
        for dev in dev_list:
            dev_id = dev[1]
            dev_resource = dev[0]
            try:
                jsonfile = output_path + "Device_" + str(dev_id) + ".json"
                with open(jsonfile, "w+") as outfile:
                    outfile.write(dev_resource.json())
            except Exception:
                print("Unable to create device JSON-file")

# build FHIR bundle from resource
def build_from_resources(resources: List[Resource], id: str | None) -> Bundle:
    bundle_id = id
    if bundle_id is None:
        bundle_id = str(uuid.uuid4())

    bundle = Bundle(**{"id": bundle_id, "type": "transaction", "entry": []})

    for resource in resources:
        request = BundleEntryRequest(
            **{"url": f"{resource.resource_type}/{resource.id}", "method": "PUT"}
        )
        entry = BundleEntry.construct()
        entry.request = request
        entry.fullUrl = request.url
        entry.resource = resource
        bundle.entry.append(entry)

    return bundle
