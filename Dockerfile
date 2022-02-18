FROM gcr.io/uwit-mci-axdd/django-container:1.3.8 as app-container

USER acait

ADD --chown=acait:acait ./docker /app/
ADD --chown=acait:acait ./setup.py /app/
ADD --chown=acait:acait ./uw_saml /app/uw_saml

WORKDIR /app/

RUN . /app/bin/activate && pip install .
RUN /app/bin/python manage.py migrate
