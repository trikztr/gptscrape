import logging
import asyncio
import tkinter as tk
from tkinter import Text, ttk
from configparser import ConfigParser
from scraper import GPTScraper
import sys

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


class App(tk.Tk):
    def __init__(self, loop: asyncio.AbstractEventLoop, interval: float = 1 / 120):
        super().__init__()
        self.loop = loop
        self.config = self._load_config()
        self.scraper: GPTScraper = None

        # Setup GUI
        self._setup_gui()

        # Setup application behavior
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.tasks = [loop.create_task(self._updater(interval))]

    def _load_config(self) -> ConfigParser:
        """
        Load and initialize configuration from config.ini file.
        """
        config = ConfigParser()
        config.read("config.ini")

        if not config.sections():
            config.add_section("nlp")
            config.set("nlp", "model_name", "nb_core_news_lg")
            config.add_section("llm")
            config.set("llm", "model_name", "Meta-Llama-3-8B-Instruct.Q4_0.gguf")
            config.set("llm", "device", "gpu")

            with open("config.ini", "w") as config_file:
                config.write(config_file)

        return config

    def _setup_gui(self):
        """
        Initialize and configure GUI components.
        """
        self.title("GPTScrape")
        self.geometry("500x300")  # Set the window size

        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL input
        ttk.Label(main_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.url_input = ttk.Entry(main_frame, width=50)
        self.url_input.grid(row=0, column=1, padx=5, pady=5)

        # Input text
        ttk.Label(main_frame, text="Input:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.input_textbox = Text(main_frame, width=50, height=10)
        self.input_textbox.grid(row=1, column=1, padx=5, pady=5)

        # Scrape button
        self.scrape_button = ttk.Button(main_frame, text="Scrape", command=self._start_scrape)
        self.scrape_button.grid(row=2, column=0, columnspan=2, pady=10)

    def _start_scrape(self):
        """
        Start the scraping task.
        """
        if self.scraper is None:
            self.scraper = GPTScraper(
                nlp_model_name=self.config.get("nlp", "model_name"),
                llm_model_name=self.config.get("llm", "model_name"),
                llm_device=self.config.get("llm", "device"),
            )
        self.loop.create_task(
            self.scraper.scrape_async(self.url_input.get(), self.input_textbox.get("1.0", "end"))
        )

    async def _updater(self, interval: float):
        """
        Continuously update the GUI at the specified interval.
        """
        while True:
            self.update()
            await asyncio.sleep(interval)

    def close(self):
        """
        Handle application closure, including stopping tasks and cleaning up resources.
        """
        logger.debug("Shutting down application")
        for task in self.tasks:
            task.cancel()
        if self.scraper:
            self.scraper.quit()
        self.loop.stop()
        self.destroy()


if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = App(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        logger.debug("Application interrupted by user")
    finally:
        loop.close()
        logger.debug("Event loop closed")
