# Pull Docker Hub base image
FROM node:16-alpine
# Variables
ENV PORT=3000
# Set working directory
WORKDIR /usr/app
# Install app dependencies
COPY package*.json ./
RUN npm install -qy
# Copy app to container
COPY . .
# Run the "dev" script in package.json
CMD npm run dev -- --host 0.0.0.0 --port $PORT