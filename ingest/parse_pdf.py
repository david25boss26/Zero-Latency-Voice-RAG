from pypdf import PdfReader

def parse_pdf(path : str) -> str:
    reader = PdfReader(path)
    text = []
    for page in reader.pages:
        if page.extract_text():
            text.append(page.extract_text())
    return "\n".join(text)

if __name__ == "__main__":
    text = parse_pdf("../data/manual.pdf")
    print("extracted chars:", len(text))
    