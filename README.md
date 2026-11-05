# NBER Working Paper Scraper and AI Mentions

This project collects metadata and abstracts for NBER working papers and explores how often the abstracts mention artificial intelligence (AI), including AI in connection with tasks.

> **AI assistance disclaimer:** This project was developed with help from an AI coding assistant.

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

By default, it requests papers starting at `w0001` and continues until the first response that is not HTTP 200. Paper numbers below 10000 are zero-padded to four digits in the URL (for example, `w0001`); numbers from 10000 onward are unpadded. To stop at a specific paper number instead, pass `end_paper`; that number is included. The scraper writes to `data/nber_papers.parquet`, saves batches of 10 records, and waits a random 10–30 seconds between successful page requests.

The scraper accepts optional arguments when called from Python:

```python
from scripts.nber_scrape import scrape_nber_working_papers

scrape_nber_working_papers(
    start_paper=1,
    end_paper=5,
    batch_size=10,
    output_file="data/nber_sample.parquet",
)
```

By default, if the output file already contains records, the scraper resumes at one more than its largest `Working Paper Number`; with no existing records, it starts at paper 1. Passing `start_paper` explicitly starts at that number instead, and can append duplicate rows if those papers are already in the output. `Working Paper Number` is stored as a number, without leading zeroes. Choose a different `output_file` to start a separate collection. The first non-200 response ends the scrape.

Each saved record has these columns:

| Column | Description |
| --- | --- |
| `Working Paper Number` | NBER working-paper number |
| `Title` | Paper title |
| `Authors` | Author names |
| `Date` | Issue date shown on the NBER page |
| `Abstract` | Paper abstract |
| `Citation` | NBER-formatted citation |
| `Published` | Whether the page lists a published version |
| `Published Version` | Published-version citation, when listed |
| `Topics` | Topic names listed for the paper, separated by semicolons |
| `Programs` | Program names listed for the paper, separated by semicolons |

## Explore the data

From the repository root, start Jupyter with the analysis notebook:

```bash
uv run jupyter notebook notebooks/nber_scrape.ipynb
```

Select the project's `.venv` kernel if prompted. The notebook reads `data/nber_papers.parquet`, groups papers by quarter, and calculates the share of abstracts mentioning “artificial intelligence” or “AI”. It also calculates the share mentioning both an AI term and “task”, and plots quarterly and cumulative percentages.

## Data source

Paper pages are fetched from the [NBER Working Papers](https://www.nber.org/papers/) website. The scraper relies on the page's current HTML structure; changes to that structure may affect extraction. Requests are made sequentially with a randomized pause to reduce request frequency.