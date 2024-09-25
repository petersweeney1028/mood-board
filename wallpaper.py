from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
import requests
from PIL import Image
from io import BytesIO
from color_analysis import get_color_palette
import random

wallpaper_bp = Blueprint('wallpaper', __name__)

@wallpaper_bp.route('/create_wallpaper')
@login_required
def create_wallpaper():
    return render_template('create_wallpaper.html')

@wallpaper_bp.route('/api/fetch_content')
@login_required
def fetch_content():
    instagram_media = fetch_instagram_media()
    spotify_albums = fetch_spotify_albums()
    
    color_palette = get_color_palette(instagram_media + spotify_albums)
    template = select_template(color_palette)
    
    return jsonify({
        'instagram': instagram_media,
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
    instagram_media = data['instagram']
    spotify_albums = data['spotify']
    
    # Generate wallpaper using PIL
    wallpaper = create_wallpaper_image(template, color_palette, instagram_media, spotify_albums)
    
    # Save wallpaper to a BytesIO object
    img_io = BytesIO()
    wallpaper.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

def fetch_instagram_media():
    # Implement Instagram API call to fetch user's recent media
    # Return a list of image URLs
    pass

def fetch_spotify_albums():
    # Implement Spotify API call to fetch user's top albums
    # Return a list of album cover URLs
    pass

def select_template(color_palette):
    # Select a template based on the color palette
    templates = ['template1.svg', 'template2.svg', 'template3.svg']
    return random.choice(templates)

def create_wallpaper_image(template, color_palette, instagram_media, spotify_albums):
    # Implement wallpaper generation using PIL
    # This is a placeholder implementation
    wallpaper = Image.new('RGB', (1242, 2688))  # iPhone 12 Pro Max resolution
    # Add logic to composite images and apply color palette
    return wallpaper
