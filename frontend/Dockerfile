FROM node:24-bookworm-slim AS development
WORKDIR /app
COPY package*.json ./
RUN npm ci --no-audit --no-fund
COPY . .
EXPOSE 5173
CMD ["sh", "-c", "npm ci --no-audit --no-fund && npm run dev -- --host 0.0.0.0"]

FROM development AS build
RUN npm run build

FROM nginx:stable-alpine AS production
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
RUN touch /var/run/nginx.pid && chown -R nginx:nginx /var/run/nginx.pid /var/cache/nginx /etc/nginx/conf.d
USER nginx
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]

FROM development AS default
