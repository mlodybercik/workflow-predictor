FROM python:3.9.16-buster

# install pipenb
ENV PIPENV_VENV_IN_PROJECT=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN pip install --user pipenv

# move Pipfiles into working directory
ADD Pipfile.lock Pipfile /usr/src/
WORKDIR /usr/src

# download all packages
RUN /root/.local/bin/pipenv sync

ADD src ./
CMD [".venv/bin/python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "-w", "2", "predictor:get_app()"]