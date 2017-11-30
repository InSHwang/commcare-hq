from __future__ import absolute_import
from __future__ import print_function
import csv
import datetime
from django.core.management.base import BaseCommand

from dimagi.utils.chunked import chunked

from corehq.apps.hqcase.utils import bulk_update_cases
from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from corehq.util.log import with_progress_bar

from custom.enikshay.duplicate_ids import get_cases_with_duplicate_ids, add_debug_info_to_cases


class Command(BaseCommand):
    help = """
    Finds cases with duplicate IDs and marks all but one of each ID as a duplicate
    """
    already_seen = set()
    logfile_fields = ['case_id', 'readable_id', 'opened_on']
    logfile_debug_fields = ['form_name', 'username', 'device_number_in_form', 'real_device_number']

    def add_arguments(self, parser):
        parser.add_argument('domain')
        parser.add_argument('case_type')
        parser.add_argument(
            '--commit',
            action='store_true',
            dest='commit',
            default=False,
        )
        parser.add_argument(
            '--debug_info',
            action='store_true',
            dest='debug_info',
            default=False,
        )

    def handle(self, domain, case_type, **options):
        self.domain = domain
        self.case_type = case_type
        commit = options['commit']
        self.debug_info = options['debug_info']

        filename = '{}-{}.csv'.format(self.__module__,
                                      datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S'))
        print("Logging actions to {}".format(filename))
        with open(filename, 'w') as f:
            if self.debug_info:
                logfile = csv.DictWriter(f, self.logfile_fields + self.logfile_debug_fields)
            else:
                logfile = csv.DictWriter(f, self.logfile_fields)
            logfile.writeheader()
            for chunk in chunked(self.get_updates(logfile), 100):
                if commit:
                    bulk_update_cases(self.domain, chunk, self.__module__)

    def get_updates(self, logfile):
        accessor = CaseAccessors(self.domain)
        print("Fetching all case ids")
        case_ids = accessor.get_case_ids_in_domain(self.case_type)
        print("Finding duplicates")
        bad_cases = get_cases_with_duplicate_ids(self.domain, self.case_type, case_ids)
        if self.debug_info:
            print("Adding debug info to cases")
            add_debug_info_to_cases(bad_cases, full_debug_info=True)
        print("Processing duplicate cases")
        for case in bad_cases:
            yield (case['case_id'], {'has_duplicate_id': 'yes'}, False)
            logfile.writerow(case)
