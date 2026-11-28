# Development execution

Install Docker Desktop/Compose and Git only. From repository root copy `.env.example` to `.env`, choose random database/root passwords and a random Django secret of at least 32 characters. Never commit `.env`. Set CSRF trusted origins for the local ports you actually use. Run `docker compose up -d --build --wait`.

Open public website `http://localhost:5173`, student login `/login`, staff/manager login `/staff/login`, administrator login `/control/login`. Nginx gateway is `http://localhost:8080` (include it in CSRF trusted origins). API Swagger `http://localhost:8000/api/docs/`; restricted maintenance tool `/admin/`. The administrator React login intentionally uses `/control/login` because `/admin/` is reserved for Django maintenance.

Services: MySQL 8.0, Redis, one migration job, backend, frontend, Celery worker, Celery Beat and Nginx. Worker/Beat start after migration and Redis. `docker compose ps` and `docker compose logs --tail=100 backend celery-worker celery-beat nginx` show status. Database/Redis ports are not published. Source reload is enabled for Django/Vite. Changes to worker task code require `docker compose restart celery-worker celery-beat`.

Create the initial local administrator with `docker compose exec backend python manage.py createsuperuser`. React configuration manages departments, categories, forms, memberships, roles, calendars and content. Initial employee/user creation still uses the restricted maintenance tool; React user management is backlog work. Existing support accounts need explicit memberships; legacy unclassified tickets require administrator classification before ordinary staff can see them.

Optional synthetic demonstration accounts:

```powershell
$env:E2E_TEST_PASSWORD = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
docker compose exec -T -e E2E_TEST_PASSWORD=$env:E2E_TEST_PASSWORD backend python manage.py seed_e2e_data
```

Accounts: `e2e_student`, `e2e_other_student`, `e2e_support`, `e2e_manager`, `e2e_admin`. They all use that operator-generated development password. Seed refuses production mode and short passwords. It updates these synthetic accounts and upserts one demonstration IT department/category/form/calendar/SLA/help article/FAQ/announcement. It does not seed the entire suggested university hierarchy, all roles or every lifecycle state. Browser runs leave clearly synthetic tickets and configuration records in the development database.

Checks:

```powershell
docker compose exec -T backend python manage.py check
docker compose exec -T backend python manage.py makemigrations --check --dry-run
docker compose exec -T backend python manage.py test --noinput
docker compose exec -T backend python manage.py spectacular --validate --file /tmp/schema.yml
docker compose exec -T frontend npm run lint
docker compose exec -T frontend npm test
docker compose exec -T frontend npm run build
docker compose exec -T frontend npm audit --audit-level=high
docker run --rm --init --ipc=host --network university-support_default --volumes-from university-support-frontend-1 -w /app -e PLAYWRIGHT_BASE_URL=http://frontend:5173 -e E2E_TEST_PASSWORD mcr.microsoft.com/playwright:v1.65.1-noble npm run test:e2e
```

Adjust network/container prefix when COMPOSE_PROJECT_NAME differs. Quality tools run in a disposable Python container using `backend/requirements-quality.txt`; no host Python/Node is needed. MySQL tests create/drop only `test_<database>` with scoped privileges provided by the initialization script. Never use SQLite or delete volumes to fix a test failure. `docker compose down` keeps volumes; volume deletion is destructive and requires explicit approval.
