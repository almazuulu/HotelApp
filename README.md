# HotelApp

Учебное веб-приложение для управления одной гостиницей: каталог номеров, бронирование, личный кабинет клиента и административная панель.

## Стек

- Backend: Python 3.13, Django 5.2 LTS, Django REST Framework 3.17, drf-spectacular и PostgreSQL 17.
- Frontend: React 19.2, TypeScript, Vite, React Router, TanStack Query, React Hook Form и React-Bootstrap.
- Локальная среда запуска: Docker Compose.

Дизайн интерфейса развивается на основе исходного шаблона `Hotelier_Template`.

## Требования

- Docker и Docker Compose v2 (проверено на Docker 29.5.3, Compose v5.1.4).
- Свободные порты `5432`, `8000` и `5173`. Их можно переопределить в `.env`.

Node.js и Python на хосте не нужны: сборка и запуск идут внутри контейнеров.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

Команда поднимает три контейнера:

| Сервис | Что это | Адрес |
|---|---|---|
| `db` | PostgreSQL 17 с healthcheck и постоянным volume | `localhost:5432` |
| `backend` | Django dev server с hot reload | http://localhost:8000 |
| `frontend` | Vite dev server с hot reload | http://localhost:5173 |

Доступные адреса:

- React SPA — http://localhost:5173
- Django admin — http://localhost:5173/admin/ (через Vite proxy)
- API v1 — http://localhost:8000/api/v1/
- Публичный CMS гостиницы — http://localhost:8000/api/v1/site/
- CSRF cookie — http://localhost:8000/api/v1/csrf/
- OpenAPI schema — http://localhost:8000/api/v1/schema/
- Swagger UI — http://localhost:8000/api/v1/docs/

`backend` дожидается готовности PostgreSQL и применяет миграции при каждом старте: Compose ждёт healthcheck сервиса `db`, а `backend/entrypoint.sh` дополнительно опрашивает базу через `pg_isready`.

Vite проксирует `/api` и `/media` на `backend`, поэтому в браузере SPA и API живут на одном origin: CORS не нужен, а сессионная cookie остаётся first-party.

Остановка и полная очистка локальных данных:

```bash
docker compose down            # остановить контейнеры
docker compose down -v         # плюс удалить volume базы, media и node_modules
```

## Полезные команды

```bash
docker compose config                      # проверить конфигурацию Compose
docker compose logs -f backend             # логи backend
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py check
docker compose exec backend pytest
docker compose exec backend ruff check .
docker compose exec backend python manage.py spectacular --file /tmp/schema.yaml --validate
docker compose exec frontend npm run typecheck
docker compose exec frontend npm run lint
docker compose exec frontend npm test
docker compose exec frontend npm run generate:api-types
```

## Session и CSRF

API использует только Django session cookie и CSRF — JWT в приложении отсутствует. SPA перед изменяющим session-auth запросом вызывает `GET /api/v1/csrf/`: endpoint устанавливает cookie `csrftoken`. Затем клиент отправляет cookie вместе с session cookie (`credentials: include`) и значение CSRF cookie в заголовке `X-CSRFToken`.

Для локального HTTP cookie имеют `SameSite=Lax`, session cookie — `HttpOnly`, CSRF cookie намеренно не `HttpOnly`, чтобы SPA могла прочитать её для заголовка. Vite проксирует API на тот же origin; `DJANGO_CSRF_TRUSTED_ORIGINS` в `.env` содержит адрес dev-server. HTTPS-атрибут cookie можно включить только через `DJANGO_COOKIE_SECURE=true` в среде с HTTPS.

Ошибки API всегда имеют форму `{ "code", "message", "errors" }`. Полный реестр из десяти стабильных кодов опубликован в OpenAPI как `ApiErrorCode`; account-клиент сопоставляет ошибки по этому коду, а не по тексту сообщения.

## Аккаунты

Публичный account API доступен по `/api/v1/auth/`:

- `POST register/`, `login/`, `logout/`;
- `GET/PATCH me/`;
- `POST password-reset/` и `password-reset/confirm/`.

Перед каждым изменяющим запросом `shared/api` запрашивает CSRF cookie и передаёт её в `X-CSRFToken`; session cookie отправляется с `credentials: include`. Типы DTO генерируются из OpenAPI: при изменении API запустите `docker compose exec frontend npm run generate:api-types` и зафиксируйте обновлённый `frontend/src/shared/api/generated/schema.d.ts`.

В local-среде письмо для сброса пароля печатается в лог backend. Ссылка в нём строится от `FRONTEND_BASE_URL` из `.env`.

## CMS гостиницы

`GET /api/v1/site/` — публичный read-only документ CMS: профиль одной гостиницы, hero-слайды, преимущества, контакты, footer и SEO. Сначала создайте единственный профиль в Django admin; второй профиль не создаётся ни через admin, ни на уровне базы данных. Менеджер или staff-пользователь с разрешениями `content` может редактировать этот контент в admin. Главная страница React получает его через `shared/api` и показывает понятное состояние с повторной попыткой, пока контент не опубликован.

Hero-слайды используют URL изображения; локальная безопасная загрузка файлов будет добавлена отдельной задачей media. Дизайн главной опирается на `Hotelier_Template`, при этом обязательная атрибуция HTML Codex сохранена в footer.

## Конфигурация

Все настройки читаются из окружения; `.env.example` описывает каждую переменную с безопасной локальной заглушкой. Реальный `.env`, данные PostgreSQL, media и `node_modules` не попадают в Git: `.env` игнорируется, а данные лежат в именованных Docker volume вне репозитория.

Бизнес-часовой пояс — `Asia/Bishkek`, язык интерфейса — русский, валюта — USD.

## Статус

Реализованы локальное окружение Docker Compose, Django/DRF и React каркасы, единый API-контракт, OpenAPI/Swagger, фиксированный CMS гостиницы и базовые backend/frontend quality gates.

Ещё не реализовано и появится в следующих задачах:

- команда `seed_demo` и демо-аккаунты из `.env`;
- доменные feature-модели и endpoint’ы, кроме account API и публичного CMS;
- SPA: каталог, бронирование, оплата и остальные публичные страницы;
- E2E-сценарии.

Этот README описывает только те команды, которые действительно работают сегодня. Планируемые команды добавляются сюда вместе с их реализацией.
