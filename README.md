# VibeScrapper

A simple web scraper to extract HTML content from divs with the attribute `data-lyrics-container="true"`.

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper with a URL:

```bash
python scraper.py https://example.com/page-with-lyrics
```

### Options

- `--output` or `-o`: Save the results to a JSON file
  ```bash
  python scraper.py https://example.com/page-with-lyrics --output results.json
  ```

## Output Format

The scraper outputs:
- HTML content of each matching div
- Text content of each matching div

## Example

```bash
python scraper.py https://example.com/page-with-lyrics
```

This will print the HTML and text content of all divs with `data-lyrics-container="true"` found on the page.
