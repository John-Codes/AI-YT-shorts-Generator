import logging

class TextProcessor:
    def __init__(self, sentences_data_path="text_content.txt"):
        self.sentences_data_path = sentences_data_path
        self.logger = logging.getLogger(__name__)

    def get_sentences(self):
        """
        Reads sentences from the text content file.
        Returns a dictionary where keys are sentence indices (S0, S1, ...)
        and values are tuples of (words, sentence_text).
        """
        sentences = {}
        try:
            with open(self.sentences_data_path, 'r') as file:
                content = file.read().strip()
                if not content:
                    self.logger.warning("Text content file is empty.")
                    return sentences  # Return empty dictionary

                # Simple splitting by newline, adjust as needed
                sentence_list = content.splitlines()

                if not sentence_list:
                    self.logger.warning("No sentences found after splitting content.")
                    return sentences

                for idx, sentence_text in enumerate(sentence_list):
                    words = sentence_text.split() # Simple word split
                    sentences[f"S{idx}"] = (words, sentence_text.strip())
        except FileNotFoundError:
            self.logger.error(f"File not found: {self.sentences_data_path}")
        except Exception as e:
            self.logger.error(f"Error reading text content file: {e}")
        return sentences

if __name__ == "__main__":
    # Example usage and basic test
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    processor = TextProcessor()
    sentences = processor.get_sentences()
    if sentences:
        logging.info(f"Sentences loaded: {sentences}")
    else:
        logging.warning("No sentences were loaded.")
