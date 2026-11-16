# Slika frontenda u dvije faze (docker-compose.prod.yml).

# Prva faza gradi aplikaciju. Node je potreban samo za izgradnju, pa ne ulazi u konačnu sliku.
FROM node:24-alpine AS build
WORKDIR /app
# Paketi prije koda, da se sloj s paketima ponovno koristi dok se popis ne promijeni
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
# Provjera tipova i izgradnja u dist/; pogreška u tipovima prekida izgradnju slike
RUN npm run build

# Druga faza: nginx poslužuje izgrađene datoteke i prosljeđuje /api backendu
FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
