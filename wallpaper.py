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
    album_opacity = data.get('album_opacity', 255)
    border_width = data.get('border_width', 0)
    border_color = data.get('border_color', '#000000')
    
    if not all([template, color_palette, spotify_albums]):
        current_app.logger.error("Missing required data for wallpaper generation")
        return jsonify({"error": "Missing required data"}), 400

    current_app.logger.info(f"Wallpaper options: template={template}, filter={filter_type}, text_size={text_size}, sticker_count={len(stickers)}, album_opacity={album_opacity}, border_width={border_width}")
    
    try:
        wallpaper = create_wallpaper_image(template, color_palette, spotify_albums, custom_text, text_size, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity, album_opacity, border_width, border_color)
        
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

def create_wallpaper_image(template, color_palette, spotify_albums, custom_text, text_size, filter_type, stickers, sticker_size, sticker_rotation, sticker_opacity, album_opacity, border_width, border_color):
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
            
            # Apply album opacity
            img = Image.blend(Image.new('RGB', img.size, (255, 255, 255)), img, album_opacity / 255)
            
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

    # Apply border
    if border_width > 0:
        draw = ImageDraw.Draw(wallpaper)
        draw.rectangle([(0, 0), (wallpaper.width - 1, wallpaper.height - 1)], outline=border_color, width=border_width)

    return wallpaper

# The rest of the functions (apply_filter, apply_sepia, apply_vintage, apply_vignette, apply_color_swap, place_stickers) remain the same
