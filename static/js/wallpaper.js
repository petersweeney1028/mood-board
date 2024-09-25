document.addEventListener('DOMContentLoaded', () => {
    const loading = document.getElementById('loading');
    const wallpaperCreator = document.getElementById('wallpaper-creator');
    const wallpaperPreview = document.getElementById('wallpaper-preview');
    const templateSelect = document.getElementById('template-select');
    const colorPalette = document.getElementById('color-palette');
    const regenerateBtn = document.getElementById('regenerate-btn');
    const downloadBtn = document.getElementById('download-btn');

    let contentData = null;

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
                hideLoading();
            })
            .catch(error => {
                console.error('Error fetching content:', error);
                hideLoading();
            });
    }

    function updateWallpaperPreview() {
        // In a real implementation, this would create and display the wallpaper preview
        // For now, we'll just show a placeholder
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

    function generateWallpaper() {
        const template = templateSelect.value;
        const data = {
            template: template,
            color_palette: contentData.color_palette,
            instagram: contentData.instagram,
            spotify: contentData.spotify
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
        link.download = 'moodboard_wallpaper.png';
        link.click();
    });

    templateSelect.addEventListener('change', generateWallpaper);

    // Initial content fetch
    fetchContent();
});
