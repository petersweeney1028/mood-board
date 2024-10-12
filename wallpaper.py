from flask import Blueprint, render_template, jsonify, request, send_file, current_app
from flask_login import login_required, current_user
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
from color_analysis import get_color_palette

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
    
    current_app.logger.info(f"Content fetched successfully for user {current_user.id}")
    return jsonify({
        'spotify': spotify_albums,
        'color_palette': color_palette
    })

@wallpaper_bp.route('/api/generate_wallpaper', methods=['POST'])
@login_required
def generate_wallpaper():
    current_app.logger.info(f"Generating wallpaper for user {current_user.id}")
    data = request.json
    if not data:
        current_app.logger.error("No data received for wallpaper generation")
        return jsonify({"error": "No data provided"}), 400

    color_palette = data.get('color_palette')
    spotify_albums = data.get('spotify')
    custom_text = data.get('custom_text', '')
    font = data.get('font', 'Arial')
    text_size = data.get('text_size', 24)
    text_color = data.get('text_color', '#FFFFFF')
    filter_type = data.get('filter', 'none')
    stickers = data.get('stickers', [])
    
    if not all([color_palette, spotify_albums]):
        current_app.logger.error("Missing required data for wallpaper generation")
        return jsonify({"error": "Missing required data"}), 400

    current_app.logger.info(f"Wallpaper options: filter={filter_type}, text_size={text_size}, sticker_count={len(stickers)}")
    
    try:
        wallpaper = create_wallpaper_image(color_palette, spotify_albums, custom_text, font, text_size, text_color, filter_type, stickers)
        
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

def create_wallpaper_image(color_palette, spotify_albums, custom_text, font, text_size, text_color, filter_type, stickers):
    wallpaper = Image.new('RGB', (1242, 2688))  # iPhone 12 Pro Max resolution
    draw = ImageDraw.Draw(wallpaper)

    # Create a gradient background
    create_gradient_background(wallpaper, color_palette)

    # Add album covers
    add_album_covers(wallpaper, spotify_albums)

    # Add custom text
    if custom_text:
        add_custom_text(wallpaper, custom_text, font, text_size, text_color)

    # Add stickers
    add_stickers(wallpaper, stickers)

    # Apply filter
    wallpaper = apply_filter(wallpaper, filter_type)

    return wallpaper

def create_gradient_background(image, color_palette):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    color1 = tuple(color_palette[0])
    color2 = tuple(color_palette[-1])
    
    for y in range(height):
        r = int(color1[0] + (color2[0] - color1[0]) * y / height)
        g = int(color1[1] + (color2[1] - color1[1]) * y / height)
        b = int(color1[2] + (color2[2] - color1[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

def add_album_covers(image, spotify_albums):
    width, height = image.size
    album_size = width // 3
    padding = 20

    for i, album in enumerate(spotify_albums[:5]):
        response = requests.get(album['url'])
        album_img = Image.open(BytesIO(response.content))
        album_img = album_img.resize((album_size, album_size), Image.LANCZOS)
        
        x = (i % 3) * (album_size + padding)
        y = (i // 3) * (album_size + padding) + height // 3
        
        image.paste(album_img, (x, y))

def add_custom_text(image, text, font_name, font_size, text_color):
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype(f"{font_name}.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
    position = ((image.width - text_width) // 2, image.height // 4 - text_height // 2)
    
    draw.text(position, text, font=font, fill=text_color)

def add_stickers(image, stickers):
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    for sticker in stickers:
        size = random.randint(50, 100)
        x = random.randint(0, width - size)
        y = random.randint(0, height - size)
        draw.text((x, y), sticker, font=ImageFont.truetype("arial.ttf", size), fill=(255, 255, 255))

def apply_filter(image, filter_type):
    if filter_type == 'grayscale':
        return image.convert('L').convert('RGB')
    elif filter_type == 'sepia':
        return apply_sepia(image)
    elif filter_type == 'blur':
        return image.filter(ImageFilter.GaussianBlur(radius=5))
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
