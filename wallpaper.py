from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import random
from color_analysis import get_color_palette
import math

wallpaper_bp = Blueprint('wallpaper', __name__)

@wallpaper_bp.route('/create')
@login_required
def create_wallpaper():
    return render_template('create_wallpaper.html')

@wallpaper_bp.route('/api/fetch_content')
@login_required
def fetch_content():
    spotify_albums = fetch_spotify_albums(current_user.spotify_token)
    
    color_palette = get_color_palette([img['url'] for img in spotify_albums])
    template = select_template(color_palette)
    
    return jsonify({
        'spotify': spotify_albums,
        'color_palette': color_palette,
        'template': template
    })

@wallpaper_bp.route('/api/generate_wallpaper', methods=['POST'])
@login_required
def generate_wallpaper():
    data = request.json
    template = data['template']
    color_palette = data['color_palette']
    spotify_albums = data['spotify']
    custom_text = data['custom_text']
    filter_type = data['filter']
    stickers = data['stickers']
    sticker_size = data['sticker_size']
    sticker_rotation = data.get('sticker_rotation', 0)
    sticker_opacity = data.get('sticker_opacity', 255)
    text_size = data.get('text_size', 48)  # New parameter for text size
    
    wallpaper = create_wallpaper_image(template, color_palette, spotify_albums, custom_text, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity, text_size)
    
    img_io = BytesIO()
    wallpaper.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

def fetch_spotify_albums(access_token):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()['items']
        return [{'url': track['album']['images'][0]['url'], 'name': track['name']} for track in data][:5]
    return []

def select_template(color_palette):
    templates = ['template1.svg', 'template2.svg', 'template3.svg']
    return random.choice(templates)

def create_wallpaper_image(template, color_palette, spotify_albums, custom_text, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity, text_size):
    wallpaper = Image.new('RGB', (1242, 2688))  # iPhone 12 Pro Max resolution
    draw = ImageDraw.Draw(wallpaper)

    # Set background color
    wallpaper.paste(tuple(color_palette[0]), [0, 0, wallpaper.size[0], wallpaper.size[1]])

    # Apply template
    if template == 'template1.svg':
        positions = [(62, 134, 1180, 1252), (62, 1436, 1180, 2554)]
    elif template == 'template2.svg':
        positions = [(62, 134, 1180, 693), (62, 1995, 1180, 2554), (621 - 559, 1344 - 559, 621 + 559, 1344 + 559)]
    else:  # template3.svg
        positions = [(62, 134, 621, 1252), (621, 134, 1180, 1252), (62, 1436, 1180, 2554)]

    # Place album covers
    for i, pos in enumerate(positions):
        if i < len(spotify_albums):
            img_url = spotify_albums[i]['url']
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((pos[2] - pos[0], pos[3] - pos[1]), Image.LANCZOS)
            wallpaper.paste(img, pos)

    # Apply filter
    if filter_type == 'grayscale':
        wallpaper = wallpaper.convert('L').convert('RGB')
    elif filter_type == 'sepia':
        wallpaper = apply_sepia(wallpaper)
    elif filter_type == 'blur':
        wallpaper = wallpaper.filter(ImageFilter.GaussianBlur(radius=5))
    elif filter_type == 'vintage':
        wallpaper = apply_vintage(wallpaper)
    elif filter_type == 'vignette':
        wallpaper = apply_vignette(wallpaper)

    # Add custom text with adjustable size
    if custom_text:
        font = ImageFont.truetype("arial.ttf", text_size)
        text_width, text_height = draw.textsize(custom_text, font=font)
        text_position = ((wallpaper.width - text_width) // 2, 50)
        draw.text(text_position, custom_text, fill=tuple(color_palette[1]), font=font)

    # Add stickers with improved placement, rotation, and opacity
    for sticker in stickers:
        sticker_font = ImageFont.truetype("arial.ttf", sticker_size)
        sticker_width, sticker_height = draw.textsize(sticker, font=sticker_font)
        
        # Improve sticker placement to avoid overlap with album covers
        valid_placement = False
        max_attempts = 50
        attempts = 0
        
        while not valid_placement and attempts < max_attempts:
            x = random.randint(0, wallpaper.width - sticker_width)
            y = random.randint(0, wallpaper.height - sticker_height)
            
            # Check if the sticker overlaps with any album cover
            overlap = any(pos[0] < x < pos[2] and pos[1] < y < pos[3] for pos in positions)
            
            if not overlap:
                valid_placement = True
            
            attempts += 1
        
        if valid_placement:
            # Create a new image for the rotated sticker
            sticker_img = Image.new('RGBA', (sticker_width, sticker_height), (0, 0, 0, 0))
            sticker_draw = ImageDraw.Draw(sticker_img)
            sticker_draw.text((0, 0), sticker, fill=tuple(color_palette[2 % len(color_palette)] + (sticker_opacity,)), font=sticker_font)
            
            # Rotate the sticker
            rotated_sticker = sticker_img.rotate(sticker_rotation, expand=True, resample=Image.BICUBIC)
            
            # Paste the rotated sticker onto the wallpaper
            wallpaper.paste(rotated_sticker, (x, y), rotated_sticker)

    return wallpaper

def apply_sepia(image):
    width, height = image.size
    pixels = image.load()
    for py in range(height):
        for px in range(width):
            r, g, b = image.getpixel((px, py))
            tr = int(0.393 * r + 0.769 * g + 0.189 * b)
            tg = int(0.349 * r + 0.686 * g + 0.168 * b)
            tb = int(0.272 * r + 0.534 * g + 0.131 * b)
            pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
    return image

def apply_vintage(image):
    sepia_image = apply_sepia(image)
    enhancer = ImageEnhance.Contrast(sepia_image)
    return enhancer.enhance(0.8)

def apply_vignette(image):
    width, height = image.size
    mask = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(mask)
    for i in range(20):
        box = [i, i, width - i, height - i]
        draw.rectangle(box, fill=255 - i * 10)
    blurred_mask = mask.filter(ImageFilter.GaussianBlur(radius=10))
    return Image.composite(image, Image.new('RGB', (width, height), (0, 0, 0)), blurred_mask)
