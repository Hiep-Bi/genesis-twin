FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy application code
COPY . .

# Build production assets
RUN npm run build

# Install lightweight static server
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Start production server
CMD ["serve", "-s", "build", "-l", "3000"]

