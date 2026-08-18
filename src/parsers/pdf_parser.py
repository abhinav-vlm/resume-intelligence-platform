import fitz

def extract_text(pdf_bytes:bytes)->str:
    doc = fitz.open(stream=pdf_bytes,filetype="pdf")
    text = ""

    for page in doc:
        text += page.get_text()
        
    return text

def extract_links(pdf_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    all_links = []

    for page_number, page in enumerate(doc):
        for link in page.get_links():
            uri = link.get("uri")

            if uri and uri.startswith("https"):
                all_links.append({
                    "url": uri,
                    "bbox": tuple(link["from"]),
                    "page": page_number
                })
    return all_links

def extract_text_blocks(pdf_bytes: bytes) -> list[dict]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    blocks = []

    for page_number, page in enumerate(doc):
        page_data = page.get_text("dict")

        for block in page_data["blocks"]:
            if block.get("type") != 0:
                continue

            for line in block.get("lines", []):
                text = "".join(
                    span["text"]
                    for span in line.get("spans", [])
                ).strip()

                if text:
                    blocks.append({
                        "text": text,
                        "bbox": line["bbox"],
                        "page": page_number
                    })

    return blocks