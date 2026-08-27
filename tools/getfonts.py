import re, urllib.request, os

os.makedirs("/home/user/assets/fonts", exist_ok=True)
URL = ("https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500;1,600"
       "&family=Manrope:wght@400;500;600;700;800&display=swap")
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"})
css = urllib.request.urlopen(req, timeout=30).read().decode()

blocks = re.findall(r"/\* (\w+) \*/\s*@font-face\s*{([^}]+)}", css, re.S)
done = set()
for subset, body in blocks:
    if subset != "latin":
        continue
    fam = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    key = (fam, style, weight)
    if key in done:
        continue
    done.add(key)
    fn = f"{fam.lower().replace(' ', '')}-{weight}{'i' if style == 'italic' else ''}.woff2"
    urllib.request.urlretrieve(url, "/home/user/assets/fonts/" + fn)
    print(fn)
print("total woff2:", len(done))
