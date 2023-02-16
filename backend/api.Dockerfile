FROM python:3.10-slim
# not using alpine because of numpy

# Ref: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

ENV PORT=5000
ARG REQUIREMENTS_TXT=api.requirements.txt

WORKDIR /usr/src/app

COPY $REQUIREMENTS_TXT ./
RUN pip install --no-cache-dir -r $REQUIREMENTS_TXT

COPY . .

# Note that interface "0.0.0.0" has to be used
CMD python -m flask --app api_server:app --debug run --host 0.0.0.0 --port $PORT

# Use e.g. `waitress` in prod: https://flask.palletsprojects.com/en/2.2.x/tutorial/deploy/#run-with-a-production-server
#CMD [ "waitress-serve", "--call", "app.app:app" ]