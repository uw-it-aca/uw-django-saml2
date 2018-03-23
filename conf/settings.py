UW_SAML = {
    "strict": True,
    "debug": True,
    "sp": {
        "entityId": "https://example.uw.edu/saml2",
        "assertionConsumerService": {
            "url": "https://example.uw.edu/Shibboleth.sso/SAML2/POST",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified",
        "x509cert": "",
        "privateKey": ""
    },
    "idp": {
        "entityId": "urn:mace:incommon:washington.edu",
        "singleSignOnService": {
            "url": "https://idp.u.washington.edu/idp/profile/SAML2/Redirect/SSO",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "x509cert": "",
    },
    "security": {
        # for 2FA you would uncomment this line.
        # "requestedAuthnContext":  ["urn:oasis:names:tc:SAML:2.0:ac:classes:TimeSyncToken"]
    }
}
