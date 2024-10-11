from flask import Blueprint, render_template, jsonify, request, send_file
from flask_login import login_required, current_user
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random
from color_analysis import get_color_palette

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
    
    wallpaper = create_wallpaper_image(template, color_palette, spotify_albums)
    
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

def create_wallpaper_image(template, color_palette, spotify_albums):
    wallpaper = Image.new('RGB', (1242, 2688))  # iPhone 12 Pro Max resolution
    draw = ImageDraw.Draw(wallpaper)

    wallpaper.paste(tuple(color_palette[0]), [0, 0, wallpaper.size[0], wallpaper.size[1]])

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
            img = img.resize((pos[2] - pos[0], pos[3] - pos[1]), Image.LANCZOS)
            wallpaper.paste(img, pos)

    font = ImageFont.load_default()
    draw.text((wallpaper.size[0] // 2, 50), "My Spotify Moodboard", fill=tuple(color_palette[1]), font=font, anchor="mm")

    return wallpaper
