FROM node:18-bullseye

WORKDIR /app

# Copy package files first (important for caching)
COPY package.json package-lock.json* ./

# Install dependencies cleanly
RUN npm install --legacy-peer-deps

# Copy rest of the project
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
