#!/bin/bash

# Generate nginx configuration for Heroku with dynamic port
PORT=${PORT:-8000}

cat > /opt/app/conf/nginx-heroku.conf << EOF
daemon              off;
worker_processes    1;
events {
  worker_connections 1024;
}
http {
  include       /etc/nginx/mime.types;
  default_type  application/octet-stream;

  keepalive_timeout  15;
  autoindex          off;
  server_tokens      off;
  port_in_redirect   off;
  absolute_redirect  off;
  sendfile           off;
  tcp_nopush         on;
  tcp_nodelay        on;

  client_max_body_size 64k;
  client_header_buffer_size 16k;
  large_client_header_buffers 4 16k;

  ## Cache open FD
  open_file_cache max=10000 inactive=3600s;
  open_file_cache_valid 7200s;
  open_file_cache_min_uses 2;

  ## Gzipping is an easy way to reduce page weight
  gzip                on;
  gzip_vary           on;
  gzip_proxied        any;
  gzip_types          application/javascript application/x-javascript application/rss+xml text/javascript text/css image/svg+xml;
  gzip_buffers        16 8k;
  gzip_comp_level     6;

  access_log         /dev/stdout;
  error_log          /dev/stderr error;

  server {
    listen $PORT;
    
    # API proxy
    location /v1/ {
      proxy_pass http://127.0.0.1:5000;
      proxy_set_header Host \$host;
      proxy_set_header X-Real-IP \$remote_addr;
      proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
      proxy_set_header X-Forwarded-Proto \$scheme;
      proxy_read_timeout 90;
      proxy_connect_timeout 90;
      proxy_redirect off;
    }

    # Static web files
    location / {
      root /opt/app/public;
      index index.html;
      try_files \$uri \$uri/ \$uri/index.html =404;
      
      # Cache control for different file types
      location ~* \.(html)$ {
        add_header Cache-Control "public, max-age=0, must-revalidate";
        expires    off;
      }
      location ~* \.(ico|jpg|jpeg|png|gif|svg|js|jsx|css|less|swf|eot|ttf|otf|woff|woff2)$ {
        add_header Cache-Control "public";
        expires +1y;
      }
      location ~* ^.*/(page-data/.*|app-data.json|sw.js)$ {
        add_header Cache-Control "public, max-age=0, must-revalidate";
        expires    off;
      }
      location = /leek-config.js {
        expires -1;
        add_header Cache-Control "no-cache, must-revalidate, proxy-revalidate, max-age=0";
      }
    }
  }
}
EOF

# Create leek-config.js with environment variables
cat > /opt/app/public/leek-config.js << EOF
window["leek_config"] = {
  LEEK_API_URL: window.location.origin,
  LEEK_API_ENABLE_AUTH: "${LEEK_API_ENABLE_AUTH:-true}",
  LEEK_FIREBASE_API_KEY: "${LEEK_FIREBASE_API_KEY}",
  LEEK_FIREBASE_AUTH_DOMAIN: "${LEEK_FIREBASE_AUTH_DOMAIN}",
  LEEK_FIREBASE_PROJECT_ID: "${LEEK_FIREBASE_PROJECT_ID}",
  LEEK_FIREBASE_APP_ID: "${LEEK_FIREBASE_APP_ID}",
  LEEK_VERSION: "${LEEK_VERSION:-'-.-.-'}"
};
EOF

# Start nginx
exec nginx -c /opt/app/conf/nginx-heroku.conf 