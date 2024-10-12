document.addEventListener('DOMContentLoaded', () => {
    const loading = document.getElementById('loading');
    const wallpaperCreator = document.getElementById('wallpaper-creator');
    const wallpaperPreview = document.getElementById('wallpaper-preview');
    const templateSelect = document.getElementById('template-select');
    const colorPalette = document.getElementById('color-palette');
    const customText = document.getElementById('custom-text');
    const textSize = document.getElementById('text-size');
    const textSizeValue = document.getElementById('text-size-value');
    const filterSelect = document.getElementById('filter-select');
    const stickerSelection = document.getElementById('sticker-selection');
    const stickerSize = document.getElementById('sticker-size');
    const stickerSizeValue = document.getElementById('sticker-size-value');
    const stickerRotation = document.getElementById('sticker-rotation');
    const stickerRotationValue = document.getElementById('sticker-rotation-value');
    const stickerOpacity = document.getElementById('sticker-opacity');
    const stickerOpacityValue = document.getElementById('sticker-opacity-value');
    const albumOpacity = document.getElementById('album-opacity');
    const albumOpacityValue = document.getElementById('album-opacity-value');
    const borderWidth = document.getElementById('border-width');
    const borderWidthValue = document.getElementById('border-width-value');
    const borderColor = document.getElementById('border-color');
    const regenerateBtn = document.getElementById('regenerate-btn');
    const downloadBtn = document.getElementById('download-btn');

    let contentData = null;
    let selectedStickers = [];

    function showLoading() {
        loading.classList.remove('hidden');
        wallpaperCreator.classList.add('hidden');
    }

    function hideLoading() {
        loading.classList.add('hidden');
        wallpaperCreator.classList.remove('hidden');
    }

    function fetchContent() {
        showLoading();
        fetch('/api/fetch_content')
            .then(response => response.json())
            .then(data => {
                contentData = data;
                updateWallpaperPreview();
                updateColorPalette();
                updateStickerSelection();
                hideLoading();
            })
            .catch(error => {
                console.error('Error fetching content:', error);
                hideLoading();
            });
    }

    function updateWallpaperPreview() {
        wallpaperPreview.innerHTML = `<div class="bg-gray-200 w-full h-full flex items-center justify-center">
            <p class="text-gray-600">Wallpaper Preview</p>
        </div>`;
    }

    function updateColorPalette() {
        colorPalette.innerHTML = '';
        contentData.color_palette.forEach(color => {
            const swatch = document.createElement('div');
            swatch.className = 'w-8 h-8 rounded-full';
            swatch.style.backgroundColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
            colorPalette.appendChild(swatch);
        });
    }

    function updateStickerSelection() {
        const stickers = ['🎵', '🎶', '🎸', '🎹', '🎤', '🎧', '💿', '🔊', '🎼', '🎷', '🎺', '🪕'];
        stickerSelection.innerHTML = '';
        stickers.forEach(sticker => {
            const stickerElement = document.createElement('div');
            stickerElement.className = 'text-3xl cursor-pointer hover:bg-gray-200 p-2 rounded';
            stickerElement.textContent = sticker;
            stickerElement.addEventListener('click', () => toggleSticker(sticker, stickerElement));
            stickerSelection.appendChild(stickerElement);
        });
    }

    function toggleSticker(sticker, element) {
        if (selectedStickers.includes(sticker)) {
            selectedStickers = selectedStickers.filter(s => s !== sticker);
            element.classList.remove('bg-blue-200');
        } else {
            selectedStickers.push(sticker);
            element.classList.add('bg-blue-200');
        }
    }

    function generateWallpaper() {
        const template = templateSelect.value;
        const text = customText.value;
        const textSizeValue = textSize.value;
        const filter = filterSelect.value;
        const size = stickerSize.value;
        const rotation = stickerRotation.value;
        const opacity = stickerOpacity.value;
        const albumOpacityValue = albumOpacity.value;
        const borderWidthValue = borderWidth.value;
        const borderColorValue = borderColor.value;
        
        const data = {
            template: template,
            color_palette: contentData.color_palette,
            spotify: contentData.spotify,
            custom_text: text,
            text_size: parseInt(textSizeValue),
            filter: filter,
            stickers: selectedStickers,
            sticker_size: parseInt(size),
            sticker_rotation: parseInt(rotation),
            sticker_opacity: parseInt(opacity),
            album_opacity: parseInt(albumOpacityValue),
            border_width: parseInt(borderWidthValue),
            border_color: borderColorValue
        };

        fetch('/api/generate_wallpaper', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.blob())
        .then(blob => {
            const url = URL.createObjectURL(blob);
            wallpaperPreview.innerHTML = `<img src="${url}" alt="Generated Wallpaper" class="w-full h-full object-cover">`;
        })
        .catch(error => {
            console.error('Error generating wallpaper:', error);
        });
    }

    regenerateBtn.addEventListener('click', generateWallpaper);

    downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.href = wallpaperPreview.querySelector('img').src;
        link.download = 'spotify_moodboard_wallpaper.png';
        link.click();
    });

    templateSelect.addEventListener('change', generateWallpaper);
    customText.addEventListener('input', generateWallpaper);
    textSize.addEventListener('input', () => {
        textSizeValue.textContent = `${textSize.value}px`;
        generateWallpaper();
    });
    filterSelect.addEventListener('change', generateWallpaper);
    stickerSize.addEventListener('input', () => {
        stickerSizeValue.textContent = `${stickerSize.value}px`;
        generateWallpaper();
    });
    stickerRotation.addEventListener('input', () => {
        stickerRotationValue.textContent = `${stickerRotation.value}°`;
        generateWallpaper();
    });
    stickerOpacity.addEventListener('input', () => {
        const opacityPercentage = Math.round((stickerOpacity.value / 255) * 100);
        stickerOpacityValue.textContent = `${opacityPercentage}%`;
        generateWallpaper();
    });
    albumOpacity.addEventListener('input', () => {
        const opacityPercentage = Math.round((albumOpacity.value / 255) * 100);
        albumOpacityValue.textContent = `${opacityPercentage}%`;
        generateWallpaper();
    });
    borderWidth.addEventListener('input', () => {
        borderWidthValue.textContent = `${borderWidth.value}px`;
        generateWallpaper();
    });
    borderColor.addEventListener('input', generateWallpaper);

    // Initial content fetch
    fetchContent();
});
