# Scrapy Book Scraper

> Built as a learning project while studying web scraping with Scrapy.
> Covers core concepts including middleware architecture, proxy rotation,
> data pipelines, and spider deployment — then refactored to production standards.

A hands-on educational project for learning web scraping with Scrapy that extracts book data from [books.toscrape.com](https://books.toscrape.com). Built while following a structured web scraping course, then extended with professional architecture, environment-based configuration, and deployment tooling.

## Features

- Scrapes all 1000+ books across 50 pages
- Cleans and normalizes data via item pipelines
- Rotating fake browser headers (ScrapeOps)
- Proxy rotation via ScrapeOps Proxy Aggregator or Oxylabs Web Unblocker
- MySQL database storage pipeline
- CSV / JSON / JSONL feed export
- Deployed via Scrapyd with ScrapydWeb dashboard
- Monitored via ScrapeOps dashboard
- Environment-based configuration

## What I Learned

- How Scrapy's request/response cycle works
- Building and chaining item pipelines for data cleaning
- Writing custom downloader middlewares for proxy and header injection
- The difference between rotating proxies and proxy APIs
- Deploying spiders with Scrapyd and managing them via ScrapydWeb
- Monitoring spider health and stats with ScrapeOps
- Professional project structure: `.env`, `.gitignore`, modular code

## Tech Stack

| Tool          | Purpose                                      |
| ------------- | -------------------------------------------- |
| Scrapy        | Core scraping framework                      |
| Scrapyd       | Spider deployment & scheduling               |
| ScrapydWeb    | Visual management dashboard                  |
| ScrapeOps     | Monitoring + proxy aggregator + fake headers |
| Oxylabs       | Web Unblocker proxy                          |
| MySQL         | Persistent data storage                      |
| python-dotenv | Environment variable management              |

## Project Structure

```
scrapy-book-scraper/
├── bookscraper/
│   ├── spiders/
│   │   └── bookspider.py      # Main spider — crawls all pages
│   ├── items.py               # Data models (BookItem)
│   ├── middlewares.py         # Proxy + header rotation middlewares
│   ├── pipelines.py           # Data cleaning + MySQL storage
│   └── settings.py            # Project configuration + feature flags
├── .env.example               # Environment variable template
├── .gitignore
├── requirements.txt
├── scrapy.cfg
└── README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/dxwood01/scrapy-book-scraper.git
cd scrapy-book-scraper
```

### 2. Create virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Fill in your credentials in `.env`:

```env
SCRAPEOPS_API_KEY=your_key_here
PROXY_USER=your_proxy_username
PROXY_PASSWORD=your_proxy_password
PROXY_ENDPOINT=unblock.oxylabs.io
PROXY_PORT=7000
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=books
```

> Free API keys available at [scrapeops.io](https://scrapeops.io) and [oxylabs.io](https://oxylabs.io)

## Running the Spider

### Direct run

```bash
scrapy crawl bookspider
```

### Via Scrapyd

```bash
# Terminal 1 — start Scrapyd server
scrapyd

# Terminal 2 — deploy project to Scrapyd
scrapyd-deploy default

# Schedule a run (PowerShell)
Invoke-WebRequest http://localhost:6800/schedule.json -Method Post -Body @{project="bookscraper"; spider="bookspider"}
```

### Via ScrapydWeb dashboard

```bash
scrapydweb
```

Then open: `http://localhost:5000`

## Middleware Configuration

All middlewares are implemented and available. Switch between strategies in `settings.py` by commenting/uncommenting:

```python
DOWNLOADER_MIDDLEWARES = {
    # --- Header Rotation (choose one) ---
    'bookscraper.middlewares.ScrapeOpsFakeBrowserHeaderAgentMiddleware': 300,
    # 'bookscraper.middlewares.ScrapeOpsFakeUserAgentMiddleware': 300,

    # --- Proxy (choose one) ---
    'bookscraper.middlewares.ScrapeOpsProxyMiddleware': 725,
    # 'bookscraper.middlewares.MyProxyMiddleware': 350,
}
```

| Middleware                                  | What It Does                                                                  |
| ------------------------------------------- | ----------------------------------------------------------------------------- |
| `ScrapeOpsFakeBrowserHeaderAgentMiddleware` | Rotates full browser header sets — makes requests look like real browsers     |
| `ScrapeOpsFakeUserAgentMiddleware`          | Rotates User-Agent strings only                                               |
| `ScrapeOpsProxyMiddleware`                  | ScrapeOps Proxy Aggregator — handles rotation, headers, retries automatically |
| `MyProxyMiddleware`                         | Oxylabs Web Unblocker — IP rotation via proxy URL                             |

### Anti-Detection Strategy

```
Level 1 — Fake headers/UA only      → simple sites
Level 2 — Fake headers + proxy      → medium difficulty sites
Level 3 — Proxy API (ScrapeOps)     → heavily protected sites (replaces levels 1+2)
```

## Data Output

| Format | How to enable                                    |
| ------ | ------------------------------------------------ |
| CSV    | Set in `FEEDS` in `settings.py` (default)        |
| JSONL  | Change format to `jsonlines` in `FEEDS`          |
| MySQL  | Enable `SaveToMySQLPipeline` in `ITEM_PIPELINES` |

### Scraped Fields

| Field            | Type   | Description         |
| ---------------- | ------ | ------------------- |
| `url`            | string | Book page URL       |
| `name`           | string | Book title          |
| `price`          | float  | Price in GBP        |
| `rating`         | int    | Star rating (0–5)   |
| `category`       | string | Book category       |
| `description`    | string | Book description    |
| `product_type`   | string | Product type        |
| `price_excl_tax` | float  | Price excluding tax |
| `price_incl_tax` | float  | Price including tax |
| `tax`            | float  | Tax amount          |
| `availability`   | int    | Number in stock     |
| `num_reviews`    | int    | Review count        |

## Monitoring

Spider runs are monitored via [ScrapeOps](https://scrapeops.io/app/overview). Enable in `settings.py`:

```python
SCRAPEOPS_MONITOR_ACTIVATED = True
```

View live stats, errors, item counts, and request logs from the ScrapeOps dashboard.

## License

[MIT License](LICENSE) — feel free to use, adapt and build on this project.

## Acknowledgements

- [books.toscrape.com](https://books.toscrape.com) — sandbox site built for scraping practice
- [ScrapeOps](https://scrapeops.io) — monitoring, fake headers, and proxy aggregator
- [Oxylabs](https://oxylabs.io) — Web Unblocker proxy service
- [The Python Scrapy Playbook](https://thepythonscrapyplaybook.com/freecodecamp-beginner-course/) — course material this project is based on
- [YouTube Tutorial by freeCodeCamp](https://youtu.be/mBoX_JCKZTE?si=nTmBJdzlPZEfizks) — video walkthrough followed during development
