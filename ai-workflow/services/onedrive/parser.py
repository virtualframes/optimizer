from bs4 import BeautifulSoup

def extract_note_points(html: str) -> list[dict]:
    """Parse HTML to extract bullet points, headings, and notes."""
    soup = BeautifulSoup(html, "html.parser")
    points = []
    for elem in soup.select("p, li, h1, h2, h3"):
        text = elem.get_text(strip=True)
        if text:
            points.append({
                "type": elem.name,
                "text": text
            })
    return points