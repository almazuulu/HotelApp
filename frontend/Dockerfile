# syntax=docker/dockerfile:1
#
# Local development image for the Vite dev server. The MVP has no production
# build stage and no static web server in front of the SPA.
FROM node:22-slim

ENV NODE_ENV=development \
    npm_config_update_notifier=false

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . /app

EXPOSE 5173

CMD ["npm", "run", "dev"]
