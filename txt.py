class text:
    def __init__(self, content):
        self.content = content

    def get_chunks(self, chunk_size=3):
        words = self.content.split()
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks
