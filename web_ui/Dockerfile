FROM node:20-alpine as build

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the code
COPY . .

# Create a production build
RUN npm run build

# Production environment
FROM nginx:alpine

# Copy build files from build stage
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy env script
COPY env.sh /usr/share/nginx/html/env.sh
RUN chmod +x /usr/share/nginx/html/env.sh

# Add env-config.js placeholder
RUN touch /usr/share/nginx/html/env-config.js

# Add script to index.html that loads env-config.js
RUN sed -i '/<head>/a \
    <script src="/env-config.js"></script>' /usr/share/nginx/html/index.html

EXPOSE 80

# Start Nginx server after setting environment variables
CMD ["/bin/sh", "-c", "/usr/share/nginx/html/env.sh && nginx -g 'daemon off;'"]
