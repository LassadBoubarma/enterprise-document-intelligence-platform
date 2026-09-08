from src.chunking import chunk_text

def test_empty_text_returns_no_chunks():
    assert chunk_text("") == []

def test_long_text_is_split_with_overlap():
    text = ("This is a sentence about enterprise software. " * 120).strip()
    chunks = chunk_text(text, chunk_size=300, overlap=50)
    assert len(chunks) > 2
    assert all(chunk.strip() for chunk in chunks)
    assert all(len(chunk) <= 310 for chunk in chunks)
