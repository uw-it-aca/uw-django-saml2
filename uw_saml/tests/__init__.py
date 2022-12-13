# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0


MOCK_SAML_ATTRIBUTES = {
    'urn:oid:0.9.2342.19200300.100.1.1': ['javerage'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': ['student'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': ['javerage@washington.edu'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': ['student@washington.edu'],
    'urn:oid:1.3.6.1.4.1.5923.1.5.1.1': [
        'urn:mace:washington.edu:groups:u_test_group',
        'urn:mace:washington.edu:groups:u_test2_group'],
    'urn:oid:2.5.4.4': ['Average'],
    'urn:oid:2.5.4.42': ['J'],
}

MOCK_SESSION_ATTRIBUTES = {
    'uwnetid': ['javerage'],
    'affiliations': ['student'],
    'eppn': ['javerage@washington.edu'],
    'scopedAffiliations': ['student@washington.edu'],
    'isMemberOf': ['u_test_group', 'u_test2_group'],
}

UW_SAML_PERMISSIONS = {
    'perm1': 'u_test_group',
    'perm2': 'u_test_another_group',
}

DJANGO_LOGIN_MOCK_SAML = {
    'NAME_ID': 'test-mock-nameid',
    'SESSION_INDEX': 'test-mock-session',
    'SAML_USERS': [
        {
            "username": "test_username",
            "password": "test_password",
            "email": "test_email",
            "MOCK_ATTRIBUTES": {
                'uwnetid': ["test_username"],
                'affiliations': ['student', 'member'],
                'eppn': ['javerage@washington.edu'],
                'scopedAffiliations': [
                    'student@washington.edu',
                    'member@washington.edu'
                ],
                'isMemberOf': [
                    UW_SAML_PERMISSIONS['perm1'],
                    UW_SAML_PERMISSIONS['perm2']
                ],
            }
        }
    ]
}


def update_user(user, attributes):
    if 'givenName' in attributes:
        user.first_name = attributes.get('givenName')

    if 'surname' in attributes:
        user.last_name = attributes.get('surname')

    user.save(update_fields=['first_name', 'last_name'])
