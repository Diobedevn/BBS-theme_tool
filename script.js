// BBS Theme Tool JavaScript

class BBSThemeTool {
    constructor() {
        this.themes = [
            { name: 'Classic Green', bg: '#000000', text: '#00ff00', accent: '#ffff00', border: '#ffffff' },
            { name: 'Amber Terminal', bg: '#1a0f00', text: '#ffb000', accent: '#ff6600', border: '#ffb000' },
            { name: 'Blue Screen', bg: '#000080', text: '#ffffff', accent: '#ffff00', border: '#c0c0c0' },
            { name: 'Matrix', bg: '#000000', text: '#00ff41', accent: '#008f11', border: '#00ff41' },
            { name: 'Retro Pink', bg: '#2d1b69', text: '#ff6ec7', accent: '#00d4aa', border: '#ff6ec7' },
            { name: 'Cyberpunk', bg: '#0f0f23', text: '#ff0080', accent: '#00ffff', border: '#ff0080' },
            { name: 'Hacker Green', bg: '#0d1117', text: '#39ff14', accent: '#ff073a', border: '#39ff14' },
            { name: 'DOS Classic', bg: '#000000', text: '#c0c0c0', accent: '#ffff00', border: '#808080' }
        ];
        
        this.currentTheme = this.themes[0];
        this.init();
    }

    init() {
        this.populateThemeList();
        this.bindEvents();
        this.applyTheme();
    }

    populateThemeList() {
        const themeList = document.getElementById('themeList');
        themeList.innerHTML = '';
        
        this.themes.forEach((theme, index) => {
            const themeItem = document.createElement('div');
            themeItem.className = 'theme-item';
            themeItem.textContent = theme.name;
            themeItem.dataset.index = index;
            
            if (index === 0) {
                themeItem.classList.add('selected');
            }
            
            themeItem.addEventListener('click', () => this.selectTheme(index));
            themeList.appendChild(themeItem);
        });
    }

    bindEvents() {
        // Theme search
        document.getElementById('themeSearch').addEventListener('input', (e) => {
            this.filterThemes(e.target.value);
        });

        // Color inputs
        document.getElementById('bgColor').addEventListener('change', (e) => {
            this.updateColor('bg', e.target.value);
        });
        
        document.getElementById('textColor').addEventListener('change', (e) => {
            this.updateColor('text', e.target.value);
        });
        
        document.getElementById('accentColor').addEventListener('change', (e) => {
            this.updateColor('accent', e.target.value);
        });
        
        document.getElementById('borderColor').addEventListener('change', (e) => {
            this.updateColor('border', e.target.value);
        });

        // Options
        document.getElementById('enableBorder').addEventListener('change', () => {
            this.applyTheme();
        });
        
        document.getElementById('enableShadow').addEventListener('change', () => {
            this.applyTheme();
        });
        
        document.getElementById('pixelFont').addEventListener('change', () => {
            this.applyTheme();
        });

        // Buttons
        document.getElementById('applyTheme').addEventListener('click', () => {
            this.applyTheme();
            this.showNotification('Theme applied successfully!');
        });
        
        document.getElementById('exportTheme').addEventListener('click', () => {
            this.exportTheme();
        });
        
        document.getElementById('resetTheme').addEventListener('click', () => {
            this.resetTheme();
        });
        
        document.getElementById('fullscreenPreview').addEventListener('click', () => {
            this.toggleFullscreen();
        });
    }

    selectTheme(index) {
        // Update selected theme in list
        document.querySelectorAll('.theme-item').forEach(item => {
            item.classList.remove('selected');
        });
        document.querySelector(`[data-index="${index}"]`).classList.add('selected');
        
        // Update current theme
        this.currentTheme = { ...this.themes[index] };
        
        // Update color inputs
        document.getElementById('bgColor').value = this.currentTheme.bg;
        document.getElementById('textColor').value = this.currentTheme.text;
        document.getElementById('accentColor').value = this.currentTheme.accent;
        document.getElementById('borderColor').value = this.currentTheme.border;
        
        this.applyTheme();
    }

    updateColor(type, value) {
        this.currentTheme[type] = value;
        this.applyTheme();
    }

    applyTheme() {
        const preview = document.getElementById('bbsPreview');
        const enableBorder = document.getElementById('enableBorder').checked;
        const enableShadow = document.getElementById('enableShadow').checked;
        const pixelFont = document.getElementById('pixelFont').checked;
        
        // Apply CSS custom properties
        preview.style.setProperty('--bg-color', this.currentTheme.bg);
        preview.style.setProperty('--text-color', this.currentTheme.text);
        preview.style.setProperty('--accent-color', this.currentTheme.accent);
        preview.style.setProperty('--border-color', this.currentTheme.border);
        
        // Apply border
        if (enableBorder) {
            preview.style.setProperty('--border-width', '2px');
        } else {
            preview.style.setProperty('--border-width', '0');
        }
        
        // Apply shadow
        if (enableShadow) {
            preview.style.setProperty('--shadow', `0 0 20px ${this.currentTheme.accent}40`);
        } else {
            preview.style.setProperty('--shadow', 'none');
        }
        
        // Apply font
        if (pixelFont) {
            preview.style.fontFamily = "'Courier New', monospace";
        } else {
            preview.style.fontFamily = "Arial, sans-serif";
        }
    }

    filterThemes(searchTerm) {
        const themeItems = document.querySelectorAll('.theme-item');
        const term = searchTerm.toLowerCase();
        
        themeItems.forEach(item => {
            const themeName = item.textContent.toLowerCase();
            if (themeName.includes(term)) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    exportTheme() {
        const themeData = {
            name: 'Custom Theme',
            ...this.currentTheme,
            options: {
                enableBorder: document.getElementById('enableBorder').checked,
                enableShadow: document.getElementById('enableShadow').checked,
                pixelFont: document.getElementById('pixelFont').checked
            }
        };
        
        const dataStr = JSON.stringify(themeData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        
        const link = document.createElement('a');
        link.href = URL.createObjectURL(dataBlob);
        link.download = 'bbs-theme.json';
        link.click();
        
        this.showNotification('Theme exported successfully!');
    }

    resetTheme() {
        this.selectTheme(0);
        document.getElementById('enableBorder').checked = false;
        document.getElementById('enableShadow').checked = false;
        document.getElementById('pixelFont').checked = true;
        this.applyTheme();
        this.showNotification('Theme reset to default!');
    }

    toggleFullscreen() {
        const previewContainer = document.getElementById('previewContainer');
        
        if (!document.fullscreenElement) {
            previewContainer.requestFullscreen().catch(err => {
                console.log('Error attempting to enable fullscreen:', err);
            });
        } else {
            document.exitFullscreen();
        }
    }

    showNotification(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #00ff00;
            color: #000;
            padding: 15px 20px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            z-index: 1000;
            box-shadow: 0 4px 15px rgba(0, 255, 0, 0.3);
            transform: translateX(100%);
            transition: transform 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 100);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BBSThemeTool();
});