import logging
import spacy
from gpt4all import GPT4All
import nodriver
import time
from typing import Optional
from utilities import clean_text, generate_css_selector

logger = logging.getLogger(__name__)


class GPTScraper:
    def __init__(
        self,
        nlp_model_name: str,
        llm_model_name: str,
        llm_device: Optional[str] = None,
        llm_system_prompt: str = (
            "You are a text-to-JSON converter. Your task is to analyze input text and convert it into a structured JSON object that describes the content.\n"
            "You only respond with the json output in a codeblock!\n"
            "The JSON output must:\n"
            "- Be valid JSON and not include any comments or extraneous text.\n"
            "- Be flat, containing no nested objects. Each piece of data must be a separate key-value pair.\n"
            "- Store everything as strings, NO MATTER WHAT!"
        ),
    ):
        logger.debug("Loading spaCy model")
        self.nlp = spacy.load(nlp_model_name)
        logger.info("Loaded spaCy model")

        logger.debug("Loading GPT4All model")
        self.llm = GPT4All(model_name=llm_model_name, device=llm_device)
        logger.info("Loaded GPT4All model")

        self.llm_system_prompt = llm_system_prompt
        logger.debug("Set LLM system prompt")

        self.browser = None
        self.tab = None

    async def scrape_async(self, url: str, text_input: str):
        """
        Scrape the web page at the given URL and process the content based on the provided text input.

        Args:
            url (str): The URL of the web page to scrape.
            text_input (str): The text input to match against the web page content.
        """
        self.browser = await nodriver.start()

        logger.debug("Navigating to URL")
        self.tab = await self.browser.get(url)
        logger.debug("Navigated to URL")

        logger.debug("Locating <body> element")
        body_element = await self.tab.select("body")
        logger.debug("Located <body> element")

        logger.debug("Finding best matching element based on text input")
        start_time = time.perf_counter()
        best_matching_element, _ = self._find_best_match(
            body_element, self.nlp(text_input)
        )
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        logger.info(f"Found best match, took {time_taken:.2f}s")

        elements_selector = generate_css_selector(best_matching_element)
        scraped_elements_texts = [
            clean_text(element.text_all)
            for element in await self.tab.query_selector_all(elements_selector)
        ]
        logger.info(f"Found {len(scraped_elements_texts)} elements")

        with self.llm.chat_session(self.llm_system_prompt):
            for scraped_element_text in scraped_elements_texts:
                start_time = time.perf_counter()

                output = self.llm.generate(
                    scraped_element_text, max_tokens=256, temp=0.01
                )
                json_output = output[
                    output.index("```") + 3 : output.rindex("```")
                ].strip()

                end_time = time.perf_counter()
                time_taken = end_time - start_time
                logger.info(f"{json_output} # took {time_taken:.2f}s")

    def _calculate_element_similarity_score(self, element, document) -> float:
        """
        Calculate the similarity score between an HTML element's text and a given document.

        Args:
            element: The HTML element.
            document: The spaCy document to compare against.

        Returns:
            float: The similarity score.
        """
        score = self.nlp(element.text_all).similarity(document)
        return score + 0.1 if element.tag_name in ["div", "a"] else score

    def _find_best_match(
        self, element, document, best_match=None, best_score=float("-inf")
    ):
        """
        Recursively find the best matching HTML element based on similarity to the given document.

        Args:
            element: The current HTML element.
            document: The spaCy document to compare against.
            best_match: The current best match (used for recursion).
            best_score: The current best score (used for recursion).

        Returns:
            tuple: The best matching element and its similarity score.
        """
        score = self._calculate_element_similarity_score(element, document)
        if score > best_score:
            best_score = score
            best_match = element

        for child in element.children:
            child_best_match, child_best_score = self._find_best_match(
                child, document, best_match, best_score
            )
            if child_best_score > best_score:
                best_score = child_best_score
                best_match = child_best_match

        return best_match, best_score

    def quit(self):
        """
        Clean up resources by closing the LLM model and browser.
        """
        if self.nlp:
            del self.nlp
        if self.llm:
            self.llm.close()
        if self.browser and not self.browser.stopped:
            if self.tab and not self.tab.closed:
                self.tab.close()
            self.browser.stop()
