from __future__ import absolute_import
from __future__ import unicode_literals
import logging
from django.utils.translation import ugettext_lazy as _


LOG_LEVEL_CHOICES = (
    (99, 'Disable logging'),
    (logging.ERROR, 'Error'),
    (logging.INFO, 'Info'),
)

IMPORT_FREQUENCY_WEEKLY = 'weekly'
IMPORT_FREQUENCY_MONTHLY = 'monthly'
IMPORT_FREQUENCY_CHOICES = (
    (IMPORT_FREQUENCY_WEEKLY, _('Weekly')),
    (IMPORT_FREQUENCY_MONTHLY, _('Monthly')),
)


XMLNS_OPENMRS = 'http://commcarehq.org/openmrs-integration'  # Form XMLNS to indicate imported from OpenMRS

# To match cases against their OpenMRS Person UUID, in case config (Project Settings > Data Forwarding > Forward to
# OpenMRS > Configure > Case config) "patient_identifiers", set the identifier's key to the value of
# PERSON_UUID_IDENTIFIER_TYPE_ID. e.g.::
#
#     "patient_identifiers": {
#         /* ... */
#         "uuid": {
#             "doc_type": "CaseProperty",
#             "case_property": "openmrs_uuid",
#         }
#     }
#
# To match against any other OpenMRS identifier, set the key to the UUID of the OpenMRS Identifier Type. e.g.::
#
#     "patient_identifiers": {
#         /* ... */
#         "e2b966d0-1d5f-11e0-b929-000c29ad1d07": {
#             "doc_type": "CaseProperty",
#             "case_property": "nid"
#         }
#     }
#
PERSON_UUID_IDENTIFIER_TYPE_ID = 'uuid'
