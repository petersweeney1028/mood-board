from colorthief import ColorThief
import requests
from io import BytesIO

def get_color_palette(image_urls, color_count=5):
    colors = []
    for url in image_urls:
        response = requests.get(url)
        img = BytesIO(response.content)
        color_thief = ColorThief(img)
        palette = color_thief.get_palette(color_count=color_count)
        colors.extend(palette)
    
    # Combine and average colors to get a final palette
    final_palette = []
    for i in range(color_count):
        r = int(sum([color[i][0] for color in colors]) / len(colors))
        g = int(sum([color[i][1] for color in colors]) / len(colors))
        b = int(sum([color[i][2] for color in colors]) / len(colors))
        final_palette.append((r, g, b))
    
    return final_palette
