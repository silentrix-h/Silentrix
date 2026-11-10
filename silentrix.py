#!/usr/bin/env python
import os
import sys
import subprocess
from urllib.parse import urlparse

DOWNLOAD_DIR = "/sdcard/Download"

def check_storage():
    """Memastikan direktori /sdcard/Download tersedia."""
    if not os.path.exists(DOWNLOAD_DIR):
        try:
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        except Exception:
            print("[!] Folder /sdcard/Download tidak terjangkau. Jalankan 'termux-setup-storage' dulu.")
            sys.exit(1)

def is_youtube(url):
    """Mendeteksi apakah link berasal dari YouTube atau YT Music."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    return any(yt in domain for yt in ["youtube.com", "youtu.be", "music.youtube.com"])

def handle_youtube(url, default_quality=False):
    is_music = "music.youtube.com" in url

    if is_music:
        if default_quality:
            bitrate = "320"
        else:
            print(f"\n[+] Terdeteksi YT Music: {url}")
            print("Pilihan Bitrate MP3:")
            print("1. 320 kbps (Suara Paling Jernih)")
            print("2. 256 kbps")
            print("3. 192 kbps")
            print("4. 128 kbps (Hemat Ukuran)")
            choice = input("Pilih [1-4] (default 1): ").strip()
            bitrate_map = {"1": "320", "2": "256", "3": "192", "4": "128"}
            bitrate = bitrate_map.get(choice, "320")

        return [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", f"{bitrate}k",
            "-P", DOWNLOAD_DIR,
            "-o", "%(title)s.%(ext)s",
            "--downloader", "aria2c",
            "--downloader-args", "aria2c:-x 16 -s 16 -k 1M",
            url
        ]
    else:
        if default_quality:
            choice = "2" # Default 720p untuk batch download
        else:
            print(f"\n[+] Terdeteksi YouTube Video: {url}")
            print("Pilihan Download:")
            print("1. Video 1080p (Full HD)")
            print("2. Video 720p (HD)")
            print("3. Video 480p")
            print("4. Video 360p")
            print("5. Ekstrak Audio Saja (MP3 320kbps)")
            choice = input("Pilih [1-5] (default 2): ").strip()

        if choice == "5":
            return [
                "yt-dlp",
                "-x",
                "--audio-format", "mp3",
                "--audio-quality", "320k",
                "-P", DOWNLOAD_DIR,
                "-o", "%(title)s.%(ext)s",
                "--downloader", "aria2c",
                "--downloader-args", "aria2c:-x 16 -s 16 -k 1M",
                url
            ]
        else:
            res_map = {"1": "1080", "2": "720", "3": "480", "4": "360"}
            res = res_map.get(choice, "720")
            fmt = f"bestvideo[height<={res}]+bestaudio/best[height<={res}]"
            return [
                "yt-dlp",
                "-f", fmt,
                "--merge-output-format", "mp4",
                "-P", DOWNLOAD_DIR,
                "-o", "%(title)s.%(ext)s",
                "--downloader", "aria2c",
                "--downloader-args", "aria2c:-x 16 -s 16 -k 1M",
                url
            ]

def handle_direct_file(url):
    return [
        "aria2c",
        "-x", "16",
        "-s", "16",
        "-k", "1M",
        "-d", DOWNLOAD_DIR,
        url
    ]

def process_download(url, default_quality=False):
    if is_youtube(url):
        cmd = handle_youtube(url, default_quality)
    else:
        cmd = handle_direct_file(url)

    print(f"\n[+] Memproses: {url}")
    try:
        subprocess.run(cmd, check=True)
        print(f"[✓] Berhasil didownload ke /sdcard/Download\n")
    except subprocess.CalledProcessError:
        print(f"[!] Gagal mengunduh: {url}\n")

def main():
    check_storage()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print("==================================================")
        print("           SILENTRIX FAST DOWNLOADER              ")
        print("==================================================")
        print(f"[*] Lokasi Simpan: {DOWNLOAD_DIR}\n")
        print("PILIH MODE:")
        print("1. Download Single Link (Pengulangan Otomatis)")
        print("2. Download Batch Multi-Link (Tempel banyak link)")
        print("0. Keluar")
        
        mode = input("\nPilihan Mode [1/2/0]: ").strip()

        if mode == "0" or mode.lower() in ["exit", "q"]:
            print("\nTerima kasih telah menggunakan Silentrix!")
            break

        elif mode == "2":
            print("\n--- MODE BATCH MULTI-LINK ---")
            print("Tempel link satu per satu (Enter setiap link).")
            print("Tekan ENTER sekali lagi (baris kosong) jika selesai untuk mulai download.")
            print("--------------------------------------------------")
            
            links = []
            while True:
                link = input(f"Link #{len(links)+1}: ").strip()
                if not link:
                    break
                links.append(link)

            if not links:
                print("[!] Tidak ada link yang dimasukkan.")
                input("\nTekan Enter untuk kembali ke menu...")
                continue

            print(f"\n[+] Memulai download {len(links)} file secara otomatis...\n")
            for idx, item in enumerate(links, 1):
                print(f"--- Processing [{idx}/{len(links)}] ---")
                process_download(item, default_quality=True)
            
            input("Semua antrean batch selesai! Tekan Enter untuk kembali ke menu...")

        else: # Default ke Mode 1 (Single Link Loop)
            while True:
                print("\n--------------------------------------------------")
                url = input("Tempel Link (atau ketik 'q' untuk ke Menu Utama): ").strip()
                
                if url.lower() in ["q", "exit", "menu"]:
                    break
                if not url:
                    continue

                process_download(url, default_quality=False)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Program dihentikan oleh pengguna.")
        sys.exit(0)
