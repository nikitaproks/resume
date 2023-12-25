# Use a Node.js image to build the SvelteKit app
FROM node:latest as build-stage

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the app
RUN npm run build

# Production stage: Use Nginx to serve the static files
FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install
# Copy built static files from the build stage
COPY --from=build-stage /app/build /app/build/