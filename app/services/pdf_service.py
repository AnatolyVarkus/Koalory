from fpdf import FPDF
from io import BytesIO
import re


class PDFWithImages(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def add_wrapped_text(self, text: str, image_map: dict[int, BytesIO]):
        parts = re.split(r"ILLUSTRATION_(\d)", text)

        i = 0
        while i < len(parts):
            chunk = parts[i].strip().replace("[", "").replace("]", "")
            if chunk:
                self.multi_cell(0, 8, chunk)
                self.ln(2)

            if i + 1 < len(parts):
                img_num = int(parts[i + 1])
                image = image_map.get(img_num)
                if image:
                    self.ln(2)
                    page_width = self.w - 2 * self.l_margin
                    self.image(image, w=page_width)
                    self.ln(2)
            i += 2


def normalize_ascii(text: str) -> str:
    try:
        text = (
            text.replace("–", "-")
                .replace("—", "-")
                .replace("‘", "'")
                .replace("’", "'")
                .replace("“", '"')
                .replace("”", '"')
        )
    except Exception as e:
        pass
    return text

def test_text(body: str):
    try:
        re.split(r"ILLUSTRATION_(\d)", body)
    except Exception as e:
        return False
    return True

def generate_pdf(title: str, body: str, image_urls: list[bytes]):
    image_map = {}
    try:
        title = normalize_ascii(title)
        body = normalize_ascii(body)
    except:
        pass
    for i, url in enumerate(image_urls, start=1):
        bio = BytesIO(url)
        bio.name = f"image_{i}.png"
        image_map[i] = bio

    pdf = PDFWithImages()
    pdf.add_font("Bookerly", "", "./app/Bookerly.ttf", uni=True)
    pdf.add_font("BookerlyLight", "", "./app/BookerlyLight.ttf", uni=True)

    # Set fonts
    pdf.set_font("Bookerly", size=24)
    pdf.multi_cell(0, 10, title, align="C")
    pdf.ln(10)
    pdf.set_font("BookerlyLight", size=16)

    # Inject text and images
    pdf.add_wrapped_text(body, image_map)

    output = BytesIO()
    pdf_bytes = pdf.output(dest="S")
    output.write(pdf_bytes)
    output.seek(0)
    return output