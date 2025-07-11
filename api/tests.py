from django.test import TestCase
import os
import pandas as pd

viewPosision_MG_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4014.html"
viewPosision_DX_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4010.html"
RADIONUCLEIDE_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_18.html"
RADIOPHARMACEUTICAL_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4021.html"
radionuclide_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/sect_CID_4020.html"
BODYSITE_SNOMED_MAPPING_URL = "https://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_L.html"


def _get_snomed_bodysite_mapping(url=BODYSITE_SNOMED_MAPPING_URL, name="BODYSITE_SNOMED_MAPPING_URL.json"):
    try:

        df = pd.read_html(url, converters={
            "Code Value": str
        })

      
        # required columns
        req_cols = ["Code Value", "Code Meaning", "Body Part Examined"]

        mapping = df[2][req_cols]
        
        # remove empty values:
        mapping = mapping[~mapping['Body Part Examined'].isnull()]
        mapping.to_json(name,orient="records", indent=2)
        return name
    except Exception as e:
        value_error = f'Error when try to connect to {url} : {e.args[0]}'
        print(value_error)

def _get_snomed_mapping_MG(url=viewPosision_MG_SNOMED_MAPPING_URL,name="viewPosision_MG_SNOMED_MAPPING_URL.json"):
    try:

        df = pd.read_html(url, converters={
            "Code Value": str,
            "ACR MQCM 1999 Equivalent": str,
            "Code Meaning": str
        })


        df[2].to_json(name,orient="records", indent=2)
        # required columns
        req_cols = ["Code Value", "Code Meaning", "ACR MQCM 1999 Equivalent"]

        mapping = df[2][req_cols]

        # remove empty values:
        mapping = mapping[~mapping['Code Value'].isnull()]
        mapping.to_json(name,orient="records", indent=2)

        return name
    except Exception as e:
        value_error = f'Error when try to connect to {url} : {e.args[0]}'
        print(value_error)

def _get_snomed_mapping_DX(url=viewPosision_DX_SNOMED_MAPPING_URL,name="viewPosision_DX_SNOMED_MAPPING_URL.json"):
    try:

        df = pd.read_html(url, converters={
            "Code Value": str,
            "Code Meaning": str
        })
        # required columns
        req_cols = ["Code Value", "Code Meaning"]
        mapping = df[2][req_cols]

        # remove empty values:
        mapping = mapping[~mapping['Code Value'].isnull()]
        mapping.to_json(name,orient="records", indent=2)

        return name
    except Exception as e:
        value_error = f'Error when try to connect to {url} : {e.args[0]}'
        print(value_error)

def _get_snomed_mapping_NM(url=RADIONUCLEIDE_SNOMED_MAPPING_URL,name="RADIONUCLEIDE_SNOMED_MAPPING_URL.json"):
    try:

        df = pd.read_html(url, converters={
            "Code Value": str,
            "SNOMED-RT ID": str
        })

        # required columns
        req_cols = ["Code Value", "Code Meaning", "SNOMED-RT ID"]

        df[2].to_json(name,orient="records", indent=2)
        mapping = df[2][req_cols]


        # remove empty values:
        mapping = mapping[~mapping['Code Value'].isnull()]
        mapping.to_json(name,orient="records", indent=2)

        return name
    except Exception as e:
        value_error = f'Error when try to connect to {url} : {e.args[0]}'
        print(value_error)


def _get_snomed_mapping_PT(url, name,):
    try:
       
        df = pd.read_html(url, converters={
            "Code Value": str,
            "Code Meaning": str,
            "SNOMED-RT ID": str
        })
        # required columns
        req_cols = ["Code Value", "Code Meaning", "SNOMED-RT ID"]

        mapping = df[2][req_cols]
        mapping.to_json(name,orient="records", indent=2)
        return name
    except Exception as e:
        value_error = f'Error when try to connect to {url} : {e.args[0]}'
        print(value_error)


def get_html_table_to_json():
    body_site_file_name =  _get_snomed_bodysite_mapping()
    print(body_site_file_name)

    mapping =pd.read_json(body_site_file_name, orient="records")

    _get_snomed('ABDOMEN',mapping)
    print(_get_snomed_mapping_DX())
    print(_get_snomed_mapping_MG())
    print(_get_snomed_mapping_NM())
    print(_get_snomed_mapping_PT(RADIOPHARMACEUTICAL_SNOMED_MAPPING_URL,'RADIOPHARMACEUTICAL_SNOMED_MAPPING_URL.json'))
    print(_get_snomed_mapping_PT(radionuclide_SNOMED_MAPPING_URL,'radionuclide_SNOMED_MAPPING_URL.json'))
    


def load_mappingtable(local_path):
    if os.path.exists(local_path):
        # df = pd.read_pickle(local_path)  # or pd.read_csv(local_path)
        # df.to_csv(local_path+'.csv')
        #df.to_json(local_path+".json", orient="records", indent=2)
 # required columns
        req_cols = ["Code Value", "Code Meaning", "Body Part Examined"]


        df2 = pd.read_json(local_path+".json", orient="records")
        mapping = df2[req_cols]

        # remove empty values:
        mapping = mapping[~mapping['Body Part Examined'].isnull()]


        return mapping



        print("Loaded table from local cache.")

def _get_snomed(dicom_bodypart, sctmapping):
    # codes are strings
    if(sctmapping is not None):
        return (sctmapping.loc[sctmapping['Body Part Examined'] == dicom_bodypart]["Code Value"].values[0],
                sctmapping.loc[sctmapping['Body Part Examined'] == dicom_bodypart]["Code Meaning"].values[0])





def test_pandas():

    get_html_table_to_json()


    #reload the json:




    # mapping_table = load_mappingtable('body_site_mapping.pkl')
    
    # #_get_snomed_bodysite_mapping(url='https://dicom.nema.org/medical/dicom/current/output/chtml/part16/chapter_L.html') 
    
    
    # bd_snomed, meaning = _get_snomed('ASCAORTA', sctmapping=mapping_table) 
    # print(bd_snomed, meaning)  



test_pandas()








