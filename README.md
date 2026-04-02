# ENCAR Selection — парсер + лендинг

Монорепозиторий: Python **FastAPI** + **SQLite**, фронт **Next.js** + **Tailwind**. Каталог подтягивается с официального JSON API encar.com (см. раздел «Источник данных»).

## Ссылки сдачи

| | URL |
|---|-----|
| **Код (репозиторий)** | [github.com/alex-zaporozhan/parsing_encar_-_new_landing_page](https://github.com/alex-zaporozhan/parsing_encar_-_new_landing_page) |
| **Работающий лендинг** | `https://YOUR_DOMAIN` — подставьте URL после деплоя (VPS / PaaS). |

Обновление каталога: **cron** на сервере или **расписание в Jenkins** — примеры ниже.

---

## Быстрый старт (локально)

### 1. Каталог ENCAR → SQLite

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
copy ..\.env.example .env       # при необходимости поправьте SQLITE_PATH
python -m app.jobs.fetch_encar
```

База по умолчанию: `data/encar.db` (от корня репозитория).

### 2. API

```bash
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Проверка: [http://127.0.0.1:8000/api/v1/health](http://127.0.0.1:8000/api/v1/health) · Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 3. Лендинг

```bash
cd frontend
npm install
set NEXT_PUBLIC_API_URL=http://127.0.0.1:8000   # Windows cmd
npm run dev
```

Откройте [http://localhost:3000](http://localhost:3000).

**Два origin (браузер → API):** задайте `CORS_ORIGINS` в `.env` бэкенда — по умолчанию разрешены **`http://localhost:3000`** и **`http://127.0.0.1:3000`** (разные Origin при обращении к Next). Фронт ходит на API по **`NEXT_PUBLIC_API_URL`** (полный URL, видимый из браузера).

**Один origin (reverse proxy):** nginx отдаёт и `/`, и проксирует `/api` на бэкенд — тогда можно выставить `NEXT_PUBLIC_API_URL` на тот же хост без порта.

**HTTPS лендинг + HTTP API:** браузер может блокировать mixed content. В проде выставьте API на **HTTPS** или проксируйте `/api` с того же origin, что и фронт.

---

## Тесты и QA (автоматизация)

### Backend (pytest)

Из каталога `backend`:

```bash
pip install -r requirements.txt
pytest -q
```

Покрыто: health, форма ответа `vehicles`, 422, **CORS preflight OPTIONS** (`tests/test_api_smoke.py`).

Коротко из корня репозитория (GNU Make / Git Bash / WSL): `make qa-api`. E2E: `make qa-e2e` (предварительно поднять API на `:8000`).

### E2E (Playwright)

1. Запустите API: `uvicorn app.main:app --host 127.0.0.1 --port 8000`.
2. В другом терминале, из `frontend`:

```bash
set NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
npm run test:e2e
```

Первый раз: `npx playwright install chromium`. Базовый URL тестов: **`http://localhost:3000`** (совпадает с CORS). Playwright поднимает `next dev` сам; если порт занят — используется существующий сервер.

Сценарии: загрузка каталога / empty, горизонтальный скролл (viewport), ссылка на encar.com, мок 500 с контрактом ошибки, OPTIONS.

### CI (Jenkins)

Конвейер в корне: [`Jenkinsfile`](Jenkinsfile) (Declarative Pipeline).

1. **Backend** — `python3 -m pytest -q` в `backend/`.
2. **E2E** — в одном шаге: `uvicorn` на `127.0.0.1:8000`, ожидание `/api/v1/health`, затем `npm ci`, Playwright (`NEXT_PUBLIC_API_URL` / `E2E_API_URL` → этот API).

**Настройка:** New Item → Pipeline → *Pipeline script from SCM*, указать репозиторий и ветку; путь к скрипту — `Jenkinsfile`. Нужен **Linux-агент** с bash, Python 3.12+, Node 20+, `curl`; для Chromium — `npx playwright install --with-deps` (уже в шаге E2E). При падении E2E в артефактах сохраняется `frontend/playwright-report/`.

Docker Hub и облачные CI для этого репозитория **не обязательны** — сборка и тесты идут на вашем Jenkins.

### Артефакты отчёта

- `docs/artifacts/QA_RUN_ENC_LANDING.md` — актуальный прогон и статусы **PASS (executed)**.
- `docs/artifacts/QA_ARCH_REVIEW_QA_RUN_ENC_LANDING.md` — мета-аудит работы @QA (закрыт после внедрения E2E).

### Метаданные для отчёта (вручную)

```bash
git rev-parse HEAD
node -v
python --version
```

---

## Docker Compose

```bash
docker compose build
docker compose up -d
```

- API: порт **8000**, том `encar_data` → `/data/encar.db`.
- Web: порт **3000**, образ собирается с `NEXT_PUBLIC_API_URL=http://localhost:8000` (браузер с хоста машины).

Проверка после деплоя:

```bash
curl -s http://localhost:8000/api/v1/health
```

Обновить каталог внутри контейнера:

```bash
docker compose exec api python -m app.jobs.fetch_encar
```

---

## Cron (1 раз в сутки)

Пример **Linux**, 03:00 по времени сервера:

```cron
0 3 * * * cd /path/to/parser_landing/backend && /path/to/.venv/bin/python -m app.jobs.fetch_encar >> /var/log/encar_fetch.log 2>&1
```

**UTC** явно:

```cron
0 3 * * * TZ=UTC ...
```

**Jenkins** (отдельный job «fetch», не путать с CI из `Jenkinsfile`): расписание **Build periodically**, например `H 3 * * *` (около 03:00), шаги — checkout SCM, `pip install -r backend/requirements.txt`, `cd backend && python3 -m app.jobs.fetch_encar`. Для постоянной SQLite укажите **workspace** на том же каталоге, что и прод, или монтируйте `data/` — иначе БД на агенте будет временной. Для продакшена чаще удобнее **cron на VPS** (раздел выше).

---

## Ограничения и этика

- Используется публичный **HTTPS API** `api.encar.com` с теми же параметрами, что и веб-клиент (листинг «премиум» / иностранные авто). Между запросами — **пауза** `ENCAR_REQUEST_DELAY_SEC`.
- Указан идентифицируемый **`ENCAR_USER_AGENT`** (замените контакт в `.env`).
- Перед промышленным использованием проверьте **ToS / robots.txt** encar.com и нагрузку на API.
- Ссылка **«Смотреть на ENCAR»** по умолчанию — **fem.encar.com** (актуальный фронт). Старый `fc_cardetailview.do` снаружи часто даёт **502**; при отдаче **`GET /api/v1/vehicles`** API **подменяет** такие URL на шаблон из `ENCAR_DETAIL_URL_TEMPLATE`, даже если в SQLite ещё лежит legacy-строка. Импорт (`fetch_encar`) всё равно стоит периодически запускать для свежих данных.

Источник разведки зафиксирован в комментарии к `backend/app/jobs/fetch_encar.py`.

---

## Переменные окружения

См. **`.env.example`** в корне. Основное:

| Переменная | Назначение |
|------------|------------|
| `SQLITE_PATH` | Путь к файлу SQLite |
| `CORS_ORIGINS` | Список origin через запятую |
| `ENCAR_*` | URL листинга, запрос `q`, пагинация, задержка, лимиты, шаблон карточки `ENCAR_DETAIL_URL_TEMPLATE` |
| `NEXT_PUBLIC_API_URL` | Базовый URL API для браузера |

---

## Архитектура

Канон: `docs/artifacts/ARCH_ENC_LANDING.md` · исполнение: `docs/artifacts/DEV_PROMPTS_ENC_LANDING.md`.

---

## Отчёт разработчика

| Компонент | Команда / путь |
|-----------|----------------|
| Парсер / job | `backend/app/jobs/fetch_encar.py` · `python -m app.jobs.fetch_encar` из каталога `backend` |
| API | `uvicorn app.main:app --host 0.0.0.0 --port 8000` |
| Фронт | `cd frontend && npm run dev` / `npm run build && npm start` |
| SQLite | Файл по `SQLITE_PATH` (по умолчанию `data/encar.db`) — бэкап: копирование файла в оффлайн-хранилище |
