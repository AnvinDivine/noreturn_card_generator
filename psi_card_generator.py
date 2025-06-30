import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import os

# Load template
TEMPLATE_PATH = "A_digital_image_of_a_blank_trading_card_frame_disp.png"
template = Image.open(TEMPLATE_PATH).convert("RGBA")

# Fonts (adjust as needed for your system or upload custom fonts)
def load_font(size):
    return ImageFont.truetype("DejaVuSans-Bold.ttf", size)

# Auto-scale font size for description
def fit_text(draw, text, max_width, max_height, font_path="DejaVuSans-Bold.ttf", max_font=28, min_font=14):
    for font_size in range(max_font, min_font - 1, -1):
        font = ImageFont.truetype(font_path, font_size)
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word
        lines.append(line)
        height = sum([font.getbbox(l)[3] - font.getbbox(l)[1] for l in lines])
        if height <= max_height:
            return lines, font
    return [text], ImageFont.truetype(font_path, min_font)

# Draw text and image over template
def create_card(name, psi_class, difficulty, maintenance, description, artwork_img):
    card = template.copy()
    draw = ImageDraw.Draw(card)

    # Artwork
    if artwork_img:
        artwork = Image.open(artwork_img).convert("RGBA").resize((700, 400))
        card.paste(artwork, (100, 150), artwork)

    # Text fields
    font_title = load_font(48)
    font_sub = load_font(36)
    font_text = load_font(28)

    draw.text((100, 30), name, font=font_title, fill="white")
    draw.text((100, 90), psi_class, font=font_sub, fill="white")

    # Difficulty and maintenance
    if maintenance:
        draw.text((100, 580), f"{difficulty} / Haltung: {maintenance}", font=font_text, fill="white")
    else:
        draw.text((100, 580), difficulty, font=font_text, fill="white")

    # Description (auto-fitted)
    max_width = 800
    max_height = 400
    lines, desc_font = fit_text(draw, description, max_width, max_height)
    y = 640
    for line in lines:
        draw.text((100, y), line, font=desc_font, fill="white")
        y += desc_font.getbbox(line)[3] - desc_font.getbbox(line)[1] + 5

    return card

# Streamlit UI
st.title("🧠 PSI-Karten Generator")

name = st.text_input("Name der PSI-App")
psi_class = st.text_input("PSI-Kraft")
difficulty = st.selectbox("Schwierigkeit", ["leicht (8–12)", "mittel (11–15)", "schwer (15–19)", "ultimativ (23–25)"])
maintenance = st.text_input("Haltungskosten (leer lassen wenn keine)")
description = st.text_area("Beschreibung der App")
artwork = st.file_uploader("Artwork hochladen (PNG oder JPG)", type=["png", "jpg", "jpeg"])

if st.button("Karte erstellen"):
    card = create_card(name, psi_class, difficulty, maintenance, description, artwork)
    buf = io.BytesIO()
    card.save(buf, format="PNG")
    st.image(card, caption="Deine generierte Karte")
    st.download_button("📥 Karte herunterladen", data=buf.getvalue(), file_name=f"{name}.png", mime="image/png")
