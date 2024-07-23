# GPTScrape
GPTScrape is a tool for scraping web content and converting it into structured JSON using NLP and LLM models. It uses spaCy for natural language processing and GPT4All for text-to-JSON conversion.

## Setup

### 1. Install Required Packages
First, ensure you have the necessary Python packages installed. Use the `requirements.txt` file provided in the repository.
```bash
pip install -r requirements.txt
```

### 2. Download spaCy Model
The application uses the nb_core_news_lg (Norwegian Bokmål) spaCy model by default. Download it with the following command:
```bash
python -m spacy download nb_core_news_lg
```

### 3. Configuration
You might want to adjust settings in the config.ini file.

## Usage

### 1. Start the Application
Run the main script to start the GPTScrape application:
```bash
python main.py
```

### 2. Application Interface
- **URL**: Enter the URL of the web page you want to scrape.
- **Input**: Provide the text input or description that you want to use for scraping.
- **Scrape Button**: Click this button to start the scraping process.

### 3. Application Behavior
For now the application will navigate to the provided URL, locate the body of the page, and use the text input to find the best matching element, then create a query selector based on it to match other elements of the same structure. It will then process these elements' text using GPT4All and prompt it to get a structured JSON output.

## Troubleshooting
- **Dependencies**: Make sure all dependencies in requirements.txt are installed. If you encounter issues, consider creating a virtual environment.
- **Model Download**: Ensure that the spaCy model download completes successfully. GPT4All model should get downloaded automatically.

## Contributing
If you want to contribute to the project, please fork the repository and create a pull request with your changes.

## License
This project is licensed under the MIT License. See the LICENSE file for details.