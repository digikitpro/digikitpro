from PIL import Image, ImageDraw, ImageFont
G = (201, 168, 106); BG = (10, 10, 12); MUT = (170, 167, 160)
base = "/usr/share/fonts/truetype/dejavu/"

im = Image.new("RGB", (180, 180), BG); d = ImageDraw.Draw(im)
d.rounded_rectangle((0, 0, 179, 179), radius=36, fill=BG)
d.ellipse((34, 34, 146, 146), outline=G, width=4)
f = ImageFont.truetype(base + "DejaVuSerif-Bold.ttf", 62)
d.text((90, 86), "D", font=f, fill=G, anchor="mm")
im.save("/home/user/assets/img/apple-touch-icon.png")

im = Image.new("RGB", (1200, 630), BG); d = ImageDraw.Draw(im)
for r in range(300, 0, -2):
    shade = int(16 + 26 * (1 - r / 300))
    d.ellipse((600 - r * 1.6, 430 - r, 600 + r * 1.6, 430 + r), outline=(shade, shade - 3, shade - 6))
f1 = ImageFont.truetype(base + "DejaVuSerif-Bold.ttf", 106)
f2 = ImageFont.truetype(base + "DejaVuSans.ttf", 34)
f3 = ImageFont.truetype(base + "DejaVuSans.ttf", 25)
d.text((600, 268), "DigiKitPro", font=f1, fill=G, anchor="mm")
d.text((600, 368), "Professional Procreate Tools for Artists", font=f2, fill=(245, 242, 235), anchor="mm")
d.text((600, 430), "Portraits · Line Art · Watercolor · Anime · Bundles", font=f3, fill=MUT, anchor="mm")
d.line((450, 490, 750, 490), fill=G, width=2)
im.save("/home/user/assets/img/og-cover.jpg", quality=86)
print("brand assets written")
