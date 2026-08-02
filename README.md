# HotelApp

Учебное веб-приложение для управления одной гостиницей: каталог номеров, бронирование, личный кабинет клиента и административная панель.

## Стек

- Backend: Python 3.13, Django 5.2 LTS, PostgreSQL 17.
- Frontend: React 19.2, TypeScript, Vite.
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
- Django admin — http://localhost:8000/admin/

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
docker compose exec frontend npm run typecheck
```

## Конфигурация

Все настройки читаются из окружения; `.env.example` описывает каждую переменную с безопасной локальной заглушкой. Реальный `.env`, данные PostgreSQL, media и `node_modules` не попадают в Git: `.env` игнорируется, а данные лежат в именованных Docker volume вне репозитория.

Бизнес-часовой пояс — `Asia/Bishkek`, язык интерфейса — русский, валюта — USD.

## Статус

Реализовано локальное окружение Docker Compose и минимальный исполняемый каркас, которого достаточно для запуска трёх контейнеров.

Ещё не реализовано и появится в следующих задачах:

- доменные приложения `accounts`, `content`, `inventory`, `bookings`, `inquiries`;
- `/api/v1/`, OpenAPI schema и Swagger UI;
- команда `seed_demo` и демо-аккаунты из `.env`;
- SPA: router, дизайн-система, страницы и сетевой слой;
- тесты, линтеры и E2E-сценарии.

Этот README описывает только те команды, которые действительно работают сегодня. Планируемые команды добавляются сюда вместе с их реализацией.
