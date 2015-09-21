# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Concept(models.Model):
    concept_id = models.IntegerField(primary_key=True)
    retired = models.BooleanField()
    short_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    form_text = models.TextField(blank=True)
#    datatype_id = models.IntegerField()
    datatype = models.ForeignKey('ConceptDatatype')
#    class_id = models.IntegerField()
    concept_class = models.ForeignKey('ConceptClass', db_column='class_id')
    is_set = models.IntegerField()
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    version = models.CharField(max_length=50, blank=True)
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)

    def __unicode__(self):
        rs = self.conceptname_set.filter(locale_preferred=True)
        return rs[0].name

    class Meta:
        managed = False
        db_table = 'concept'


class ConceptAnswer(models.Model):
    concept_answer_id = models.IntegerField(primary_key=True)

    # answers for this concept
#    concept_id = models.IntegerField()
    question_concept = models.ForeignKey('Concept',
        db_column='concept_id', related_name='question_answer')

#    answer_concept = models.IntegerField(blank=True, null=True)
    answer_concept = models.ForeignKey('Concept',
        db_column='answer_concept', related_name='answer')

    answer_drug = models.IntegerField(blank=True, null=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    uuid = models.CharField(unique=True, max_length=38)
    sort_weight = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'concept_answer'

class ConceptClass(models.Model):
    concept_class_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    retired = models.IntegerField()
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'concept_class'


class ConceptComplex(models.Model):
    concept = models.ForeignKey(Concept, primary_key=True)
    handler = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.handler

    class Meta:
        managed = False
        db_table = 'concept_complex'

class ConceptDatatype(models.Model):
    concept_datatype_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    hl7_abbreviation = models.CharField(max_length=3, blank=True)
    description = models.CharField(max_length=255)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    retired = models.IntegerField()
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_datatype'


class ConceptDescription(models.Model):
    concept_description_id = models.IntegerField(primary_key=True)
#    concept_id = models.IntegerField()
    concept = models.ForeignKey('Concept')
    description = models.TextField()
    locale = models.CharField(max_length=50)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(unique=True, max_length=38)

    def __unicode__(self):
        return self.description

    class Meta:
        managed = False
        db_table = 'concept_description'


class ConceptMapType(models.Model):
    concept_map_type_id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    description = models.CharField(max_length=255, blank=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)
    is_hidden = models.IntegerField(blank=True, null=True)
    retired = models.IntegerField()
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)

    class Meta:
        managed = False
        db_table = 'concept_map_type'

    def __unicode__(self):
        return self.name


class ConceptName(models.Model):
#    concept_id = models.IntegerField(blank=True, null=True)
    concept = models.ForeignKey('Concept')
    name = models.CharField(max_length=255)
    locale = models.CharField(max_length=50)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    concept_name_id = models.IntegerField(unique=True, primary_key=True)
    voided = models.BooleanField()
    voided_by = models.IntegerField(blank=True, null=True)
    date_voided = models.DateTimeField(blank=True, null=True)
    void_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)
    concept_name_type = models.CharField(max_length=50, blank=True)
#    locale_preferred = models.IntegerField(blank=True, null=True)
    locale_preferred = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'concept_name'

class ConceptNameTag(models.Model):
    concept_name_tag_id = models.IntegerField(unique=True)
    tag = models.CharField(unique=True, max_length=50)
    description = models.TextField()
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    voided = models.IntegerField()
    voided_by = models.IntegerField(blank=True, null=True)
    date_voided = models.DateTimeField(blank=True, null=True)
    void_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_name_tag'

class ConceptNameTagMap(models.Model):
    concept_name = models.ForeignKey(ConceptName)
    concept_name_tag = models.ForeignKey(ConceptNameTag)
    class Meta:
        managed = False
        db_table = 'concept_name_tag_map'


class ConceptNumeric(models.Model):
    concept = models.ForeignKey(Concept, primary_key=True)
    hi_absolute = models.FloatField(blank=True, null=True)
    hi_critical = models.FloatField(blank=True, null=True)
    hi_normal = models.FloatField(blank=True, null=True)
    low_absolute = models.FloatField(blank=True, null=True)
    low_critical = models.FloatField(blank=True, null=True)
    low_normal = models.FloatField(blank=True, null=True)
    units = models.CharField(max_length=50, blank=True)
    precise = models.IntegerField()
    display_precision = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'concept_numeric'

