from fpdf import FPDF
import requests
from io import BytesIO
import re


class PDFWithImages(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_page()

    def add_wrapped_text(self, text: str, image_map: dict[int, BytesIO]):
        # Split the text on ILLUSTRATION_n markers
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
        parts = re.split(r"ILLUSTRATION_(\d)", body)
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
    pdf.set_font("Bookerly", size=20)
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
#
# body='[ILLUSTRATION_1]\n\nIn the bustling city of Moscow, there lived an 18-year-old boy named Tolya. With his light brown quiff hairstyle and piercing blue eyes, he stood out in a crowd. Tolya had a passion that set him apart from his friends – he loved to dance in the woods.\n\nOne crisp autumn morning, Tolya decided to venture into the nearby forest for inspiration. As he zipped up his black jacket over his gray hoodie, he couldn\'t contain his excitement. The whimsical trees seemed to sway in welcome as he stepped onto the the woodland [ILLUSTRATION_2]\n\nAs Tolya walked deeper into the forest, he noticed something unusual. The leaves on the ground changing colors, but not in the typical autumn shades. Instead, they shimmered with vibrant blues, purples, and silvers. Intrigued, Tolya moved closer to investigate.\n\nSuddenly, a gust of wind swept through the trees, and the colorful leaves began to swirl around him. Tolya felt a rhythm in the air, and without thinking, he started to dance. His body moved in harmony with the swirling leaves, creating a mesmerizing spectacle.\n\n[ILLUSTRATION_3]\n\nAs Tolya danced, he noticed the forest coming to life around him. Flowers bloomed in his footsteps, and the trees seemed to lean in to watch. Even the animals emerged from their hiding spots, captivated by his performance.\n\n"This is amazing!" Tolya exclaimed, twirling with joy. "I\'ve never felt so connected to nature before!"\n\n[ILLUSTRATION_4]\n\nInspired by his surroundings, Tolya began to experiment with new moves. He incorporated the graceful sway of the branches, the playful hops of rabbits, and the elegant flight of birds into his dance. With each step, his creativity flourished, and his dance became more extraordinary beautiful fusion of human.\n\nAs the day wore on, Tolya realized he had unintentionally created a new dance style – one that celebrated the beauty and rhythm of the forest. He decided to call it "Forest whirl."\n\n[ILLUSTRATION_5]\n\nExcited to share his discovery, Tolya rushed back to the city. He gathered his friends in the local park and showed them the Woodland Whirl. At first, they were skeptical, but as Tolya danced, they couldn\'t help but join in.\n\nSoon, a crowd gathered, mesmerized by the unique dance style. People of all ages started to move, imitating the flow of leaves and the grace of forest creatures. The park came alive with the spirit of the woods, right in the heart of Moscow.\n\n[ILLUSTRATION_6]\n\nIn the following weeks, Woodland Whirl became a sensation. Dance schools invited Tolya to teach, and people flocked to the forests for inspiration. Tolya\'s creativity had not only won him recognition but had also brought a piece of nature\'s magic into the city.\n\nAs Tolya watched people dancing in the park, imitating the movements he had created, he smiled. His love for dancing in the woods had turned into something beautiful that everyone could enjoy. He realized that when you follow your passion and let your creativity flow, wonderful things can happen.\n\nThis story teaches the value of embracing one\'s unique interests and how creativity can bring joy to others and connect people with nature.'
# title="Tolya's Woodland Dance Adventure"
# body = normalize_ascii(body)
# title = normalize_ascii(title)
#
# # Usage
# generate_pdf(
#     title=title,
#     body=body,
#         image_urls=['https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/2a446d59-55f8-4221-8438-9950415c0340/Leonardo_Phoenix_10_Tolya_an_18yearold_boy_with_a_Quiff_hairst_0.jpg', 'https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/74452e4c-2c98-4c20-8492-d941f673ac2d/Leonardo_Phoenix_10_Tolya_an_18yearold_boy_with_a_Quiff_hairst_0.jpg', 'https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/adaae72c-f110-4988-8dae-d1727adf7fe3/Leonardo_Phoenix_10_Closeup_of_Tolya_an_18yearold_boy_with_a_Q_0.jpg', 'https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/a76c1c0f-ceed-4e36-a28a-a2deecad07c1/Leonardo_Phoenix_10_Tolya_an_18yearold_boy_with_a_Quiff_hairst_0.jpg', 'https://cdn.leonardo.ai/users/0fad626b-b70d-4f3c-907d-8ee1a30b3e35/generations/ea8e52fd-9345-4c0a-a2e9-67d8d44593d9/Leonardo_Phoenix_10_Wide_shot_of_Tolya_an_18yearold_boy_with_a_0.jpg'],  # list of 6 image URLs
#     output_path="tolya_story.pdf"
# )