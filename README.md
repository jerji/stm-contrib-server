# STM Contrib Server

Community-driven bus line and product code contribution server for LecteurOPUS.
Users submit data via the app; you review submissions and add confirmed entries to the next app release.

## Quick Start

```bash
git clone https://github.com/jerji/stm-contrib-server.git
cd stm-contrib-server
mkdir -p data
docker compose up -d
```

Set your API key via env var (override the default):
```bash
STM_CONTRIB_API_KEY="your-secret-key" docker compose up -d
```

## API Endpoints

All write endpoints require `X-API-Key` header with the shared app key.
All read endpoints are public (no key needed).

### Bus Line Votes
Users can submit unknown bus routes and vote on auto-detected bus → operator mappings.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/bus/vote` | API key | Vote confirm(+1)/reject(-1) a bus ID mapping |
| POST | `/api/v1/bus/submit` | API key | Submit unknown bus/operator name + raw card data |
| GET | `/api/v1/bus/votes?bus_name=X` | None | View vote tallies for a bus name |

### Product Codes
Users can submit product code → name mappings as they discover them.
Names with score ≥ 3 appear in the public listing for your review.

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/products/submit` | API key | Submit a new product code name (or upvote existing) |
| POST | `/api/v1/products/vote` | API key | Upvote/downvote an existing submission |
| GET | `/api/v1/products/` | None | List confirmed + top-voted (score ≥ 3) codes |
| GET | `/api/v1/products/search?q=X` | None | Search by name fragment |

### General
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | None | Service info |
| GET | `/health` | None | Health check |

## Admin Tasks

No admin API routes. SSH into the host and use the container directly:

```bash
# View all product submissions
docker compose exec stm-contrib-api sqlite3 /app/data/stmcontrib.db \
  "SELECT * FROM product_submissions ORDER BY vote_score DESC;"

# Confirm a submission (mark for inclusion in next app release)
docker compose exec stm-contrib-api sqlite3 /app/data/stmcontrib.db \
  "UPDATE product_submissions SET confirmed=1 WHERE id=5;"

# View recent bus votes
docker compose exec stm-contrib-api sqlite3 /app/data/stmcontrib.db \
  "SELECT * FROM bus_votes ORDER BY id DESC LIMIT 20;"

# View recent bus submissions
docker compose exec stm-contrib-api sqlite3 /app/data/stmcontrib.db \
  "SELECT * FROM bus_submissions ORDER BY id DESC LIMIT 20;"
```

## Workflow

1. User discovers an unknown product code on their OPUS card
2. App submits `code=0x0A4B&name=10 trips, All modes A` to the server
3. Other users can upvote if they confirm the name
4. You review submissions weekly via `docker exec` SQLite queries
5. Add confirmed codes to `res/xml/product_codes.xml` in the LecteurOPUS fork
6. Ship next APK

## Security

| Layer | What | Why |
|-------|------|-----|
| HTTPS | Caddy + Let's Encrypt | All traffic encrypted |
| Rate limit | 10 req/min per IP | Prevents spam on write endpoints |
| API key | Single shared key, set via env var | Simple abuse prevention |
| Input validation | Pydantic length/type limits | No injection via text fields |
| ORM | SQLAlchemy parameterized queries | No SQL injection |
| Docker | Non-root user inside container | Container escape ≠ host compromise |

## pfSense Port Forwarding

Forward ports 80 and 443 to the host running Docker:

```
WAN → 192.168.1.67:80  (HTTP, for Let's Encrypt validation)
WAN → 192.168.1.67:443 (HTTPS)
```

## DNS

Create an A record for `stmcontrib.jouellet.net` pointing to your public IP.