class ConceptProposal(models.Model):
    concept_proposal_id = models.IntegerField(primary_key=True)
    concept_id = models.IntegerField(blank=True, null=True)
    encounter_id = models.IntegerField(blank=True, null=True)
    original_text = models.CharField(max_length=255)
    final_text = models.CharField(max_length=255, blank=True)
    obs_id = models.IntegerField(blank=True, null=True)
    obs_concept_id = models.IntegerField(blank=True, null=True)
    state = models.CharField(max_length=32)
    comments = models.CharField(max_length=255, blank=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)
    locale = models.CharField(max_length=50)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_proposal'


class ConceptProposalTagMap(models.Model):
    concept_proposal = models.ForeignKey(ConceptProposal)
    concept_name_tag = models.ForeignKey(ConceptNameTag)

    class Meta:
        managed = False
        db_table = 'concept_proposal_tag_map'


class ConceptReferenceMap(models.Model):
    concept_map_id = models.IntegerField(primary_key=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
#    concept_id = models.IntegerField()
    concept = models.ForeignKey('Concept')
    uuid = models.CharField(unique=True, max_length=38)
#    concept_reference_term_id = models.IntegerField()
    concept_reference_term = models.ForeignKey('ConceptReferenceTerm')
#    concept_map_type_id = models.IntegerField()
    map_type = models.ForeignKey('ConceptMapType',
        db_column='concept_map_type_id')
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'concept_reference_map'


class ConceptReferenceSource(models.Model):
    concept_source_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    hl7_code = models.CharField(unique=True, max_length=50, blank=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    retired = models.IntegerField()
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)

    class Meta:
        managed = False
        db_table = 'concept_reference_source'

    def __unicode__(self):
        return self.name


class ConceptReferenceTerm(models.Model):
    concept_reference_term_id = models.IntegerField(primary_key=True)
#    concept_source_id = models.IntegerField()
    concept_source = models.ForeignKey('ConceptReferenceSource')
    name = models.CharField(max_length=255, blank=True)
    code = models.CharField(max_length=255)
    version = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=255, blank=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    date_changed = models.DateTimeField(blank=True, null=True)
    changed_by = models.IntegerField(blank=True, null=True)
    retired = models.IntegerField()
    retired_by = models.IntegerField(blank=True, null=True)
    date_retired = models.DateTimeField(blank=True, null=True)
    retire_reason = models.CharField(max_length=255, blank=True)
    uuid = models.CharField(unique=True, max_length=38)

    class Meta:
        managed = False
        db_table = 'concept_reference_term'

    def __unicode__(self):
        # self.name is null
        return self.code


class ConceptReferenceTermMap(models.Model):
    concept_reference_term_map_id = models.IntegerField(primary_key=True)
    term_a_id = models.IntegerField()
    term_b_id = models.IntegerField()
    a_is_to_b_id = models.IntegerField()
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    changed_by = models.IntegerField(blank=True, null=True)
    date_changed = models.DateTimeField(blank=True, null=True)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_reference_term_map'


class ConceptSet(models.Model):
    concept_set_id = models.IntegerField(primary_key=True)
#    concept_id = models.IntegerField()
#    concept_set = models.IntegerField()
    concept = models.ForeignKey('Concept', db_column='concept_id', related_name='concept_set_parent')
    concept_set_owner = models.ForeignKey('Concept', db_column='concept_set')
    sort_weight = models.FloatField(blank=True, null=True)
    creator = models.IntegerField()
    date_created = models.DateTimeField()
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_set'

class ConceptSetDerived(models.Model):
    concept_id = models.IntegerField()
    concept_set = models.IntegerField()
    sort_weight = models.FloatField(blank=True, null=True)
    uuid = models.CharField(max_length=38, blank=True)
    class Meta:
        managed = False
        db_table = 'concept_set_derived'

class ConceptStateConversion(models.Model):
    concept_state_conversion_id = models.IntegerField(primary_key=True)
    concept_id = models.IntegerField(blank=True, null=True)
    program_workflow_id = models.IntegerField(blank=True, null=True)
    program_workflow_state_id = models.IntegerField(blank=True, null=True)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_state_conversion'

class ConceptStopWord(models.Model):
    concept_stop_word_id = models.IntegerField(primary_key=True)
    word = models.CharField(max_length=50)
    locale = models.CharField(max_length=20)
    uuid = models.CharField(unique=True, max_length=38)
    class Meta:
        managed = False
        db_table = 'concept_stop_word'

class ConceptWord(models.Model):
    concept_word_id = models.IntegerField()
    concept = models.ForeignKey(Concept)
    word = models.CharField(max_length=50)
    locale = models.CharField(max_length=20)
    concept_name = models.ForeignKey(ConceptName)
    weight = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'concept_word'

