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
- Публичный каталог категорий — http://localhost:8000/api/v1/room-types/
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
docker compose exec backend pytest -c pytest-postgres.ini apps/inventory/tests/test_occupancy.py tests/test_occupancy_concurrency.py
docker compose exec backend ruff check .
docker compose exec backend python manage.py spectacular --file /tmp/schema.yaml --validate
docker compose exec frontend npm run typecheck
docker compose exec frontend npm run lint
docker compose exec frontend npm test
docker compose exec frontend npm run generate:api-types
docker compose exec frontend npm run api-types:check
docker compose exec frontend npm run check
```

Вторая команда `pytest` запускает PostgreSQL-набор занятости и concurrency: Django создаёт
отдельную test-базу, проверяет `btree_gist`, exclusion constraint и гонку за последний номер.
Обычный `pytest` остаётся быстрым SQLite-набором и намеренно не создаёт таблицу `RoomOccupancy`.

## Session и CSRF

API использует только Django session cookie и CSRF — JWT в приложении отсутствует. SPA перед изменяющим session-auth запросом вызывает `GET /api/v1/csrf/`: endpoint устанавливает cookie `csrftoken`. Затем клиент отправляет cookie вместе с session cookie (`credentials: include`) и значение CSRF cookie в заголовке `X-CSRFToken`.

Для локального HTTP cookie имеют `SameSite=Lax`, session cookie — `HttpOnly`, CSRF cookie намеренно не `HttpOnly`, чтобы SPA могла прочитать её для заголовка. Vite проксирует API на тот же origin; `DJANGO_CSRF_TRUSTED_ORIGINS` в `.env` содержит адрес dev-server. HTTPS-атрибут cookie можно включить только через `DJANGO_COOKIE_SECURE=true` в среде с HTTPS.

Ошибки API всегда имеют форму `{ "code", "message", "errors" }`. Полный реестр из десяти стабильных кодов опубликован в OpenAPI как `ApiErrorCode`; account-клиент сопоставляет ошибки по этому коду, а не по тексту сообщения.

## Аккаунты

Публичный account API доступен по `/api/v1/auth/`:

- `POST register/`, `login/`, `logout/`;
- `GET/PATCH me/`;
- `POST password-reset/` и `password-reset/confirm/`.

Перед каждым изменяющим запросом `shared/api` запрашивает CSRF cookie и передаёт её в `X-CSRFToken`; session cookie отправляется с `credentials: include`. Вне `frontend/src/shared/api` нет ни одного вызова fetch, CSRF-заголовка или `credentials` — сетевой адаптер ровно один. Тесты фич внедряют stub-адаптер (`src/test/stubApiClient.ts`) через `ApiClientContext` вместо мока глобального fetch.

Типы DTO генерируются из OpenAPI одной командой `docker compose exec frontend npm run generate:api-types`; обновлённый `frontend/src/shared/api/generated/schema.d.ts` фиксируется в репозитории, а его переводы строк закреплены как LF в `.gitattributes`. Свежесть типов проверяет `npm run api-types:check`: типы перегенерируются в памяти и сравниваются с закоммиченным файлом, при любом расхождении команда падает, поэтому устаревшие типы роняют проверку, а не предупреждают. Источник схемы по умолчанию `http://backend:8000/api/v1/schema/` внутри Compose; снаружи Docker задайте `OPENAPI_SCHEMA_URL` (например, `http://localhost:8000/...`) или передайте путь к файлу схемы позиционным аргументом. CI (`.github/workflows/frontend-api-contract.yml`) дампит схему оффлайн через `manage.py spectacular --format openapi-json` с настройками `config.settings.test` и запускает ту же проверку — без базы данных и секретов. Локально весь набор quality gates фронтенда запускается одной командой `npm run check` (typecheck, lint, test, api-types:check).

Decimal-поля (цены, площадь) приходят и хранятся строками и не парсятся во float; даты и время передаются ISO 8601-строками.

В local-среде письмо для сброса пароля печатается в лог backend. Ссылка в нём строится от `FRONTEND_BASE_URL` из `.env`.

## CMS гостиницы

`GET /api/v1/site/` — публичный read-only документ CMS: профиль одной гостиницы, hero-слайды, преимущества, контакты, footer и SEO. Сначала создайте единственный профиль в Django admin; второй профиль не создаётся ни через admin, ни на уровне базы данных. Менеджер или staff-пользователь с разрешениями `content` может редактировать этот контент в admin. Главная страница React получает его через `shared/api` и показывает понятное состояние с повторной попыткой, пока контент не опубликован.

Hero-слайды используют URL изображения; локальная безопасная загрузка файлов будет добавлена отдельной задачей media. Дизайн главной опирается на `Hotelier_Template`, при этом обязательная атрибуция HTML Codex сохранена в footer.

## Каталог номеров

`GET /api/v1/room-types/` возвращает все публичные категории номеров обычным массивом без
pagination. Ответ содержит только данные категории: цену и площадь как строки Decimal, лимиты
взрослых и детей, режим подтверждения, удобства и упорядоченную URL-галерею. Физические номера
и их ID в API не публикуются.

Список принимает необязательные фильтры `adults` (целое число от 1), `children` (целое число от
0) и повторяемый `amenity` (slug). Все переданные `amenity` должны быть у категории:

```text
GET /api/v1/room-types/?adults=2&children=1&amenity=wifi&amenity=breakfast
```

`GET /api/v1/room-types/{slug}/` возвращает одну категорию. Каталог доступен только для чтения:
создание и изменение выполняются менеджером в Django admin. Контент-редактор может менять
маркетинговые поля категории, удобства и галерею, но не видит и не изменяет цену, лимиты вместимости
или режим подтверждения; физические комнаты ему недоступны.

## Расчёт доступности и цены

`POST /api/v1/quotes/` рассчитывает доступность категории и актуальную цену без создания брони или удержания. Запрос принимает `check_in`, `check_out`, `room_type` (slug), `adults` и `children`:

```json
{
  "check_in": "2026-09-10",
  "check_out": "2026-09-13",
  "room_type": "deluxe",
  "adults": 2,
  "children": 1
}
```

Ответ содержит `available`, количество `nights`, `price_per_night` и `total`; цены всегда сериализуются строками Decimal. `total` — авторитетное значение, которое клиент передаст как `quoted_total` при последующем создании брони.

## Конфигурация

Все настройки читаются из окружения; `.env.example` описывает каждую переменную с безопасной локальной заглушкой. Реальный `.env`, данные PostgreSQL, media и `node_modules` не попадают в Git: `.env` игнорируется, а данные лежат в именованных Docker volume вне репозитория.

Бизнес-часовой пояс — `Asia/Bishkek`, язык интерфейса — русский, валюта — USD.

## Статус

Реализованы локальное окружение Docker Compose, Django/DRF и React каркасы, единый API-контракт, OpenAPI/Swagger, фиксированный CMS гостиницы, публичный каталог категорий, Booking foundation, stay policy и PostgreSQL occupancy ledger без публичных booking-endpoint’ов.

Ещё не реализовано и появится в следующих задачах:

- команда `seed_demo` и демо-аккаунты из `.env`;
- booking API, lifecycle, котировки, idempotency и demo-оплата;
- SPA: каталог, бронирование, оплата и остальные публичные страницы;
- E2E-сценарии.

Этот README описывает только те команды, которые действительно работают сегодня. Планируемые команды добавляются сюда вместе с их реализацией.
