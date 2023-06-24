FROM python:3.9.16-slim AS base

ENV PIPENV_VENV_IN_PROJECT=1 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1

FROM base AS builder
# install pipenv
RUN pip install --user pipenv

# move Pipfiles into working directory
ADD Pipfile.lock Pipfile .

# download all packages
RUN /root/.local/bin/pipenv install --deploy --verbose

FROM base as runtime
WORKDIR /app/
COPY --from=builder .venv .venv

ADD src ./

CMD [".venv/bin/python", "-m", "gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "predictor:get_app()"]