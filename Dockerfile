ARG DJANGO_CONTAINER_VERSION=3.0.2

FROM us-docker.pkg.dev/uwit-mci-axdd/containers/django-container:${DJANGO_CONTAINER_VERSION} AS app-container

USER acait

ADD --chown=acait:acait ./docker /app/
ADD --chown=acait:acait ./setup.py /app/
ADD --chown=acait:acait ./uw_saml /app/uw_saml

WORKDIR /app/

RUN . /app/bin/activate && pip install .
RUN /app/bin/python manage.py migrate
