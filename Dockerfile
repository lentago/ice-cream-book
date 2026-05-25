# Dockerfile for the cookbook site
#
# This is a SIMPLE Dockerfile — no multi-stage build needed because
# CI/CD builds the Astro site before Docker runs. We just copy the
# pre-built static files into nginx.
#
# The Astro build happens in the GitHub Action (Node environment).
# Docker's only job: package the output into a serving container.

FROM nginx:latest

# Copy the nginx config (port 8080, /health endpoint, clean URLs)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy pre-built static site from Astro
COPY ice_cream_site/dist/ /usr/share/nginx/html/

EXPOSE 8080
