from pathlib import Path
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.core.security import redact_sensitive

PDF_DIR = Path(__file__).resolve().parents[2] / "data" / "pdfs"

class DocumentRetriever:
    def __init__(self):
        self.chunks: list[dict] = []
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.matrix = None
        self.refresh()

    def refresh(self) -> None:
        self.chunks.clear()
        for pdf in PDF_DIR.glob("*.pdf"):
            reader = PdfReader(str(pdf))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
            parts = [p.strip() for p in text.split("\n") if len(p.strip()) > 40]
            for i, p in enumerate(parts):
                self.chunks.append({"source": pdf.name, "chunk_id": i, "text": redact_sensitive(p)})
        if self.chunks:
            self.matrix = self.vectorizer.fit_transform([c["text"] for c in self.chunks])

    def search(self, query: str, k: int = 5) -> list[dict]:
        if not self.chunks or self.matrix is None:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).flatten()
        idxs = scores.argsort()[::-1][:k]
        return [{**self.chunks[i], "score": round(float(scores[i]), 4)} for i in idxs if scores[i] > 0]

retriever = DocumentRetriever()
