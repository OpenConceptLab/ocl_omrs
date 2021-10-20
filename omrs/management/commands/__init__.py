""" Init for commands """


class UnrecognizedSourceException(Exception):
    """ UnrecognizedSourceException """
    pass


class OclOpenmrsHelper(object):
    """ Helper class for OpenMRS exporter and validator """

    MAP_TYPE_CONCEPT_SET = 'CONCEPT-SET'
    MAP_TYPE_Q_AND_A = 'Q-AND-A'
    MAP_TYPE_SAME_AS = 'SAME-AS'

    OCL_API_URL = {
        'qa': 'https://api.qa.openconceptlab.org',
        'demo': 'https://api.demo.openconceptlab.org',
        'staging': 'https://api.staging.openconceptlab.org',
        'production': 'https://api.openconceptlab.org',
    }

    # Directory of sources with metadata
    SOURCE_DIRECTORY = [
        {'owner_type': 'org', 'owner_id': 'IHTSDO',
            'omrs_id': 'SNOMED CT', 'ocl_id': 'SNOMED-CT'},
        {'owner_type': 'org', 'owner_id': 'IHTSDO',
            'omrs_id': 'SNOMED NP', 'ocl_id': 'SNOMED-NP'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'ICD-10-WHO', 'ocl_id': 'ICD-10-WHO'},
        {'owner_type': 'org', 'owner_id': 'NLM',
            'omrs_id': 'RxNORM', 'ocl_id': 'RxNORM'},
        {'owner_type': 'org', 'owner_id': 'NLM',
            'omrs_id': 'RxNORM Comb', 'ocl_id': 'RxNORM-Comb'},
        {'owner_type': 'org', 'owner_id': 'Regenstrief',
            'omrs_id': 'LOINC', 'ocl_id': 'LOINC'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'ICD-10-WHO NP', 'ocl_id': 'ICD-10-WHO-NP'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'ICD-10-WHO 2nd', 'ocl_id': 'ICD-10-WHO-2nd'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'ICD-10-WHO NP2', 'ocl_id': 'ICD-10-WHO-NP2'},
        {'owner_type': 'org', 'owner_id': 'HL7',
            'omrs_id': 'HL-7 CVX', 'ocl_id': 'HL-7-CVX'},
        {'owner_type': 'org', 'owner_id': 'PIH',
            'omrs_id': 'PIH', 'ocl_id': 'PIH'},
        {'owner_type': 'org', 'owner_id': 'PIH',
            'omrs_id': 'PIH Malawi', 'ocl_id': 'PIH-Malawi'},
        {'owner_type': 'org', 'owner_id': 'AMPATH',
            'omrs_id': 'AMPATH', 'ocl_id': 'AMPATH'},
        {'owner_type': 'org', 'owner_id': 'CIEL',
            'omrs_id': 'SNOMED MVP', 'ocl_id': 'SNOMED-MVP'},
        {'owner_type': 'org', 'owner_id': 'CIEL',
            'omrs_id': 'SNOMED UK', 'ocl_id': 'SNOMED-UK'},
        {'owner_type': 'org', 'owner_id': 'OpenMRS',
            'omrs_id': 'org.openmrs.module.mdrtb', 'ocl_id': 'org.openmrs.module.mdrtb'},
        {'owner_type': 'org', 'owner_id': 'MVP',
            'omrs_id': 'MVP Amazon Server 174', 'ocl_id': 'MVP-Amazon-Server-174'},
        {'owner_type': 'org', 'owner_id': 'IHTSDO',
            'omrs_id': 'SNOMED US', 'ocl_id': 'SNOMED-US'},
        {'owner_type': 'org', 'owner_id': 'HL7', 'omrs_id': 'HL7 2.x Route of Administration',
            'ocl_id': 'HL7-2.x-Route-of-Administration'},
        {'owner_type': 'org', 'owner_id': '3BT',
            'omrs_id': '3BT', 'ocl_id': '3BT'},
        {'owner_type': 'org', 'owner_id': 'WICC',
            'omrs_id': 'ICPC2', 'ocl_id': 'ICPC2'},
        {'owner_type': 'org', 'owner_id': 'CIEL',
            'omrs_id': 'CIEL', 'ocl_id': 'CIEL'},
        {'owner_type': 'org', 'owner_id': 'CCAM',
            'omrs_id': 'CCAM', 'ocl_id': 'CCAM'},
        {'owner_type': 'org', 'owner_id': 'OpenMRS',
            'omrs_id': 'org.openmrs.module.emrapi', 'ocl_id': 'org.openmrs.module.emrapi'},
        {'owner_type': 'org', 'owner_id': 'IMO',
            'omrs_id': 'IMO ProblemIT', 'ocl_id': 'IMO-ProblemIT'},
        {'owner_type': 'org', 'owner_id': 'IMO',
            'omrs_id': 'IMO ProcedureIT', 'ocl_id': 'IMO-ProcedureIT'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'Pharmacologic Drug Class', 'ocl_id': 'Pharmacologic-Drug-Class'},
        {'owner_type': 'org', 'owner_id': 'VHA',
            'omrs_id': 'NDF-RT NUI', 'ocl_id': 'NDF-RT-NUI'},
        {'owner_type': 'org', 'owner_id': 'FDA', 'omrs_id': 'FDA Route of Administration',
            'ocl_id': 'FDA-Route-of-Administration'},
        {'owner_type': 'org', 'owner_id': 'NCI',
            'omrs_id': 'NCI Concept Code', 'ocl_id': 'NCI-Concept-Code'},
        {'owner_type': 'org', 'owner_id': 'HL7', 'omrs_id': 'HL7 DiagnosticReportStatus',
            'ocl_id': 'HL7-DiagnosticReportStatus'},
        {'owner_type': 'org', 'owner_id': 'HL7', 'omrs_id': 'HL7 DiagnosticServiceSections',
            'ocl_id': 'HL7-DiagnosticServiceSections'},
        {'owner_type': 'org', 'owner_id': 'AMA',
            'omrs_id': 'CPT', 'ocl_id': 'CPT'},
        {'owner_type': 'org', 'owner_id': 'RSNA',
            'omrs_id': 'Radlex', 'ocl_id': 'Radlex'},
        {'owner_type': 'org', 'owner_id': 'PIH',
            'omrs_id': 'Liberia MoH', 'ocl_id': 'LiberiaMOH'},
        {'owner_type': 'org', 'owner_id': 'PIH', 'omrs_id': 'org.openmrs.module.mirebalaisreports',
            'ocl_id': 'org.openmrs.module.mirebalaisreports'},
        {'owner_type': 'org', 'owner_id': 'PIH', 'omrs_id': 'org.openmrs.module.hirifxray',
            'ocl_id': 'org.openmrs.module.hirifxray'},
        {'owner_type': 'org', 'owner_id': 'VHA',
            'omrs_id': 'MED-RT NUI', 'ocl_id': 'MED-RT-NUI'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'WHOATC', 'ocl_id': 'WHOATC'},
        {'owner_type': 'org', 'owner_id': 'NAACCR',
            'omrs_id': 'NAACCR', 'ocl_id': 'NAACCR'},
        {'owner_type': 'org', 'owner_id': 'KenyaMOH',
            'omrs_id': 'KenyaEMR', 'ocl_id': 'KenyaEMR'},
        {'owner_type': 'org', 'owner_id': 'PIH',
            'omrs_id': 'Mexico MoH SIS', 'ocl_id': 'Mexico-MoH-SIS'},
        {'owner_type': 'org', 'owner_id': 'PIH',
            'omrs_id': 'Mexico MoH SUIVE', 'ocl_id': 'Mexico-MoH-SUIVE'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'ICD-11-WHO', 'ocl_id': 'ICD-11-WHO'},
        {'owner_type': 'org', 'owner_id': 'WHO',
            'omrs_id': 'WHO ICHI', 'ocl_id': 'WHO-ICHI'},
        {'omrs_id': 'ICD-O Morphology', 'ocl_id': 'ICD-O-WHO-Morphology',
            'owner_type': 'org', 'owner_id': 'WHO'},
        {'omrs_id': 'ICD-O Histology', 'ocl_id': 'ICD-O-WHO-Histology',
            'owner_type': 'org', 'owner_id': 'WHO'},
        {'omrs_id': 'ICD-O Topology', 'ocl_id': 'ICD-O-WHO-Topology',
            'owner_type': 'org', 'owner_id': 'WHO'},
        {'omrs_id': 'org.openmrs.module.mirebalaisreports', 'ocl_id': 'org.openmrs.module.mirebalaisreports',
         'owner_type': 'org', 'owner_id': 'PIH'},
        {'omrs_id': 'Liberia MoH', 'ocl_id': 'LiberiaMOH',
         'owner_type': 'org', 'owner_id': 'PIH'},
        {'omrs_id': 'HL-7 MVX code', 'ocl_id': 'MVX',
            'owner_type': 'org', 'owner_id': 'HL7'}

        # Added for AMPATH dictionary import
        # {'owner_type':'org', 'owner_id':'WHO', 'omrs_id':'ICD-10', 'ocl_id':'ICD-10-WHO'},
        # {'owner_type':'org', 'owner_id':'CIEL', 'omrs_id':'MCL/CIEL', 'ocl_id':'CIEL'},
        # {'owner_type':'org', 'owner_id':'NLM', 'omrs_id':'RxNorm', 'ocl_id':'RxNORM'},
        # {'owner_type':'org', 'owner_id':'KenyaMOH', 'omrs_id':'KENYA EMR', 'ocl_id':'KenyaEMR'},
    ]

    @classmethod
    def get_source_owner_id(cls, omrs_source_id=None, ocl_source_id=None):
        """ Returns the owner ID for the specified source """
        if omrs_source_id and ocl_source_id:
            raise Exception(
                'Must pass only omrs_source_id or ocl_source_id. Both provided.')
        elif omrs_source_id:
            source_id = omrs_source_id
            source_id_type = 'omrs_id'
        elif ocl_source_id:
            source_id = ocl_source_id
            source_id_type = 'ocl_id'
        else:
            raise Exception(
                'Must pass omrs_source_id or ocl_source_id. Neither provided.')
        for src in cls.SOURCE_DIRECTORY:
            if src[source_id_type] == source_id:
                return src['owner_id']
        raise UnrecognizedSourceException(
            'Source %s not found in source directory.' % source_id)

    @classmethod
    def get_ocl_source_id_from_omrs_id(cls, omrs_source_id):
        for src in cls.SOURCE_DIRECTORY:
            if src['omrs_id'] == omrs_source_id:
                return src['ocl_id']
        raise UnrecognizedSourceException(
            'Source %s not found in source directory.' % omrs_source_id)

    @classmethod
    def get_omrs_source_id_from_ocl_id(cls, ocl_source_id):
        for src in cls.SOURCE_DIRECTORY:
            if src['ocl_id'] == ocl_source_id:
                return src['omrs_id']
        raise UnrecognizedSourceException(
            'Source %s not found in source directory.' % ocl_source_id)
