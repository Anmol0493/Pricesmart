# PriceMart Product Scraper

This Python script is designed to scrape product information from the PriceMart website. It utilizes BeautifulSoup for web scraping, multithreading for concurrent data extraction, and requests for HTTP communication.

## Prerequisites

Before using this script, ensure that you have the following prerequisites in place:

- **Python**: Make sure you have Python installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

- **Required Libraries**: Install the necessary Python libraries by running the following command:

    ```bash
    pip install requests beautifulsoup4 pandas
    ```

## How to Use

1. Clone or download this repository to your local machine.

2. Open a terminal or command prompt and navigate to the directory containing the script files.

3. Ensure you have the necessary configuration files (`config.json` and `product_info.json`) in the same directory as the script.

4. Run the script by executing the following command:

    ```bash
    python main.py
    ```

5. The script will scrape product information from the PriceMart website and save the data in a CSV file (`<config_filename>.csv`) in the same directory.

## Customization

- **Configuration**: Modify the `config.json` file to adjust script parameters such as maximum workers, location, and file names.

- **Product Information**: Update the `product_info.json` file with the required product information fields.

- **Error Handling**: Implement error handling mechanisms as needed to handle cases such as failed HTTP requests or unexpected page structures.

## Data Output

- **CSV File**: Contains the scraped product information in CSV format, including details such as SKU, name, price, description, and image URLs.

## Notes

- Ensure compliance with the PriceMart website's terms of service and robots.txt file when scraping data.

- Consider incorporating proxy rotation or IP rotation mechanisms to avoid IP bans or rate limiting from the website server.

- Regularly check and update the scraping logic to adapt to any changes in the website's HTML structure or content presentation.
