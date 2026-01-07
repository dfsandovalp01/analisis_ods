from PIL import Image
from pathlib import Path

def optimize_images(input_dir="config/institucional/logos", max_size=(800, 800)):
    """Optimiza imágenes institucionales"""
    
    input_path = Path(input_dir)
    
    for img_file in input_path.glob("*.png"):
        img = Image.open(img_file)
        
        # Redimensionar si es necesario
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Guardar como WebP (mejor compresión)
        output_file = img_file.with_suffix('.webp')
        img.save(output_file, 'WEBP', quality=85, method=6)
        
        print(f"Optimizado: {img_file.name} -> {output_file.name}")
        print(f"  Reducción: {img_file.stat().st_size / 1024:.1f}KB -> {output_file.stat().st_size / 1024:.1f}KB")