MOCK_SAML_ATTRIBUTES = {
    'urn:oid:0.9.2342.19200300.100.1.1': ['javerage'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.1': ['student'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.6': ['javerage@washington.edu'],
    'urn:oid:1.3.6.1.4.1.5923.1.1.1.9': ['student@washington.edu'],
    'urn:oid:1.3.6.1.4.1.5923.1.5.1.1': [
        'urn:mace:washington.edu:groups:u_test_group',
        'urn:mace:washington.edu:groups:u_test2_group'],
}


MOCK_SESSION_ATTRIBUTES = {
    'uwnetid': ['javerage'],
    'affiliations': ['student'],
    'eppn': ['javerage@washington.edu'],
    'scopedAffiliations': ['student@washington.edu'],
    'isMemberOf': ['u_test_group', 'u_test2_group'],
}
