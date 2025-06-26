import streamlit as st
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import io
import datetime
import requests
from urllib.parse import urlparse

# Konfigurasi halaman
st.set_page_config(
    page_title="📸 Photo Booth App with DroidCam",
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
    .droidcam-setup {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
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
    .connection-status {
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
        font-weight: bold;
    }
    .connected {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .disconnected {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session state
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'photo_counter' not in st.session_state:
    st.session_state.photo_counter = 0
if 'droidcam_url' not in st.session_state:
    st.session_state.droidcam_url = ""
if 'droidcam_connected' not in st.session_state:
    st.session_state.droidcam_connected = False

def test_droidcam_connection(url):
    """Test koneksi ke DroidCam"""
    try:
        # Tambahkan http:// jika tidak ada
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        # Test dengan timeout singkat
        response = requests.get(url + '/mjpegfeed', timeout=5, stream=True)
        if response.status_code == 200:
            return True, url
        else:
            return False, f"Status code: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Tidak dapat terhubung ke DroidCam. Pastikan IP dan port benar."
    except requests.exceptions.Timeout:
        return False, "Timeout. Pastikan DroidCam aktif dan terhubung ke jaringan yang sama."
    except Exception as e:
        return False, f"Error: {str(e)}"

def capture_from_droidcam(url):
    """Ambil foto dari DroidCam"""
    try:
        # Ambil satu frame dari MJPEG stream
        response = requests.get(url + '/mjpegfeed', timeout=10, stream=True)
        if response.status_code == 200:
            # Ambil chunk pertama (satu frame)
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    # Cari JPEG header dan footer
                    start = chunk.find(b'\xff\xd8')
                    end = chunk.find(b'\xff\xd9')
                    if start != -1 and end != -1:
                        jpeg_data = chunk[start:end+2]
                        return Image.open(io.BytesIO(jpeg_data))
            return None
        else:
            return None
    except Exception as e:
        st.error(f"Error mengambil foto dari DroidCam: {str(e)}")
        return None

def apply_photo_effects(image, effect="normal"):
    """Menambahkan efek pada foto menggunakan PIL"""
    try:
        if effect == "grayscale":
            return image.convert('L').convert('RGB')
        elif effect == "sepia":
            grayscale = image.convert('L')
            sepia = Image.new('RGB', image.size)
            pixels = []
            for pixel in grayscale.getdata():
                r = min(255, int(pixel * 1.0))
                g = min(255, int(pixel * 0.8))
                b = min(255, int(pixel * 0.6))
                pixels.append((r, g, b))
            sepia.putdata(pixels)
            return sepia
        elif effect == "blur":
            return image.filter(ImageFilter.GaussianBlur(radius=3))
        elif effect == "vintage":
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

def save_photo(image, effect="normal", source="camera"):
    """Menyimpan foto ke session state"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.photo_counter += 1
    photo_data = {
        'image': image,
        'timestamp': timestamp,
        'effect': effect,
        'source': source,
        'id': st.session_state.photo_counter
    }
    st.session_state.photos.append(photo_data)

def create_download_link(image, filename):
    """Membuat link download untuk foto"""
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    return buf.getvalue()

# Header
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 class="main-header">📸 Photo Booth Studio + DroidCam</h1>
    <p style="font-size: 1.2rem; color: #666; font-style: italic;">
        Gunakan smartphone sebagai kamera berkualitas tinggi!
    </p>
</div>
""", unsafe_allow_html=True)

# DroidCam Setup Section
st.markdown("""
<div class="droidcam-setup">
    <h3 style="text-align: center; margin-bottom: 1rem;">📱 Setup DroidCam</h3>
</div>
""", unsafe_allow_html=True)

col_setup1, col_setup2 = st.columns([2, 1])

with col_setup1:
    st.subheader("🔧 Koneksi DroidCam")
    
    # Input URL DroidCam
    droidcam_input = st.text_input(
        "🌐 IP Address DroidCam:", 
        placeholder="Contoh: 192.168.1.100:4747",
        help="Masukkan IP dan port yang ditampilkan di aplikasi DroidCam"
    )
    
    col_test, col_connect = st.columns(2)
    
    with col_test:
        if st.button("🔍 Test Koneksi", use_container_width=True):
            if droidcam_input:
                is_connected, message = test_droidcam_connection(droidcam_input)
                if is_connected:
                    st.session_state.droidcam_url = message
                    st.session_state.droidcam_connected = True
                    st.success("✅ DroidCam terhubung!")
                else:
                    st.session_state.droidcam_connected = False
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Masukkan IP address DroidCam terlebih dahulu!")
    
    with col_connect:
        if st.button("📱 Hubungkan", type="primary", use_container_width=True):
            if droidcam_input:
                is_connected, message = test_droidcam_connection(droidcam_input)
                if is_connected:
                    st.session_state.droidcam_url = message
                    st.session_state.droidcam_connected = True
                    st.success("✅ DroidCam berhasil dihubungkan!")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("⚠️ Masukkan IP address terlebih dahulu!")

with col_setup2:
    # Status koneksi
    if st.session_state.droidcam_connected:
        st.markdown(f"""
        <div class="connection-status connected">
            ✅ TERHUBUNG<br>
            📱 {st.session_state.droidcam_url}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="connection-status disconnected">
            ❌ BELUM TERHUBUNG<br>
            Setup DroidCam terlebih dahulu
        </div>
        """, unsafe_allow_html=True)

# Instruksi Setup
with st.expander("📖 Cara Setup DroidCam", expanded=not st.session_state.droidcam_connected):
    st.markdown("""
    ### 🔧 Langkah-langkah Setup:
    
    1. **📱 Install DroidCam:**
       - Download "DroidCam" dari Play Store/App Store
       - Install juga DroidCam Client di laptop (opsional)
    
    2. **🌐 Koneksi WiFi:**
       - Pastikan smartphone dan laptop terhubung ke WiFi yang sama
       - Buka aplikasi DroidCam di smartphone
    
    3. **📋 Dapatkan IP Address:**
       - Di aplikasi DroidCam, lihat "WiFi IP" (contoh: 192.168.1.100:4747)
       - Salin IP address tersebut
    
    4. **🔗 Hubungkan:**
       - Paste IP address di kotak input di atas
       - Klik "Test Koneksi" atau "Hubungkan"
    
    ### 💡 Tips:
    - ✅ Gunakan port default 4747
    - ✅ Pastikan firewall tidak memblokir koneksi
    - ✅ Restart aplikasi jika tidak bisa connect
    """)

# Main Photo Booth Interface
st.markdown("---")

# Layout dengan 2 kolom
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Studio Foto")
    
    # Tab untuk berbagai sumber foto
    tab1, tab2, tab3 = st.tabs(["📱 DroidCam", "💻 Webcam", "📁 Upload"])
    
    with tab1:
        if st.session_state.droidcam_connected:
            st.success("📱 DroidCam siap digunakan!")
            
            if st.button("📸 Ambil Foto dari DroidCam", type="primary", use_container_width=True):
                with st.spinner("📷 Mengambil foto dari DroidCam..."):
                    droidcam_image = capture_from_droidcam(st.session_state.droidcam_url)
                    if droidcam_image:
                        st.session_state.current_image = droidcam_image
                        st.session_state.image_source = "droidcam"
                        st.success("✅ Foto berhasil diambil dari DroidCam!")
                        st.rerun()
                    else:
                        st.error("❌ Gagal mengambil foto dari DroidCam")
        else:
            st.warning("⚠️ Hubungkan DroidCam terlebih dahulu di bagian setup di atas")
    
    with tab2:
        st.info("💻 Gunakan webcam laptop sebagai alternatif")
        camera_photo = st.camera_input("📸 Ambil foto dengan webcam")
        if camera_photo:
            st.session_state.current_image = Image.open(camera_photo)
            st.session_state.image_source = "webcam"
    
    with tab3:
        st.info("📁 Upload foto dari galeri")
        uploaded_file = st.file_uploader(
            "Upload foto", 
            type=['jpg', 'jpeg', 'png', 'webp'],
            help="Pilih foto dari device Anda"
        )
        if uploaded_file:
            st.session_state.current_image = Image.open(uploaded_file)
            st.session_state.image_source = "upload"
    
    # Pilihan efek
    if 'current_image' in st.session_state:
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
            format_func=lambda x: effect_options[x]
        )
        
        # Preview foto dengan efek
        st.subheader("👀 Preview")
        processed_preview = apply_photo_effects(st.session_state.current_image.copy(), effect)
        st.image(processed_preview, caption=f"Preview dengan efek {effect_options[effect]}", 
                use_column_width=True)
        
        # Tombol simpan
        col_save, col_reset = st.columns(2)
        with col_save:
            if st.button("💾 Simpan Foto", type="primary", use_container_width=True):
                processed_image = apply_photo_effects(st.session_state.current_image.copy(), effect)
                save_photo(processed_image, effect, st.session_state.image_source)
                st.success(f"✅ Foto berhasil disimpan dengan efek {effect_options[effect]}!")
                st.balloons()
                # Clear current image
                if 'current_image' in st.session_state:
                    del st.session_state.current_image
                st.rerun()
        
        with col_reset:
            if st.button("🔄 Reset", use_container_width=True):
                if 'current_image' in st.session_state:
                    del st.session_state.current_image
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
        
        # Tampilkan sumber foto
        source_icons = {
            "droidcam": "📱 DroidCam",
            "webcam": "💻 Webcam", 
            "upload": "📁 Upload"
        }
        st.metric("📸 Sumber", source_icons.get(latest_photo['source'], "Unknown"))
        
        # Tampilkan foto terakhir
        st.subheader("🖼️ Foto Terakhir")
        st.image(latest_photo['image'], caption="Foto terbaru", use_column_width=True)
    
    # Kontrol
    st.markdown("---")
    if st.button("🗑️ Hapus Semua Foto", type="secondary", use_container_width=True):
        st.session_state.photos = []
        st.session_state.photo_counter = 0
        st.success("✅ Semua foto telah dihapus!")
        st.rerun()

# Gallery (sama seperti sebelumnya)
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
                photo = st.session_state.photos[-(i + j + 1)]
                with cols[j]:
                    source_icons = {
                        "droidcam": "📱", "webcam": "💻", "upload": "📁"
                    }
                    source_icon = source_icons.get(photo['source'], "📸")
                    
                    st.image(
                        photo['image'], 
                        caption=f"{source_icon} {photo['timestamp']}\n🎨 {effect_options[photo['effect']]}", 
                        use_column_width=True
                    )
                    
                    download_data = create_download_link(photo['image'], f"photo_{photo['timestamp']}.png")
                    st.download_button(
                        label="💾 Download",
                        data=download_data,
                        file_name=f"photo_{photo['timestamp']}.png",
                        mime="image/png",
                        key=f"download_{photo['id']}",
                        use_container_width=True
                    )

# Sidebar dengan informasi
st.sidebar.title("📱 DroidCam Setup")
st.sidebar.markdown("""
### 🔧 Requirements:
```
streamlit>=1.28.0
pillow>=10.0.0
numpy>=1.24.0
requests>=2.28.0
```

### 📱 DroidCam App:
- **Android**: DroidCam di Play Store
- **iOS**: EpocCam atau DroidCam
- **Free**: Resolusi terbatas
- **Pro**: HD quality

### 🌐 Network Setup:
- Smartphone & laptop di WiFi sama
- Port default: 4747
- Format: IP:PORT (192.168.1.100:4747)

### 💡 Troubleshooting:
- Restart aplikasi DroidCam
- Cek firewall/antivirus
- Pastikan tidak ada app lain yang pakai kamera
- Coba ganti port jika perlu
""")

st.sidebar.success("🚀 Aplikasi siap dengan DroidCam!")
