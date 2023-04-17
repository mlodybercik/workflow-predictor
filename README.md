# workflow-predictor
Zespołowe Przedsięwzięcie Inżynierskie, projekt dla Credit Suisse

## Pisanie kodu u siebie
Najsampierw będziemy potrzebowali `pipenv`, dalej potrzebujemy zsynchronizować paczki żeby klepać w tym samym środowisku. U siebie korzystam z pythona 3.9, więc wy też musicie (w 3.8 weszło `:=` a w 3.9 `str.removesuffix/prefix`). Jak zainstalujecie paczki (te deweloperskie też), to musicie odpalić to środowisko. W tym środowisku dalej musicie zainstalować hooki `pre-commit`'a (zanim coś wsadzicie do commita, bedzie musiało przejść jakieś testy żeby ten kod przynajmniej jakoś wyglądał). W tym momencie możecie pracować. Jak będziecie coś dodawali to `git commit ...` będzie wykonywało te testy.
```bash
python3 -m pip install pipenv
pipenv install --dev
pipenv shell
pre-commit install
```
Uruchamianie kodu to:
- jeśli masz Dockera zainstalowanego to `docker compose build`, `docker compose up`,
- jeśli nie, to serwer odpalasz `python src/app.py`.
Oba podejścia dają praktycznie to samo, ale Docker daje środowisko produkcyjne. W obu przypadkach aplikacja będzie dostępna pod: `http://localhost:5000` (albo innym jak stawiasz na jakimś remote serwerze).

## Dane
Do pracy wrzućcie sobie dane do folderu `data/`, wyłączyłem w gitignore ten duży plik co dostaliśmy od Grzesia żeby go w tej formie nie trzymać.
W rubryce params znajdują się następujące parametry:
```python
{'processing-location', 'bsinp-run-id', 'api-version', 'correlation-id', 'flow-type', 'batch-workflow', 'rd-run-id', 'batch-instance-seq', 'chf-usd-rate', 'skip-mdl-out', 'pb-run-id', 'setenv', 'regulatory-approaches', 'business-date', 'skip-mdl-landing', 'ib-run-id', 'as-of-date', 'failed-job-status', 'as-of-datetime', 'failed-job-uid', 'source-type', 'rules-branch', 'failed-job-id', 'scenario-workflow', 'process-flag', 'hac-run-id', 'business-day'}
```
te parametry to są wszystkie jakie istnieją, prawdopodobnie nie potrzebujemy wszystkich.

|uid|parent_uid|kafka_offset|cmd_time|event_time|workflow_name|job_name|business_date|params|status|skip-mdl-out|rd-run-id|as-of-date|pb-run-id|rules-branch|hac-run-id|api-version|skip-mdl-landing|as-of-datetime|failed-job-id|ib-run-id|batch-workflow|failed-job-uid|processing-location|batch-instance-seq|business-date|business-day|chf-usd-rate|setenv|process-flag|regulatory-approaches|correlation-id|failed-job-status|flow-type|scenario-workflow|bsinp-run-id|source-type|
|---|----------|------------|--------|----------|-------------|--------|-------------|------|------|------------|---------|----------|---------|------------|----------|-----------|----------------|--------------|-------------|---------|--------------|--------------|-------------------|------------------|-------------|------------|------------|------|------------|---------------------|--------------|-----------------|---------|-----------------|------------|-----------|
|1be997ff0fa411ed9efe4be67384bf3f||546082|2022-07-30 05:08:24.0|2022-07-30 05:08:24.0|strategic-flow|f1-notification-trigger|2022-07-29||PROCESSING|||2022-07-29||||||2022-07-30_03.08.13|||STRATEGIC_PAC||PAC||2022-07-29|BD0|||||||STRATEGIC||||
|1be997ff0fa411ed9efe4be67384bf3f||546084|2022-07-30 05:08:24.0|2022-07-30 05:08:24.0|strategic-flow|f1-notification-trigger|2022-07-29||SUCCESS|||2022-07-29||||||2022-07-30_03.08.13|||STRATEGIC_PAC||PAC||2022-07-29|BD0|||||||STRATEGIC||||
|1bf0c3f00fa411ed9efe75307937e094|1be997ff0fa411ed9efe4be67384bf3f|546086|2022-07-30 05:08:24.0|2022-07-30 05:08:24.0|strategic-flow|open-date-card|2022-07-29||SUBMITTED|||2022-07-29||||||2022-07-30_03.08.13|||STRATEGIC_PAC||PAC||2022-07-29|BD0|||||||STRATEGIC||||
|1bf0c3f00fa411ed9efe75307937e094|1be997ff0fa411ed9efe4be67384bf3f|546088|2022-07-30 05:08:24.0|2022-07-30 05:08:24.0|strategic-flow|open-date-card|2022-07-29||PROCESSING|||2022-07-29||||||2022-07-30_03.08.13|||STRATEGIC_PAC||PAC||2022-07-29|BD0|||||||STRATEGIC||||
|1bf0c3f00fa411ed9efe75307937e094|1be997ff0fa411ed9efe4be67384bf3f|546090|2022-07-30 05:08:24.0|2022-07-30 05:08:25.0|strategic-flow|open-date-card|2022-07-29||SUCCESS|||2022-07-29||||||2022-07-30_03.08.13|||STRATEGIC_PAC||PAC||2022-07-29|BD0|||||||STRATEGIC||||

