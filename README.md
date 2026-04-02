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

### CI (Jenkins) и образы в GitHub Container Registry (GHCR)

Конвейер: [`Jenkinsfile`](Jenkinsfile). **Docker Hub не нужен** — образы пушатся в [**GitHub Container Registry**](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry) (`ghcr.io`), для публичных пакетов это **бесплатно**.

| Этап | Что делает |
|------|------------|
| **Backend** | `pytest` в `backend/` |
| **E2E** | uvicorn + Playwright (`NEXT_PUBLIC_API_URL` для dev = `127.0.0.1:8000`) |
| **Docker build and push** | Только ветки **`main`** / **`master`**: `docker build` → `docker push` в `ghcr.io/<GHCR_OWNER>/encar-landing-api` и `.../encar-landing-web` |

**Агент Jenkins:** Linux, **Docker CLI + daemon** (пользователь агента в группе `docker` или socket), Python 3.12+, Node 22+, `curl`, Chromium для Playwright.

**Учётные данные GHCR в Jenkins:** тип **Username with password**, id **`ghcr-pat`**: *Username* = логин GitHub, *Password* = [Personal Access Token](https://github.com/settings/tokens) с правами **`write:packages`**, **`read:packages`** (и при необходимости `delete:packages`). В классическом Jenkins: *Manage Jenkins → Credentials*.

**Параметры сборки (Build with Parameters):**

- **`IMAGE_TAG`** — тег образов (например `latest` или `v1.0.0`).
- **`NEXT_PUBLIC_API_URL`** — URL API **для браузера в проде** (вшивается в Next.js при сборке образа `web`). Для релиза укажите реальный `https://...`.
- **`GHCR_OWNER`** — пользователь или организация GitHub (по умолчанию `alex-zaporozhan`; при форке смените).

После первого push откройте на GitHub **Packages** → пакет `encar-landing-api` / `encar-landing-web` → *Package settings* → **Change visibility** → Public (если нужен pull без логина на VPS).

При падении E2E в артефактах — `frontend/playwright-report/`.

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

Переменные для **сборки и рантайма** (файл `.env` в корне репозитория рядом с `docker-compose.yml`, не коммитить):

| Переменная | Назначение |
|------------|------------|
| `NEXT_PUBLIC_API_URL` | Полный URL API **для браузера** (вшивается в фронт при `docker compose build`). Локально: `http://localhost:8000` или `http://IP_СЕРВЕРА:8000`. |
| `CORS_ORIGINS` | Origin сайта с фронтом, через запятую. Должен совпадать с тем, что пользователь вводит в адресной строке (`https://...`). |

```bash
docker compose build
docker compose up -d
```

- API: порт **8000**, том `encar_data` → `/data/encar.db`.
- Web: порт **3000**.

Проверка после деплоя:

```bash
curl -s http://localhost:8000/api/v1/health
```

Обновить каталог внутри контейнера:

```bash
docker compose exec api python -m app.jobs.fetch_encar
```

---

## Деплой на VPS с GHCR (без сборки на сервере)

Если Jenkins уже пушит образы в **ghcr.io**, на VPS достаточно `pull`, без `docker compose build`.

1. Установите Docker + Compose (как ниже).
2. Клонируйте репозиторий (нужны только `docker-compose.ghcr.yml` и `.env`).
3. Создайте `.env`:

```env
GHCR_OWNER=alex-zaporozhan
IMAGE_TAG=latest
CORS_ORIGINS=https://ваш-сайт,https://www.ваш-сайт
```

4. Если пакеты **приватные**, один раз:  
   `echo ВАШ_PAT | docker login ghcr.io -u ВАШ_GITHUB_LOGIN --password-stdin`  
   (PAT с `read:packages`.)

5. Запуск:

```bash
docker compose -f docker-compose.ghcr.yml pull
docker compose -f docker-compose.ghcr.yml up -d
docker compose -f docker-compose.ghcr.yml exec api python -m app.jobs.fetch_encar
```

Обновление после нового релиза: `docker compose -f docker-compose.ghcr.yml pull && docker compose -f docker-compose.ghcr.yml up -d`.

**Важно:** URL API в браузере зашит в образ **`web`** на этапе Jenkins — при смене домена API пересоберите образ в Jenkins с новым `NEXT_PUBLIC_API_URL` и снова `pull` на VPS.

---

## Деплой на VPS (сборка образов на сервере)

Если GHCR не используете — собирайте из исходников на машине (см. раздел **Docker Compose** выше).

### 1. Сервер

- Ubuntu 22.04+ (или аналог), открыты порты **22** (SSH), **80/443** (если сразу ставите nginx + HTTPS) или временно **3000** и **8000** для проверки.

Установите Docker Engine и плагин Compose ([официальная инструкция](https://docs.docker.com/engine/install/ubuntu/)).

### 2. Клон и переменные

```bash
sudo apt update && sudo apt install -y git
git clone https://github.com/alex-zaporozhan/parsing_encar_-_new_landing_page.git
cd parsing_encar_-_new_landing_page
```

Создайте `.env` в **корне** репозитория (рядом с `docker-compose.yml`):

**Вариант A — быстрый тест по IP (без домена):**

```env
NEXT_PUBLIC_API_URL=http://ВАШ_IP:8000
CORS_ORIGINS=http://ВАШ_IP:3000
```

**Вариант B — один домен и nginx впереди (рекомендуется для прод):**  
Проксируйте `https://example.com` → контейнер `web:3000`, а `https://example.com/api` → префикс FastAPI (нужен nginx с `location /api/` → `proxy_pass` на `http://127.0.0.1:8000` с нужным `strip`/префиксом) **или** отдельный поддомен `https://api.example.com` → порт 8000. Тогда, например:

```env
NEXT_PUBLIC_API_URL=https://api.example.com
CORS_ORIGINS=https://example.com
```

После **любого** изменения `NEXT_PUBLIC_API_URL` нужна пересборка фронта: `docker compose build web --no-cache` (или полный `docker compose build`).

### 3. Запуск

```bash
docker compose build
docker compose up -d
docker compose exec api python -m app.jobs.fetch_encar
```

Проверка: `curl -s http://127.0.0.1:8000/api/v1/health`, в браузере — `http://ВАШ_IP:3000` (или домен через nginx).

### 4. Обновление кода

```bash
cd parsing_encar_-_new_landing_page
git pull
docker compose build
docker compose up -d
```

### 5. Расписание импорта ENCAR

Используйте **cron** на VPS (раздел ниже), подставив путь к проекту и вызов:

`docker compose exec -T api python -m app.jobs.fetch_encar`

(или отдельный systemd timer).

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
