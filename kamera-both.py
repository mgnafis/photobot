import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import datetime
import base64

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
    }
    .photo-container {
        display: flex;
        justify-content: center;
        margin: 2rem 0;
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
        background-color: #f8f9fa;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Inisialisasi session state
if 'photos' not in st.session_state:
    st.session_state.photos = []
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

def capture_photo_from_camera():
    """Fungsi untuk mengambil foto dari kamera"""
    try:
        # Inisialisasi kamera
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return None, "Tidak dapat mengakses kamera. Pastikan kamera tersedia."
        
        # Ambil frame
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            # Konversi BGR ke RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb, None
        else:
            return None, "Gagal mengambil foto dari kamera."
    except Exception as e:
        return None, f"Error: {str(e)}"

def add_photo_effects(image, effect="normal"):
    """Menambahkan efek pada foto"""
    if effect == "grayscale":
        return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    elif effect == "sepia":
        sepia_filter = np.array([[0.393, 0.769, 0.189],
                               [0.349, 0.686, 0.168],
                               [0.272, 0.534, 0.131]])
        return cv2.transform(image, sepia_filter)
    elif effect == "blur":
        return cv2.GaussianBlur(image, (15, 15), 0)
    else:
        return image

def save_photo(image, effect="normal"):
    """Menyimpan foto ke session state"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    photo_data = {
        'image': image,
        'timestamp': timestamp,
        'effect': effect
    }
    st.session_state.photos.append(photo_data)

# Header
st.markdown('<h1 class="main-header">📸 Photo Booth App</h1>', unsafe_allow_html=True)

# Layout dengan 2 kolom
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📷 Kamera")
    
    # Widget untuk mengambil foto dari kamera (Streamlit camera input)
    camera_photo = st.camera_input("Ambil foto dengan kamera")
    
    # Upload foto alternatif
    uploaded_file = st.file_uploader("Atau upload foto", type=['jpg', 'jpeg', 'png'])
    
    # Pilihan efek
    effect = st.selectbox(
        "Pilih efek foto:",
        ["normal", "grayscale", "sepia", "blur"]
    )
    
    # Tombol untuk memproses foto
    if st.button("📸 Ambil & Simpan Foto", type="primary"):
        image_to_process = None
        
        # Prioritas: kamera input, lalu uploaded file
        if camera_photo is not None:
            image_to_process = Image.open(camera_photo)
        elif uploaded_file is not None:
            image_to_process = Image.open(uploaded_file)
        
        if image_to_process is not None:
            # Konversi PIL ke numpy array
            img_array = np.array(image_to_process)
            
            # Terapkan efek
            processed_image = add_photo_effects(img_array, effect)
            
            # Simpan foto
            save_photo(processed_image, effect)
            
            st.success(f"✅ Foto berhasil disimpan dengan efek {effect}!")
            st.rerun()
        else:
            st.error("❌ Silakan ambil foto atau upload file terlebih dahulu!")

with col2:
    st.subheader("📊 Statistik")
    st.metric("Total Foto", len(st.session_state.photos))
    
    if st.session_state.photos:
        latest_photo = st.session_state.photos[-1]
        st.metric("Foto Terakhir", latest_photo['timestamp'])
        st.metric("Efek Terakhir", latest_photo['effect'].title())
    
    # Tombol untuk menghapus semua foto
    if st.button("🗑️ Hapus Semua Foto", type="secondary"):
        st.session_state.photos = []
        st.success("✅ Semua foto telah dihapus!")
        st.rerun()

# Gallery
if st.session_state.photos:
    st.markdown('<div class="gallery-container">', unsafe_allow_html=True)
    st.subheader("🖼️ Galeri Foto")
    
    # Tampilkan foto dalam grid
    cols = st.columns(3)
    for i, photo in enumerate(reversed(st.session_state.photos)):
        with cols[i % 3]:
            # Tampilkan foto
            if len(photo['image'].shape) == 2:  # Grayscale
                st.image(photo['image'], caption=f"{photo['timestamp']} - {photo['effect']}", 
                        use_column_width=True, clamp=True)
            else:
                st.image(photo['image'], caption=f"{photo['timestamp']} - {photo['effect']}", 
                        use_column_width=True)
            
            # Tombol download
            if len(photo['image'].shape) == 2:
                img_pil = Image.fromarray(photo['image'], mode='L')
            else:
                img_pil = Image.fromarray(photo['image'])
            
            buf = io.BytesIO()
            img_pil.save(buf, format='PNG')
            
            st.download_button(
                label="💾 Download",
                data=buf.getvalue(),
                file_name=f"photo_{photo['timestamp']}.png",
                mime="image/png",
                key=f"download_{i}"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
### 📝 Cara Penggunaan:
1. **Ambil Foto**: Gunakan kamera atau upload file foto
2. **Pilih Efek**: Normal, Grayscale, Sepia, atau Blur
3. **Simpan**: Klik tombol "Ambil & Simpan Foto"
4. **Lihat Galeri**: Scroll ke bawah untuk melihat semua foto
5. **Download**: Klik tombol download untuk menyimpan foto

### 🚀 Fitur:
- ✅ Ambil foto langsung dari kamera
- ✅ Upload foto dari file
- ✅ 4 efek foto berbeda
- ✅ Galeri foto dengan timestamp
- ✅ Download foto hasil
- ✅ Statistik foto
""")

# Informasi deployment
st.sidebar.title("📋 Info Deployment")
st.sidebar.markdown("""
**Requirements untuk deployment:**
```
streamlit
opencv-python-headless
pillow
numpy
```

**Cara deploy ke Streamlit Cloud:**
1. Upload code ke GitHub
2. Buka streamlit.io
3. Connect repository
4. Deploy!

**File requirements.txt:**
```
streamlit>=1.28.0
opencv-python-headless>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
```
""")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tips**: Pastikan browser memberikan akses kamera untuk fitur foto langsung!")