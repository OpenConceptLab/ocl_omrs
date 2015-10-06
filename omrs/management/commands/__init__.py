""" Init for commands """


class UnrecognizedSourceException(Exception):
    """ UnrecognizedSourceException """
    pass



class OclOpenmrsHelper(object):
    """ Helper class for OpenMRS exporter and validator """

    ## CONSTANTS
    MAP_TYPE_CONCEPT_SET = 'CONCEPT-SET'
    MAP_TYPE_Q_AND_A = 'Q-AND-A'

    # Directory of sources with metadata
    SOURCE_DIRECTORY = [
        {'owner_type':'org', 'onwer_id':'IHTSDO', 'omrs_id':'SNOMED CT', 'ocl_id':'SNOMED-CT'},
        {'owner_type':'org', 'onwer_id':'IHTSDO', 'omrs_id':'SNOMED NP', 'ocl_id':'SNOMED-NP'},
        {'owner_type':'org', 'onwer_id':'WHO', 'omrs_id':'ICD-10-WHO', 'ocl_id':'ICD-10-WHO'},
        {'owner_type':'org', 'onwer_id':'NLM', 'omrs_id':'RxNORM', 'ocl_id':'RxNORM'},
        {'owner_type':'org', 'onwer_id':'NLM', 'omrs_id':'RxNORM Comb', 'ocl_id':'RxNORM-Comb'},
        {'owner_type':'org', 'onwer_id':'Regenstrief', 'omrs_id':'LOINC', 'ocl_id':'LOINC'},
        {'owner_type':'org', 'onwer_id':'WHO', 'omrs_id':'ICD-10-WHO NP', 'ocl_id':'ICD-10-WHO-NP'},
        {'owner_type':'org', 'onwer_id':'WHO', 'omrs_id':'ICD-10-WHO 2nd', 'ocl_id':'ICD-10-WHO-2nd'},
        {'owner_type':'org', 'onwer_id':'WHO', 'omrs_id':'ICD-10-WHO NP2', 'ocl_id':'ICD-10-WHO-NP2'},
        {'owner_type':'org', 'onwer_id':'HL7', 'omrs_id':'HL-7 CVX', 'ocl_id':'HL-7-CVX'},
        {'owner_type':'org', 'onwer_id':'PIH', 'omrs_id':'PIH', 'ocl_id':'PIH'},
        {'owner_type':'org', 'onwer_id':'PIH', 'omrs_id':'PIH Malawi', 'ocl_id':'PIH-Malawi'},
        {'owner_type':'org', 'onwer_id':'AMPATH', 'omrs_id':'AMPATH', 'ocl_id':'AMPATH'},
        {'owner_type':'org', 'onwer_id':'CIEL', 'omrs_id':'SNOMED MVP', 'ocl_id':'SNOMED-MVP'},
        {'owner_type':'org', 'onwer_id':'OpenMRS', 'omrs_id':'org.openmrs.module.mdrtb', 'ocl_id':'org.openmrs.module.mdrtb'},
        {'owner_type':'org', 'onwer_id':'MVP', 'omrs_id':'MVP Amazon Server 174', 'ocl_id':'MVP-Amazon-Server-174'},
        {'owner_type':'org', 'onwer_id':'IHTSDO', 'omrs_id':'SNOMED US', 'ocl_id':'SNOMED-US'},
        {'owner_type':'org', 'onwer_id':'HL7', 'omrs_id':'HL7 2.x Route of Administration', 'ocl_id':'HL7-2.x-Route-of-Administration'},
        {'owner_type':'org', 'onwer_id':'3BT', 'omrs_id':'3BT', 'ocl_id':'3BT'},
        {'owner_type':'org', 'onwer_id':'WICC', 'omrs_id':'ICPC2', 'ocl_id':'ICPC2'},
        {'owner_type':'org', 'onwer_id':'CIEL', 'omrs_id':'CIEL', 'ocl_id':'CIEL'},
        {'owner_type':'org', 'onwer_id':'CCAM', 'omrs_id':'CCAM', 'ocl_id':'CCAM'},
        {'owner_type':'org', 'onwer_id':'OpenMRS', 'omrs_id':'org.openmrs.module.emrapi', 'ocl_id':'org.openmrs.module.emrapi'},
        {'owner_type':'org', 'onwer_id':'IMO', 'omrs_id':'IMO ProblemIT', 'ocl_id':'IMO-ProblemIT'},
        {'owner_type':'org', 'onwer_id':'IMO', 'omrs_id':'IMO ProcedureIT', 'ocl_id':'IMO-ProcedureIT'},
        {'owner_type':'org', 'onwer_id':'WHO', 'omrs_id':'Pharmacologic Drug Class', 'ocl_id':'Pharmacologic-Drug-Class'},
        {'owner_type':'org', 'onwer_id':'VHA', 'omrs_id':'NDF-RT NUI', 'ocl_id':'NDF-RT-NUI'},
        {'owner_type':'org', 'onwer_id':'FDA', 'omrs_id':'FDA Route of Administration', 'ocl_id':'FDA-Route-of-Administration'},
        {'owner_type':'org', 'onwer_id':'NCI', 'omrs_id':'NCI Concept Code', 'ocl_id':'NCI-Concept-Code'},
        {'owner_type':'org', 'onwer_id':'HL7', 'omrs_id':'HL7 DiagnosticReportStatus', 'ocl_id':'HL7-DiagnosticReportStatus'},
        {'owner_type':'org', 'onwer_id':'HL7', 'omrs_id':'HL7 DiagnosticServiceSections', 'ocl_id':'HL7-DiagnosticServiceSections'},
    ]

    @classmethod
    def get_source_owner_id(cls, omrs_source_id=None, ocl_source_id=None):
        """ Returns the owner ID for the specified source """
        if omrs_source_id and ocl_source_id:
            raise Exception('Must pass only omrs_source_id or ocl_source_id. Both provided.')
        elif omrs_source_id:
            source_id = omrs_source_id
            source_id_type = 'omrs_id'
        elif ocl_source_id:
            source_id = ocl_source_id
            source_id_type = 'ocl_id'
        else:
            raise Exception('Must pass omrs_source_id or ocl_source_id. Neither provided.')
        for src in cls.SOURCE_DIRECTORY:
            if src[source_id_type] == source_id:
                return src['owner_id']
        raise UnrecognizedSourceException('Source %s not found in source directory.' % source_id)

    @classmethod
    def get_ocl_source_id_from_omrs_id(cls, omrs_source_id):
        for src in cls.SOURCE_DIRECTORY:
            if src['omrs_id'] == omrs_source_id:
                return src['ocl_id']
        raise UnrecognizedSourceException('Source %s not found in source directory.' % omrs_source_id)

    @classmethod
    def get_omrs_source_id_from_ocl_id(cls, ocl_source_id):
        for src in cls.SOURCE_DIRECTORY:
            if src['ocl_id'] == ocl_source_id:
                return src['omrs_id']
        raise UnrecognizedSourceException('Source %s not found in source directory.' % ocl_source_id)
