FROM acait/django-container:1.0.6 as django

USER root
RUN apt-get update
RUN apt-get install -y libpq-dev
RUN apt-get install -y postgresql-client-10

USER acait

ADD --chown=acait:acait ./docker /app/
ADD --chown=acait:acait ./setup.py /app/
ADD --chown=acait:acait ./uw_saml /app/uw_saml

WORKDIR /app/

RUN . /app/bin/activate && pip install .