FROM node:20-slim

WORKDIR /app

COPY server/package*.json ./
RUN npm ci --omit=dev

COPY dist/client ./dist/client
COPY dist/server ./dist/server
COPY server/index.js ./index.js

EXPOSE 3000

ENV NODE_ENV=production
ENV API_URL=http://backend:8000

CMD ["node", "index.js"]
