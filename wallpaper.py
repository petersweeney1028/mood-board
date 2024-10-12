from flask import Blueprint, render_template, jsonify, request, send_file, current_app
from flask_login import login_required, current_user
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import random
from color_analysis import get_color_palette
import math

wallpaper_bp = Blueprint('wallpaper', __name__)

@wallpaper_bp.route('/create')
@login_required
def create_wallpaper():
    current_app.logger.info(f"User {current_user.id} accessed wallpaper creation page")
    return render_template('create_wallpaper.html')

@wallpaper_bp.route('/api/fetch_content')
@login_required
def fetch_content():
    current_app.logger.info(f"Fetching content for user {current_user.id}")
    spotify_albums = fetch_spotify_albums(current_user.spotify_token)
    
    color_palette = get_color_palette([img['url'] for img in spotify_albums])
    template = select_template(color_palette)
    
    current_app.logger.info(f"Content fetched successfully for user {current_user.id}")
    return jsonify({
        'spotify': spotify_albums,
        'color_palette': color_palette,
        'template': template
    })

@wallpaper_bp.route('/api/generate_wallpaper', methods=['POST'])
@login_required
def generate_wallpaper():
    current_app.logger.info(f"Generating wallpaper for user {current_user.id}")
    data = request.json
    if not data:
        current_app.logger.error("No data received for wallpaper generation")
        return jsonify({"error": "No data provided"}), 400

    template = data.get('template')
    color_palette = data.get('color_palette')
    spotify_albums = data.get('spotify')
    custom_text = data.get('custom_text', '')
    text_size = data.get('text_size', 48)
    filter_type = data.get('filter', 'none')
    stickers = data.get('stickers', [])
    sticker_size = data.get('sticker_size', 72)
    sticker_rotation = data.get('sticker_rotation', 0)
    sticker_opacity = data.get('sticker_opacity', 255)
    
    if not all([template, color_palette, spotify_albums]):
        current_app.logger.error("Missing required data for wallpaper generation")
        return jsonify({"error": "Missing required data"}), 400

    current_app.logger.info(f"Wallpaper options: template={template}, filter={filter_type}, text_size={text_size}, sticker_count={len(stickers)}")
    
    try:
        wallpaper = create_wallpaper_image(template, color_palette, spotify_albums, custom_text, text_size, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity)
        
        img_io = BytesIO()
        wallpaper.save(img_io, 'PNG')
        img_io.seek(0)
        
        current_app.logger.info(f"Wallpaper generated successfully for user {current_user.id}")
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        current_app.logger.error(f"Error generating wallpaper: {str(e)}")
        return jsonify({"error": "Failed to generate wallpaper"}), 500

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

def create_wallpaper_image(template, color_palette, spotify_albums, custom_text, text_size, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity):
    wallpaper = Image.new('RGB', (1242, 2688))  # iPhone 12 Pro Max resolution
    draw = ImageDraw.Draw(wallpaper)

    wallpaper.paste(tuple(color_palette[0]), (0, 0, wallpaper.width, wallpaper.height))

    if template == 'template1.svg':
        positions = [(62, 134, 1180, 1252), (62, 1436, 1180, 2554)]
    elif template == 'template2.svg':
        positions = [(62, 134, 1180, 693), (62, 1995, 1180, 2554), (621 - 559, 1344 - 559, 621 + 559, 1344 + 559)]
    else:  # template3.svg
        positions = [(62, 134, 621, 1252), (621, 134, 1180, 1252), (62, 1436, 1180, 2554)]

    for i, pos in enumerate(positions):
        if i < len(spotify_albums):
            img_url = spotify_albums[i]['url']
            response = requests.get(img_url)
            img = Image.open(BytesIO(response.content))
            img = img.resize((pos[2] - pos[0], pos[3] - pos[1]), Image.Resampling.LANCZOS)
            wallpaper.paste(img, pos)

    wallpaper = apply_filter(wallpaper, filter_type)

    if custom_text:
        font = ImageFont.truetype("arial.ttf", text_size)
        left, top, right, bottom = font.getbbox(custom_text)
        text_width = right - left
        text_height = bottom - top
        text_position = ((wallpaper.width - text_width) // 2, 50)
        draw.text(text_position, custom_text, fill=tuple(color_palette[1]), font=font)

    place_stickers(wallpaper, stickers, color_palette, positions, sticker_size, sticker_rotation, sticker_opacity)

    return wallpaper

def apply_filter(image, filter_type):
    if filter_type == 'grayscale':
        return ImageOps.grayscale(image).convert('RGB')
    elif filter_type == 'sepia':
        return apply_sepia(image)
    elif filter_type == 'blur':
        return image.filter(ImageFilter.GaussianBlur(radius=5))
    elif filter_type == 'vintage':
        return apply_vintage(image)
    elif filter_type == 'vignette':
        return apply_vignette(image)
    elif filter_type == 'edge_enhance':
        return image.filter(ImageFilter.EDGE_ENHANCE)
    elif filter_type == 'emboss':
        return image.filter(ImageFilter.EMBOSS)
    elif filter_type == 'sharpen':
        return image.filter(ImageFilter.SHARPEN)
    elif filter_type == 'color_swap':
        return apply_color_swap(image)
    else:
        return image

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

def apply_color_swap(image):
    r, g, b = image.split()
    return Image.merge("RGB", (b, r, g))

def place_stickers(wallpaper, stickers, color_palette, positions, sticker_size, sticker_rotation, sticker_opacity):
    width, height = wallpaper.size
    grid_size = 100
    grid = [[False for _ in range(height // grid_size + 1)] for _ in range(width // grid_size + 1)]

    for pos in positions:
        for x in range(pos[0] // grid_size, pos[2] // grid_size + 1):
            for y in range(pos[1] // grid_size, pos[3] // grid_size + 1):
                if x < len(grid) and y < len(grid[0]):
                    grid[x][y] = True

    for sticker in stickers:
        sticker_font = ImageFont.truetype("arial.ttf", sticker_size)
        left, top, right, bottom = sticker_font.getbbox(sticker)
        sticker_width = right - left
        sticker_height = int((bottom - top) * 1.2)
        
        valid_placement = False
        max_attempts = 50
        attempts = 0
        
        while not valid_placement and attempts < max_attempts:
            x = random.randint(0, width - sticker_width)
            y = random.randint(0, height - sticker_height)
            
            grid_x, grid_y = x // grid_size, y // grid_size
            if not grid[grid_x][grid_y]:
                valid_placement = True
                grid[grid_x][grid_y] = True
            
            attempts += 1
        
        if valid_placement:
            sticker_img = Image.new('RGBA', (sticker_width, sticker_height), (0, 0, 0, 0))
            sticker_draw = ImageDraw.Draw(sticker_img)
            sticker_draw.text((0, 0), sticker, fill=tuple(color_palette[2 % len(color_palette)] + (sticker_opacity,)), font=sticker_font)
            
            rotated_sticker = sticker_img.rotate(sticker_rotation, expand=True, resample=Image.Resampling.BICUBIC)
            
            wallpaper.paste(rotated_sticker, (x, y), rotated_sticker)
