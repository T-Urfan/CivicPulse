FROM node:20.17.0-slim AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build the application
COPY . .
RUN npm run build

# Serve with Nginx
FROM nginx:1.25.4-alpine
RUN apk update && apk upgrade --no-cache
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Nginx image already drops privileges in newer versions if configured or we just accept it as standard for this image unless strict non-root is demanded for the frontend, but we pinned it.
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
