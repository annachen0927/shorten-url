<<<<<<< HEAD
# shorten-url
=======
---
title: Short URL Service API Documentation

---

# Short URL Service API Documentation

## API Endpoints

### 1. Create Short URL
**Endpoint:** `POST /shorten`

**Description:**
Creates a shortened URL for the given original URL. The request is rate-limited using Redis to prevent abuse.

**Request:**
```json
{
  "original_url": "https://example.com/some-long-url"
}
```

**Response Example (Success):**
If the URL was successfully shortened, the response will be:
```json
{
  "short_url": "http://localhost:8000/abcd12",
  "expiration_date": "2025-04-23T12:00:00Z",
  "success": true
}
```
- `short_url`: The shortened URL that can be used to access the original URL.

- `expiration_date`: The expiration date of the shortened URL.

- `success`: A boolean flag indicating that the operation was successful.

**Response Example (Error):**
If there was an error with the provided URL, the response will indicate the error reason.
Possible Error Reasons:
1. URL too long
 - `Code`: 400
  - `Description`: The original URL exceeds the allowed length limit.
  - `Response`:
```json
{
  "success": false,
  "reason": "URL too long"
}
```
2. Invalid URL format
- `Code`: 400
- `Description`: The provided URL is not a valid URL format.
- `Response`:
```json
{
  "success": false,
  "reason": "Invalid URL"
}
```

**Status Codes:**
- `201 Created` – Successfully created short URL.
- `400 Bad Request` – Invalid URL format or too long.
- `429 Too Many Requests` – Rate limit exceeded.

---

### 2. Redirect Short URL
**Endpoint:** `GET /<short_code>`

**Description:**
Redirects to the original URL associated with the short code. If the short code is found in the Redis cache, it will redirect immediately; otherwise, it will query the database and update the cache.

**Response:**
- `302 Found` – Redirects to the original URL.
- `410 Gone` – Short URL has expired.
- `404 Not Found` – Short URL does not exist.

---

## Deployment Instructions

### Option 1: Run from Docker Hub
1. Clone the repository (to get the docker-compose.prod.yml file):
   ```sh
   git clone https://github.com/annachen0927/shorten-url.git
   cd shorten-url
   ```
2. Copy the .env.example to .env
3. Open the .env file and provide the required values.
   
4. Pull the image from Docker Hub:
   ```sh
   docker pull himachen/short-url-system:latest 
   ```
5. Run the container with Docker Compose:
   ```sh
   docker-compose -f docker-compose.prod.yml up -d
   ```
6. Create the database::
   ```sh
   docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
   ```

### Option 2: Build and Run Locally
1. Clone the repository:
   ```sh
   git clone https://github.com/annachen0927/shorten-url.git
   cd shorten-url
   ```
2. Build the Docker image:
   ```sh
   docker build -t short-url .
   ```
2. Copy the .env.example to .env
3. Open the .env file and provide the required values.
5. Run the container with Docker Compose:
   ```sh
   docker-compose -f docker-compose.dev.yml up -d
   ```
4. Create the database:
   ```sh
   docker-compose -f docker-compose.dev.yml exec web python manage.py migrate
   ```

Now the service is running at `http://localhost:8000/`.

---

## Environment Variables

Ensure the following environment variables are configured properly in your `.env` file:
```ini
REDIS_HOST=redis
REDIS_PORT=6379

POSTGRES_DB=shorturl_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

DAY=30
RATE_LIMIT=10
WINDOW_SIZE=60

SECRET_KEY=django-insecure-2#&p3r75wa$9^j4*#jz27*
```

---

## Additional Notes
- The service uses PostgreSQL as the database and Redis for caching and rate limiting.
- Ensure the database and Redis instances are running before starting the service.

---


>>>>>>> c3ea758 (Add Create Short URL API and Resolve Short URL API to redirect to original URL)
