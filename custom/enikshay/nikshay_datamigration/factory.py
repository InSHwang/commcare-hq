from dimagi.utils.decorators.memoized import memoized

from casexml.apps.case.const import CASE_INDEX_EXTENSION
from casexml.apps.case.mock import CaseFactory, CaseStructure, CaseIndex
from corehq.apps.locations.models import SQLLocation
from corehq.form_processor.exceptions import CaseNotFound
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from custom.enikshay.nikshay_datamigration.models import Outcome, Followup


def validate_number(string_value):
    if string_value is None or string_value.strip() == '':
        return None
    else:
        return int(string_value)


class EnikshayCaseFactory(object):

    domain = None
    patient_detail = None

    def __init__(self, domain, patient_detail):
        self.domain = domain
        self.patient_detail = patient_detail
        self.factory = CaseFactory(domain=domain)
        self.case_accessor = CaseAccessors(domain)

    def create_cases(self):
        self.create_person_occurrence_episode_cases()
        self.create_test_cases()

    def create_person_occurrence_episode_cases(self):
        episode_structure = self.episode(self._outcome)
        self.factory.create_or_update_case(episode_structure)

    def create_test_cases(self):
        self.factory.create_or_update_cases([self.test(followup) for followup in self._followups])

    @memoized
    def person(self):
        nikshay_id = self.patient_detail.PregId

        kwargs = {
            'attrs': {
                'case_type': 'person',
                # 'owner_id': self._location.location_id,
                'update': {
                    'aadhaar_number': self.patient_detail.paadharno,
                    'age': self.patient_detail.page,
                    'age_entered': self.patient_detail.page,
                    'contact_phone_number': validate_number(self.patient_detail.pmob),
                    'current_address': self.patient_detail.paddress,
                    'current_address_district_choice': self.patient_detail.Dtocode,
                    'current_address_state_choice': self.patient_detail.scode,
                    'dob_known': 'no',
                    'first_name': self.patient_detail.first_name,
                    'last_name': self.patient_detail.last_name,
                    'middle_name': self.patient_detail.middle_name,
                    'name': self.patient_detail.pname,
                    'nikshay_id': nikshay_id,
                    'permanent_address_district_choice': self.patient_detail.Dtocode,
                    'permanent_address_state_choice': self.patient_detail.scode,
                    'phi': self.patient_detail.PHI,
                    'secondary_contact_name_address': (
                        (self.patient_detail.cname or '')
                        + ', '
                        + (self.patient_detail.caddress or '')
                    ),
                    'secondary_contact_phone_number': validate_number(self.patient_detail.cmob),
                    'sex': self.patient_detail.sex,
                    'tu_choice': self.patient_detail.Tbunitcode,

                    'migration_created_case': True,
                },
            },
        }

        if nikshay_id in self.nikshay_id_to_preexisting_nikshay_person_cases:
            kwargs['case_id'] = self.nikshay_id_to_preexisting_nikshay_person_cases[nikshay_id].case_id
            kwargs['attrs']['create'] = False
        else:
            kwargs['attrs']['create'] = True

        return CaseStructure(**kwargs)

    @memoized
    def occurrence(self, outcome):
        kwargs = {
            'attrs': {
                'case_type': 'occurrence',
                'update': {
                    'name': 'Occurrence #1',
                    'nikshay_id': self.patient_detail.PregId,
                    'occurrence_episode_count': 1,

                    'migration_created_case': True,
                },
            },
            'indices': [CaseIndex(
                self.person(),
                identifier='host',
                relationship=CASE_INDEX_EXTENSION,
                related_type=self.person().attrs['case_type'],
            )],
        }
        if outcome:
            # TODO - store with correct value
            kwargs['attrs']['update']['hiv_status'] = outcome.HIVStatus

        try:
            matching_occurrence_case = next((
                occurrence_case for occurrence_case in self.case_accessor.get_cases([
                    index.referenced_id for index in
                    self.case_accessor.get_case(self.person().case_id).reverse_indices
                ])
                if self.patient_detail.PregId == occurrence_case.dynamic_case_properties().get('nikshay_id')
            ), None)
        except CaseNotFound:
            matching_occurrence_case = None
        if matching_occurrence_case:
            kwargs['case_id'] = matching_occurrence_case.case_id
            kwargs['attrs']['create'] = False
        else:
            kwargs['attrs']['create'] = True

        return CaseStructure(**kwargs)

    @memoized
    def episode(self, outcome):
        kwargs = {
            'attrs': {
                'case_type': 'episode',
                'update': {
                    'date_reported': self.patient_detail.pregdate1,  # is this right?
                    'disease_classification': self.patient_detail.disease_classification,
                    'patient_type_choice': self.patient_detail.patient_type_choice,
                    'treatment_supporter_designation': self.patient_detail.treatment_supporter_designation,
                    'treatment_supporter_first_name': self.patient_detail.treatment_supporter_first_name,
                    'treatment_supporter_last_name': self.patient_detail.treatment_supporter_last_name,
                    'treatment_supporter_mobile_number': validate_number(self.patient_detail.dotmob),

                    'migration_created_case': True,
                },
            },
            'indices': [CaseIndex(
                self.occurrence(outcome),
                identifier='host',
                relationship=CASE_INDEX_EXTENSION,
                related_type=self.occurrence(outcome).attrs['case_type'],
            )],
        }

        try:
            matching_episode_case = next((
                extension_case for extension_case in self.case_accessor.get_cases([
                    index.referenced_id for index in
                    self.case_accessor.get_case(self.occurrence(outcome).case_id).reverse_indices
                ])
                if (
                    extension_case.type == 'episode'
                    and extension_case.dynamic_case_properties().get('migration_created_case')
                )
            ), None)
        except CaseNotFound:
            matching_episode_case = None
        if matching_episode_case:
            kwargs['case_id'] = matching_episode_case.case_id
            kwargs['attrs']['create'] = False
        else:
            kwargs['attrs']['create'] = True

        return CaseStructure(**kwargs)

    @memoized
    def test(self, followup):
        occurrence_structure = self.occurrence(self._outcome)  # TODO - pass outcome as argument

        kwargs = {
            'attrs': {
                'create': True,
                'case_type': 'test',
                'update': {
                    'date_tested': followup.TestDate,

                    'migration_created_case': True,
                    'migration_followup_id': followup.id,
                },
            },
            'indices': [CaseIndex(
                occurrence_structure,
                identifier='host',
                relationship=CASE_INDEX_EXTENSION,
                related_type=occurrence_structure.attrs['case_type'],
            )],
        }

        matching_test_case = next((
            extension_case for extension_case in self.case_accessor.get_cases([
                index.referenced_id for index in
                self.case_accessor.get_case(occurrence_structure.case_id).reverse_indices
            ])
            if (
                extension_case.type == 'test'
                and followup.id == int(extension_case.dynamic_case_properties().get('migration_followup_id', -1))
            )
        ), None)
        if matching_test_case:
            kwargs['case_id'] = matching_test_case.case_id
            kwargs['attrs']['create'] = False
        else:
            kwargs['attrs']['create'] = True

        return CaseStructure(**kwargs)

    @property
    @memoized
    def nikshay_id_to_preexisting_nikshay_person_cases(self):
        return {
            person_case.dynamic_case_properties()['nikshay_id']: person_case
            for person_case in self.case_accessor.get_cases([
                case_id for case_id in self.case_accessor.get_case_ids_in_domain(type='person')
            ])
            if person_case.dynamic_case_properties().get('migration_created_case')
        }

    @property
    @memoized
    def _outcome(self):
        zero_or_one_outcomes = list(Outcome.objects.filter(PatientId=self.patient_detail))
        if zero_or_one_outcomes:
            return zero_or_one_outcomes[0]
        else:
            return None

    @property
    @memoized
    def _followups(self):
        return Followup.objects.filter(PatientID=self.patient_detail)

    @property
    def _location(self):
        return self.nikshay_code_to_location(self.domain)[self._nikshay_code]

    @classmethod
    @memoized
    def nikshay_code_to_location(cls, domain):
        return {
            location.metadata.get('nikshay_code'): location
            for location in SQLLocation.objects.filter(domain=domain)
            if 'nikshay_code' in location.metadata
        }

    @property
    def _nikshay_code(self):
        return '-'.join(self.patient_detail.PregId.split('-')[:4])
