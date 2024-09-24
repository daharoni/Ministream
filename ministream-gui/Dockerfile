# Stage 1: Build the React application
FROM node:14 as build

# Set working directory
WORKDIR /app

# Copy only package.json and package-lock.json
COPY ministream-gui/package.json ministream-gui/package-lock.json ./

# Install dependencies
# TODO: Fix this. It should ideally be RUN npm ci but that currently throws an error
RUN npm install 

# Copy the rest of the application code
COPY ministream-gui/ ./

# Build the app
# TODO: Fix this. It should ideally be RUN npm ci but that currently throws an error
RUN npm install && npm run build

# Stage 2: Serve the app using Nginx
FROM nginx:alpine

# Remove default Nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy the build output to Nginx static assets directory
COPY --from=build /app/build /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Start Nginx server
CMD ["nginx", "-g", "daemon off;"]
