# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


"""
Documentation for UW attributes is at
https://wiki.cac.washington.edu/display/infra/Guide+to+NameID+Formats+and+Attributes+Available+from+the+UW+IdP
"""
ATTRIBUTE_MAP = {
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': 'affiliations',
    'urn:oid:2.5.4.3': 'cn',
    'urn:oid:2.16.840.1.113730.3.1.241': 'displayName',
    'urn:oid:0.9.2342.19200300.100.1.3': 'email',
    'urn:oid:2.16.840.1.113730.3.1.3': 'employeeNumber',
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': 'eppn',
    'urn:oid:2.5.4.42': 'givenName',
    'urn:oid:2.5.4.11': 'homeDepartment',
    'urn:oid:1.3.6.1.4.1.5923.1.5.1.1': 'isMemberOf',  # gws_groups
    'urn:oid:1.2.840.113994.200.47': 'preferredFirst',
    'urn:oid:1.2.840.113994.200.48': 'preferredMiddle',
    'urn:oid:1.2.840.113994.200.49': 'preferredSurname',
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': 'scopedAffiliations',
    'urn:oid:2.5.4.4': 'surname',
    'urn:oid:1.2.840.113994.200.45': 'uwEduEmail',
    'urn:oid:1.2.840.113994.200.51': 'uwPronouns',
    'urn:oid:0.9.2342.19200300.100.1.1': 'uwnetid',
    'urn:oid:1.2.840.113994.200.24': 'uwregid',
    'urn:oid:1.2.840.113994.200.21': 'uwStudentID',
    'urn:oid:1.2.840.113994.200.20': 'uwStudentSystemKey',
}
