import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io
import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="📸 Photo Booth App",
    page_icon="📸",
    layout="wide"
)

# CSS untuk styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        font-size: 3rem;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .photo-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
    }
    .controls-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0;
    }
    .gallery-container {
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .stats-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .effect-preview {
        border: 3px solid #fff;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session state
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'photo_counter' not in st.session_state:
    st.session_state.photo_counter = 0

def apply_photo_effects(image, effect="normal"):
    """Menambahkan efek pada foto menggunakan PIL"""
    try:
        if effect == "grayscale":
            return image.convert('L').convert('RGB')
        elif effect == "sepia":
            # Konversi ke grayscale dulu
            grayscale = image.convert('L')
            # Buat sepia dengan menambahkan warna coklat
            sepia = Image.new('RGB', image.size)
            pixels = []
            for pixel in grayscale.getdata():
                # Rumus sepia
                r = min(255, int(pixel * 1.0))
                g = min(255, int(pixel * 0.8))
                b = min(255, int(pixel * 0.6))
                pixels.append((r, g, b))
            sepia.putdata(pixels)
            return sepia
        elif effect == "blur":
            return image.filter(ImageFilter.GaussianBlur(radius=3))
        elif effect == "vintage":
            # Efek vintage dengan mengurangi kontras dan menambah warmth
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(0.8)
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.2)
            return image
        elif effect == "bright":
            enhancer = ImageEnhance.Brightness(image)
            return enhancer.enhance(1.3)
        elif effect == "dramatic":
            enhancer = ImageEnhance.Contrast(image)
            return enhancer.enhance(1.5)
        else:
            return image
    except Exception as e:
        st.error(f"Error applying effect: {str(e)}")
        return image

def save_photo(image, effect="normal"):
    """Menyimpan foto ke session state"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.photo_counter += 1
    photo_data = {
        'image': image,
        'timestamp': timestamp,
        'effect': effect,
        'id': st.session_state.photo_counter
    }
    st.session_state.photos.append(photo_data)

def create_download_link(image, filename):
    """Membuat link download untuk foto"""
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    return buf.getvalue()

# Header dengan animasi
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 class="main-header">📸 Photo Booth Studio</h1>
    <p style="font-size: 1.2rem; color: #666; font-style: italic;">
        Ambil foto cantik dengan berbagai efek menarik!
    </p>
</div>
""", unsafe_allow_html=True)

# Layout dengan 2 kolom
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 15px; margin-bottom: 2rem;">
        <h3 style="color: white; text-align: center; margin-bottom: 1rem;">
            📷 Studio Foto
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Widget untuk mengambil foto dari kamera
    camera_photo = st.camera_input("📸 Ambil foto dengan kamera")
    
    # Upload foto alternatif
    uploaded_file = st.file_uploader(
        "📁 Atau upload foto dari galeri", 
        type=['jpg', 'jpeg', 'png', 'webp'],
        help="Pilih foto dari device Anda"
    )
    
    # Pilihan efek dengan preview
    st.subheader("🎨 Pilih Efek Foto")
    effect_options = {
        "normal": "🌟 Normal",
        "grayscale": "⚫ Hitam Putih", 
        "sepia": "🟤 Sepia Klasik",
        "blur": "🌫️ Blur Artistik",
        "vintage": "📸 Vintage",
        "bright": "☀️ Cerah",
        "dramatic": "🎭 Dramatis"
    }
    
    effect = st.selectbox(
        "Efek:",
        options=list(effect_options.keys()),
        format_func=lambda x: effect_options[x],
        help="Pilih efek yang ingin diterapkan pada foto"
    )
    
    # Preview foto dengan efek
    preview_image = None
    if camera_photo is not None:
        preview_image = Image.open(camera_photo)
    elif uploaded_file is not None:
        preview_image = Image.open(uploaded_file)
    
    if preview_image is not None:
        st.subheader("👀 Preview dengan Efek")
        processed_preview = apply_photo_effects(preview_image.copy(), effect)
        st.image(processed_preview, caption=f"Preview dengan efek {effect_options[effect]}", 
                use_column_width=True, clamp=True)
    
    # Tombol untuk memproses foto
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn1:
        if st.button("📸 Simpan Foto", type="primary", use_container_width=True):
            if preview_image is not None:
                # Terapkan efek
                processed_image = apply_photo_effects(preview_image.copy(), effect)
                
                # Simpan foto
                save_photo(processed_image, effect)
                
                st.success(f"✅ Foto berhasil disimpan dengan efek {effect_options[effect]}!")
                st.balloons()
                st.rerun()
            else:
                st.error("❌ Silakan ambil foto atau upload file terlebih dahulu!")
    
    with col_btn2:
        if st.button("🔄 Reset", type="secondary", use_container_width=True):
            st.rerun()

