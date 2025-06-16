## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/s1hetu/b2b_marketplace_scraping.git
   ```
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Installation of requirements: <br>
   ```bash
   pip install -r requirements.txt
   ```
<br>

## Run the apps
```
python -m apps.<app_name>.main
```

### Deldure Scraper
```bash
   python -m apps.deldure_scraper.main
```

### IndiaMart Scraper
```bash
   python -m apps.indiamart_scraper.main
```

### JustDial Scraper
```bash
  python -m apps.justdial_scraper.main
```

### GST Data Fetcher
```bash
  python -m apps.gst_data_fetcher.main
```

### Google Business Data Fetcher
```bash
  python -m apps.google_business_data_fetcher.main
```

<br>
<br>

## Run helpers

### Insert scraped data to DB
```bash
  python -m libs.utils.database_operations.insertion.scraped_data_insertion
```

### Insert GST data to DB
```bash
  python -m libs.utils.database_operations.insertion.gst_data_insertion
```

### Insert Google Business Data data to DB
```bash
  python -m libs.utils.database_operations.insertion.gbd_data_insertion
```

### Insert Matched Google Business Data data to DB
```bash
  python -m libs.utils.database_operations.insertion.matched_gbd_data_insertion
```

### Perform static field ranking on scraped data
```bash
  python -m libs.utils.database_operations.ranking.scraped_data_static_ranking
```

### Perform static gst ranking
```bash
  python -m libs.utils.database_operations.ranking.gst_data_static_ranking
```

### Perform gst & scraped data comparison ranking
```bash
  python -m libs.utils.database_operations.ranking.gst_data_comparison_with_scraped_data_ranking
```

### Perform static google business data ranking
```bash
  python -m libs.utils.database_operations.ranking.gbd_data_static_ranking
```

### Perform google business data & scraped data comparison ranking
```bash
  python -m libs.utils.database_operations.ranking.gbd_data_comparison_with_scraped_data_ranking
```