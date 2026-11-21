# STM Contrib Server

Community-driven bus line and product code contribution server for LecteurOPUS.

## Quick Start

```bash
# Clone
git clone https://github.com/jerji/stm-contrib-server.git
cd stm-contrib-server

# Create data directory
mkdir -p data

# Start
docker compose up -d

# Find the admin API key in the logs:
docker compose logs stm-contrib-api | grep "ADMIN API KEY"
```

## API Endpoints

### Bus Line Votes
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/bus/vote` | API key | Vote to confirm/reject a bus ID mapping |
| POST | `/api/v1/bus/submit` | API key | Submit an unknown bus/operator pair |
| GET | `/api/v1/bus/votes?bus_name=X` | None | Get vote tallies for a bus |

### Product Codes
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/products/submit` | API key | Submit or upvote a product code name |
| POST | `/api/v1/products/vote` | API key | Vote on a product name submission |
| GET | `/api/v1/products/` | None | List all confirmed + top-voted codes |
| GET | `/api/v1/products/search?q=X` | None | Search product codes by name |

### Admin
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/keys/generate?label=X&admin=false` | None | Generate a new API key |

## Security

- **HTTPS only** — Caddy auto-provisions Let's Encrypt certificates
- **Rate limited** — 10 requests/min per IP on submission endpoints
- **API keys** — Required for all write operations
- **Input validation** — All inputs sanitized and length-limited
- **SQL injection** — SQLAlchemy ORM prevents injection
- **No secrets in code** — Admin key generated on first run, printed to logs
- **Docker isolation** — API runs as non-root in container

## pfSense Port Forwarding

Forward ports 80 and 443 to the host running Docker:

```
WAN → 192.168.1.67:80  (HTTP, for Let's Encrypt validation)
WAN → 192.168.1.67:443 (HTTPS)
```

## DNS

Create an A record for `stmcontrib.jouellet.net` pointing to your public IP.