with col2:
    st.markdown("""
    <div class="stats-card">
        <h3>📊 Statistik Studio</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistik
    total_photos = len(st.session_state.photos)
    st.metric("📷 Total Foto", total_photos)
    
    if st.session_state.photos:
        latest_photo = st.session_state.photos[-1]
        st.metric("⏰ Foto Terakhir", latest_photo['timestamp'])
        st.metric("🎨 Efek Terakhir", effect_options[latest_photo['effect']])
        
        # Tampilkan foto terakhir
        st.subheader("🖼️ Foto Terakhir")
        st.image(latest_photo['image'], caption="Foto terbaru Anda", use_column_width=True)
    
    # Kontrol galeri
    st.markdown("---")
    col_clear, col_download = st.columns(2)
    
    with col_clear:
        if st.button("🗑️ Hapus Semua", type="secondary", use_container_width=True):
            st.session_state.photos = []
            st.session_state.photo_counter = 0
            st.success("✅ Semua foto telah dihapus!")
            st.rerun()
    
    with col_download:
        if st.session_state.photos:
            if st.button("📦 Download Semua", use_container_width=True):
                st.info("💡 Klik tombol download pada setiap foto di galeri!")

# Gallery
if st.session_state.photos:
    st.markdown("""
    <div class="gallery-container">
        <h2 style="color: white; text-align: center; margin-bottom: 2rem;">
            🖼️ Galeri Foto Studio
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Tampilkan foto dalam grid
    photos_per_row = 3
    for i in range(0, len(st.session_state.photos), photos_per_row):
        cols = st.columns(photos_per_row)
        for j in range(photos_per_row):
            if i + j < len(st.session_state.photos):
                photo = st.session_state.photos[-(i + j + 1)]  # Terbaru dulu
                with cols[j]:
                    st.image(
                        photo['image'], 
                        caption=f"📅 {photo['timestamp']}\n🎨 {effect_options[photo['effect']]}", 
                        use_column_width=True
                    )
                    
                    # Tombol download
                    download_data = create_download_link(photo['image'], f"photo_{photo['timestamp']}.png")
                    st.download_button(
                        label="💾 Download",
                        data=download_data,
                        file_name=f"photo_{photo['timestamp']}.png",
                        mime="image/png",
                        key=f"download_{photo['id']}",
                        use_container_width=True
                    )

# Footer dengan informasi
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
            padding: 2rem; border-radius: 15px; color: white; margin-top: 2rem;">
    <h3 style="text-align: center;">📝 Panduan Penggunaan</h3>
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
        <div>
            <h4>🚀 Langkah-langkah:</h4>
            <ul>
                <li>📸 Ambil foto dengan kamera atau upload file</li>
                <li>🎨 Pilih efek yang diinginkan</li>
                <li>👀 Lihat preview hasil</li>
                <li>💾 Klik "Simpan Foto"</li>
                <li>🖼️ Lihat di galeri dan download</li>
            </ul>
        </div>
        <div>
            <h4>✨ Fitur Tersedia:</h4>
            <ul>
                <li>🌟 7 efek foto berbeda</li>
                <li>📊 Statistik real-time</li>
                <li>🖼️ Galeri dengan preview</li>
                <li>💾 Download individual</li>
                <li>🗑️ Manajemen foto</li>
            </ul>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar untuk informasi deployment
st.sidebar.title("🚀 Info Deployment")
st.sidebar.markdown("""
### 📋 Requirements.txt:
```
streamlit>=1.28.0
pillow>=10.0.0
numpy>=1.24.0
```

### 🔧 Cara Deploy:
1. **GitHub**: Upload code + requirements.txt
2. **Streamlit Cloud**: Connect repository  
3. **Deploy**: Pilih file Python
4. **Done**: Aplikasi siap digunakan!

### 💡 Tips:
- ✅ Tidak perlu OpenCV (sudah dihapus)
- ✅ Menggunakan PIL untuk efek foto
- ✅ Kompatibel dengan Streamlit Cloud
- ✅ Responsive dan user-friendly
""")

st.sidebar.success("🎉 Aplikasi siap deploy!")
st.sidebar.info("💡 Berikan akses kamera untuk fitur foto langsung!")
