import ssl
import requests
import io
import yt_dlp
from flask import Flask, render_template, request, send_file

# Bypass SSL agar tidak error di jaringan tertentu
requests.packages.urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

app = Flask(__name__)

def get_tiktok_video(url):
    print(f"[*] Downloader TikTok: {url}")
    api_url = "https://www.tikwm.com/api/"
    try:
        res = requests.post(api_url, data={'url': url, 'hd': 1}, timeout=15).json()
        if res['code'] == 0:
            v_url = res['data']['play']
            if not v_url.startswith('http'): 
                v_url = "https://www.tikwm.com" + v_url
            return requests.get(v_url, verify=False).content, f"tiktok_{res['data']['id']}.mp4"
    except Exception as e:
        print(f"[DEBUG TikTok Error]: {e}")
    return None, None

def get_yt_ig_video(url, platform):
    print(f"[*] Downloader {platform.upper()}: {url}")
    ydl_opts = {
        'format': 'best', # Mengambil format terbaik yang sudah tergabung (audio+video)
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url')
            if video_url:
                video_data = requests.get(video_url, timeout=30, verify=False).content
                ext = info.get('ext', 'mp4')
                return video_data, f"{platform}_{info.get('id', 'video')}.{ext}"
    except Exception as e:
        print(f"[DEBUG {platform.upper()} Error]: {e}")
    return None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    platform = request.form.get('platform')
    
    if not url:
        return "Link tidak boleh kosong", 400

    if platform == 'tiktok':
        video_bytes, filename = get_tiktok_video(url)
    elif platform == 'instagram':
        video_bytes, filename = get_yt_ig_video(url, 'instagram')
    elif platform == 'youtube':
        video_bytes, filename = get_yt_ig_video(url, 'youtube')
    else:
        return "Platform tidak dikenal", 400
    
    if video_bytes:
        return send_file(
            io.BytesIO(video_bytes),
            mimetype='video/mp4',
            as_attachment=True,
            download_name=filename
        )
    
    # Di app.py bagian return error (paling bawah)
    return render_template('index.html', error=True)

if __name__ == '__main__':
    app.run(debug=True)
