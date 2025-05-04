#Simple conversion DICOM SR to FHIR
#  pip install fhir.resources

import pydicom
import uuid

import json
from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from fhir.resources.observation import Observation
from fhir.resources.imagingstudy import ImagingStudy
from fhir.resources.documentreference import DocumentReference

from fhir.resources.humanname import HumanName
from fhir.resources.identifier import Identifier
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.coding import Coding
from fhir.resources.attachment import Attachment
from fhir.resources.meta import Meta
from fhir.resources.reference import Reference
from fhir.resources.fhirtypes import DateType, DateTimeType
from fhir.resources.imagingstudy import ImagingStudy, ImagingStudySeries, ImagingStudySeriesInstance


#reading dicom file
ds = pydicom.dcmread("report09.dcm")
# Helper: get a tag value safely
def get_value(ds,tag_name):
    return getattr(ds, tag_name, None)

# Helper function to create a CodeableConcept
def create_codeable_concept(system, code, display):
    return CodeableConcept(
        coding=[Coding(system=system, code=code, display=display)],
        text=display
    )
# Extract useful identifiers
study_uid = get_value(ds,"StudyInstanceUID")
series_uid = get_value(ds,"SeriesInstanceUID")
sop_uid = get_value(ds,"SOPInstanceUID")
modality = get_value(ds,"Modality")
date = get_value(ds,"StudyDate") or get_value(ds,"ContentDate")

description = get_value(ds,"SeriesDescription") or get_value(ds,"StudyDescription")

# --- Create Patient Resource -------------------------------------------------------------------
patient = Patient()
patient.id = str(uuid.uuid4())

# Identifier
if hasattr(ds, "PatientID"):
    patient.identifier = [
        Identifier(
            system="urn:dicom:patientid",
            value=ds.PatientID
        )
    ]

# Name
if hasattr(ds, "PatientName"):
    name = ds.PatientName
    patient.name = [
        HumanName(
            family=name.family_name,
            given=[name.given_name] if name.given_name else []
        )
    ]

# Gender
if hasattr(ds, "PatientSex"):
    patient.gender = ds.PatientSex.lower()
    
# Birth Date
if hasattr(ds, "PatientBirthDate"):
    if(len(ds.PatientBirthDate)>8):
        patient.birthDate = f"{ds.PatientBirthDate[:4]}-{ds.PatientBirthDate[4:6]}-{ds.PatientBirthDate[6:]}"


# --- Create Observation Resource -------------------------------------------------------------------------------------
observation = Observation.construct()
# observation.id = "observation-1"
observation.status = "final"
observation.subject = {"reference": f"Patient/{patient.id}"}
observation.code = create_codeable_concept( system="http://loinc.org",
                                            code="18767-4",
                                            display="DICOM Structured Report")

# Effective date
if hasattr(ds, "StudyDate"):
    date = ds.StudyDate
    if(len(date)>8):
        observation.effectiveDateTime = f"{date[:4]}-{date[4:6]}-{date[6:]}T00:00:00Z"

# Observation value
value_lines = []
if hasattr(ds, "StudyDescription"):
    value_lines.append(f"Study Description: {ds.StudyDescription}")
if hasattr(ds, "SeriesDescription"):
    value_lines.append(f"Series Description: {ds.SeriesDescription}")
if hasattr(ds, "Modality"):
    value_lines.append(f"Modality: {ds.Modality}")
observation.valueString = "\n".join(value_lines)


#---------------------------------Create DocumentReference----------------------------------------------------------------
doc_ref = DocumentReference.construct()
doc_ref.status = "current"
doc_ref.type = {
    "coding": [{
        "system": "http://loinc.org",
        "code": "18748-4",
        "display": "Diagnostic imaging study"
    }]
}
doc_ref.identifier = [Identifier(system="urn:dicom:uid", value=sop_uid or "unknown-sop")]
doc_ref.description = description or "DICOM Structured Report"
doc_ref.content = [{
    "attachment": Attachment.construct(
        contentType="application/dicom",
        url=f"urn:oid:{sop_uid}" if sop_uid else None,
        title="DICOM SR Report"
    )
}]

#----------generate bundle-------------------------------------------------------------------------------------------------
bundle = Bundle.construct()
bundle.type = "collection"
bundle.entry = [
    {"resource": patient},
    {"resource": observation},
    # {"resource": imaging_study},
    {"resource": doc_ref}
]

# ---------Save bundle --------------------------------------------------------------------------------------------------
with open("dicom_sr_full_bundle.json", "w") as f:
    json.dump(bundle.dict(), f, indent=2)

print("✅ FHIR Bundle exported to dicom_sr_full_bundle.json")