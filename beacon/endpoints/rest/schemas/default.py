import logging

from .... import conf
from .utils import filter_hstore

# It will raise an exception if the fields are not found in the record
from ....utils.json import jsonb

LOG = logging.getLogger(__name__)


def beacon_info_v20(datasets, authorized_datasets=[]):
    return {
        'id': conf.beacon_id,
        'name': conf.beacon_name,
        'apiVersion': conf.api_version,
        'environment': conf.environment,
        'organization': {
            'id': conf.org_id,
            'name': conf.org_name,
            'description': conf.org_description,
            'address': conf.org_adress,
            'welcomeUrl': conf.org_welcome_url,
            'contactUrl': conf.org_contact_url,
            'logoUrl': conf.org_logo_url,
            'info': conf.org_info,
        },
        'description': conf.description,
        'version': conf.version,
        'welcomeUrl': conf.welcome_url,
        'alternativeUrl': conf.alternative_url,
        'createDateTime': conf.create_datetime,
        'updateDateTime': conf.update_datetime,
        'serviceType': conf.service_type,
        'serviceUrl': conf.service_url,
        'entryPoint': conf.entry_point,
        'open': conf.is_open,
        'datasets': [beacon_dataset_info_v20(row, authorized_datasets) for row in datasets],
        'info': None,
    }


def beacon_dataset_info_v20(row, authorized_datasets=[]):
    dataset_id = row['datasetId']
    is_authorized = dataset_id in authorized_datasets

    return {
        'id': dataset_id,
        'name': row['name'],
        'description': row['description'],
        'assemblyId': row['assemblyId'],
        'createDateTime': row['createdAt'].strftime(conf.datetime_format) if row['createdAt'] else None,
        'updateDateTime': row['updatedAt'].strftime(conf.datetime_format) if row['updatedAt'] else None,
        'dataUseConditions': None,
        'version': None,
        'variantCount': row['variantCount'],  # already coalesced
        'callCount': row['callCount'],
        'sampleCount': row['sampleCount'],
        'externalURL': None,
        'info': {
            'accessType': row['accessType'],
            'authorized': True if row['accessType'] == 'PUBLIC' else is_authorized,
            'datasetSource': row['datasetSource'],
            'datasetType': row['datasetType']
        }
    }


def beacon_variant_v20(row):
    return {
            'variantId': row['variant_id'],
            'refseqId': row['refseq_id'],
            'ref': row['reference'],
            'alt': row['alternate'],
            'variantType': row['variant_type'],
            'start': row['start'],
            'end': row['end'],
            'assemblyId': row['assembly_id'],
            'info': None,
        }


def beacon_variant_annotation_v20(row):
    schema_name = 'beacon-variant-annotation-v2.0.0-draft.2'
    return {
            'variantId': row['variant_id'],
            'variantAlternativeIds': [row['variant_name']],
            'genomicHGVSId': row['genomic_hgvs_id'],
            'transcriptHGVSIds': row['transcript_hgvs_ids'],
            'proteinHGVSIds': row['protein_hgvs_ids'],
            'genomicRegions': row['genomic_regions'],
            'genomicFeatures': filter_hstore(row['genomic_features_ontology'], schema_name),
            'molecularEffects': row['molecular_effects'],
            'aminoacidChanges': row['aminoacid_changes'],
            'info': None
        }

def beacon_biosample_v20(row):
    schema_name = 'beacon-biosample-v2.0.0-draft.2'
    return {
        'biosampleId': row['biosample_stable_id'],
        'subjectId': row['individual_stable_id'],
        'description': row['description'],
        'biosampleStatus': row['biosample_status_ontology'],
        'collectionDate':  str(row['collection_date']) if row['collection_date'] else None,
        'subjectAgeAtCollection': row['individual_age_at_collection'],
        'sampleOriginDescriptors': filter_hstore(row['sample_origins_ontology'], schema_name),
        'obtentionProcedure': row['obtention_procedure_ontology'],
        'cancerFeatures': {
            'tumorProgression': row['tumor_progression_ontology'],
            'tumorGrade': row['tumor_grade_ontology'],
        },
        'handovers': [jsonb(h) for h in row['handovers']],
        'info': {
            'alternativeIds': row['alternative_ids'],
            'studyId': row['study_id'],
            'bioprojectId': row['bioproject_id'],
            'files': [jsonb(v) for v in row['files']],
        }
    }


def beacon_individual_v20(row):
    schema_name = 'beacon-individual-v2.0.0-draft.2'
    return {
        'subjectId': row.get('individual_stable_id', ''),
        'datasetIds': row.get('dataset_ids', ''),
        'taxonId': row.get('taxon_id', ''),
        'sex': row.get('sex_ontology', ''),
        'ethnicity': row.get('ethnicity_ontology', ''),
        'geographicOrigin': row.get('geographic_origin_ontology', ''),
        'phenotypicFeatures': filter_hstore(row.get('phenotypic_features', ''), schema_name),
        'diseases': row.get('diseases', ''),
        # 'diseases': filter_hstore(row.get('diseases', []), schema_name),
        # 'treatments': filter_hstore(row.get('treatments', []), schema_name),  # Added to match the newest schema; to be added in the matching DB part
        # 'interventions': filter_hstore(row.get('interventions', []), schema_name),  # As above... TODO: remove this comment after it works
        'pedigrees': filter_hstore(row.get('pedigrees', []), schema_name),
        'handovers': [jsonb(h) for h in row.get('handovers', [])],
        'info': {
            'medications': row.get('medications', '{}'),
            # 'medications': [jsonb(v) for v in row.get('medications', [])
            # 'sraFamilyId': row.get('sra_family_id', ''),     # TODO: remove if no longer needed
            # 'alternativeIds': row.get('alternative_ids', ''),
            'race': row.get('race', '')
            # 'weightKg': row.get('weight_kg', ''),
            # 'heightCm': row.get('height_cm', ''),
            # 'bloodType': row.get('blood_type', ''),
            # 'procedures': [jsonb(v) for v in row.get('procedures', '')],
        }
    }

