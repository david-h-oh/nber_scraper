# NBER Working Paper Scraper and AI Mentions

This project collects metadata and abstracts for NBER working papers and explores how often the abstracts mention artificial intelligence (AI), including AI in connection with tasks.

## Project structure

- [`scripts/nber_scrape.py`](./scripts/nber_scrape.py) — scrapes NBER working-paper pages and saves records to Parquet.
- [`notebooks/nber_scrape.ipynb`](./notebooks/nber_scrape.ipynb) — analyzes abstracts by quarter and plots AI-mention trends.
- [`data/nber_papers.parquet`](./data/nber_papers.parquet) — the existing dataset used by the notebook and scraper; new records are saved here by default.
- [`reports/Pct_nber_wpaper_mentioning_ai.png`](./reports/Pct_nber_wpaper_mentioning_ai.png) — a saved visualization of AI mentions.
- `pyproject.toml` and `uv.lock` — project dependencies and their locked versions.

## Setup with uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it is not already available, then sync the project dependencies:

```bash
uv sync
```

This creates a project-local `.venv` and installs the scraper and notebook dependencies. The committed `uv.lock` keeps dependency versions reproducible.

## Scrape papers

From the repository root, run the scraper in the managed environment:

```bash
uv run scripts/nber_scrape.py
```

By default, it requests papers from `w26694` through `w35018` and writes the results to `data/nber_papers.parquet`. It saves batches of 10 records and waits a random 10–30 seconds between successful page requests.

The scraper accepts optional arguments when called from Python:

```python
from scripts.nber_scrape import scrape_nber_working_papers

scrape_nber_working_papers(
    start_paper=26694,
    end_paper=26700,
    batch_size=10,
    output_file="data/nber_papers.parquet",
)
```

If the output file already contains records, the scraper starts at one more than its largest `Working Paper Number`, overriding `start_paper`. Choose a different `output_file` to start a separate collection. Pages that do not return HTTP 200 are skipped.

Each saved record has these columns:

| Column | Description |
| --- | --- |
| `Working Paper Number` | NBER working-paper number |
| `Title` | Paper title |
| `Authors` | Author names |
| `Date` | Issue date shown on the NBER page |
| `Abstract` | Paper abstract |

## Explore the data

From the repository root, start Jupyter with the analysis notebook:

```bash
uv run jupyter notebook notebooks/nber_scrape.ipynb
```

Select the project's `.venv` kernel if prompted. The notebook reads `data/nber_papers.parquet`, groups papers by quarter, and calculates the share of abstracts mentioning “artificial intelligence” or “AI”. It also calculates the share mentioning both an AI term and “task”, and plots quarterly and cumulative percentages.

## Data source

Paper pages are fetched from the [NBER Working Papers](https://www.nber.org/papers/) website. The scraper relies on the page's current HTML structure; changes to that structure may affect extraction. Requests are made sequentially with a randomized pause to reduce request frequency.