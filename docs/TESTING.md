## 10. Tests and CI

The repository uses pytest/pytest-django. The GitHub Actions workflow is
`.github/workflows/ci.yml`.

It runs on pushes and pull requests targeting `main` and `develop`, and
can also be started manually. The job uses Python 3.12 and a PostgreSQL
16 pgvector service, installs both root and Drive service requirements,
enables the vector extension, and runs:

```bash
PYTHONPATH=. python -m pytest
```

Useful local checks:

```bash
python manage.py check
python -m compileall core apps Workflow RagCore drive_service
PYTHONPATH=. python -m pytest
```

CI currently provides **continuous integration/testing**. The inspected
workflow does not build and publish Docker images or deploy the
application. There is no deployment workflow in `.github/workflows/` on
the reviewed branch.