Tutaj zostawiam te które moim zdaniem (Przemek) mają najwięcej w sobie informacji.
flow-type|event_time|hac-run-id|status|batch-workflow|as-of-datetime|batch-instance-seq|regulatory-approaches|uid|business_date|parent_uid|as-of-date|business-day|processing-location|workflow_name|job_name|rules-branch|ib-run-id|skip-mdl-out|business-date|cmd_time
---------|----------|----------|------|--------------|--------------|------------------|---------------------|---|-------------|----------|----------|------------|-------------------|-------------|--------|------------|---------|------------|-------------|--------
STRATEGIC|2022-07-30 05:08:24.0||PROCESSING|STRATEGIC_PAC|2022-07-30_03.08.13|||1be997ff0fa411ed9efe4be67384bf3f|2022-07-29||2022-07-29|BD0|PAC|strategic-flow|f1-notification-trigger||||2022-07-29|2022-07-30 05:08:24.0
STRATEGIC|2022-07-30 05:08:24.0||SUCCESS|STRATEGIC_PAC|2022-07-30_03.08.13|||1be997ff0fa411ed9efe4be67384bf3f|2022-07-29||2022-07-29|BD0|PAC|strategic-flow|f1-notification-trigger||||2022-07-29|2022-07-30 05:08:24.0
STRATEGIC|2022-07-30 05:08:24.0||SUBMITTED|STRATEGIC_PAC|2022-07-30_03.08.13|||1bf0c3f00fa411ed9efe75307937e094|2022-07-29|1be997ff0fa411ed9efe4be67384bf3f|2022-07-29|BD0|PAC|strategic-flow|open-date-card||||2022-07-29|2022-07-30 05:08:24.0

### Zły YAML
Zacznę od tego, że YAML'e które dostaliśmy były błędnie zapisane, osoba która je tworzyła nie sprawdziła potem czy się w ogóle otworzy. Linijki z niego były usuwane z palca, nie skryptem, bo w jednym miejscu ktoś usunął deklaracje słownika. Dalej kwestia cudzysłowiów, wszystkie biblioteki (YAML'owe) które przetestowałem, nie radzą sobię z tym, że w niektórych linijkach pojawia się dwa razy dwukropek, bez żadnego cudzysłowia.

### CSV
W pliku csv, `workflow_name` nie wskazuje jednoznacznie na workflow z którego trzeba korzystać. Unikatowych tasków jest 61, w `securitization-flow.yml` jest 28 zadań, w `strategic-flow.yml` w 41 (`69 != 61`). Czym jest `parent_id` skoro istnieje grupka eventów gdzie cały graf zaczyna się wykonywać w środku?

## Źródła
(prawdopodobnie bedziecie potrzebowali proxy uczelnianego)

Dwuetapowe podejście z uczeniem maszynowym do estymacji w zależności od parametrów długości czasów wykonywania zadań.
[Predicting Workflow Task Execution Time in the Cloud using A Two-Stage Machine Learning Approach](https://core.ac.uk/download/pdf/144872471.pdf)

Wybór parametrów wpływających na długość wykonywania zadań.
[Performance Modeling and Prediction of Big Data Workflows: An Exploratory Analysis](https://par.nsf.gov/servlets/purl/10212855)

Mniej ważne gówno nt. *statystycznego* podejścia do estymacji czasu wykonywania całego workflowa z DAG'a.
[Characterizing Co-Located Workloads in Alibaba Cloud Datacenters](https://ieeexplore.ieee.org/abstract/document/9242282)

A tutaj to samo, ale nie statystyczne.
[Workflow performance prediction based on graph structure aware deep attention neural network](https://www.sciencedirect.com/science/article/pii/S2452414X22000097)
