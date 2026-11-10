#!/usr/bin/env python
import os
import sys
import subprocess
from urllib.parse import urlparse

# Lokasi penyimpanan utama (Memori Internal / Download)
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

def handle_youtube(url):
    is_music = "music.youtube.com" in url

    if is_music:
        print("\n[+] Terdeteksi: YouTube Music (Audio Only)")
        print("Pilihan Bitrate MP3:")
        print("1. 320 kbps (Suara Paling Jernih)")
        print("2. 256 kbps")
        print("3. 192 kbps")
        print("4. 128 kbps (Hemat Ukuran)")
        
        choice = input("Pilih [1-4] (default 1): ").strip()
        bitrate_map = {"1": "320", "2": "256", "3": "192", "4": "128"}
        bitrate = bitrate_map.get(choice, "320")

        cmd = [
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
        print("\n[+] Terdeteksi: YouTube Video")
        print("Pilihan Download:")
        print("1. Video 1080p (Full HD)")
        print("2. Video 720p (HD)")
        print("3. Video 480p")
        print("4. Video 360p")
        print("5. Ekstrak Audio Saja (MP3 320kbps)")
        
        choice = input("Pilih [1-5] (default 2): ").strip()

        if choice == "5":
            cmd = [
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
            cmd = [
                "yt-dlp",
                "-f", fmt,
                "--merge-output-format", "mp4",
                "-P", DOWNLOAD_DIR,
                "-o", "%(title)s.%(ext)s",
                "--downloader", "aria2c",
                "--downloader-args", "aria2c:-x 16 -s 16 -k 1M",
                url
            ]
    return cmd

def handle_direct_file(url):
    print("\n[+] Terdeteksi: Link Direct Download (Zip, RAR, APK, ISO, Document, dll)")
    custom_name = input("Ubah nama file? (Kosongkan jika ingin pakai nama asli): ").strip()

    cmd = [
        "aria2c",
        "-x", "16",
        "-s", "16",
        "-k", "1M",
        "-d", DOWNLOAD_DIR,
        url
    ]
    if custom_name:
        cmd.extend(["-o", custom_name])
    
    return cmd

def main():
    check_storage()
    print("==================================================")
    print("           SILENTRIX FAST DOWNLOADER              ")
    print("==================================================")
    print(f"[*] Lokasi Simpan: {DOWNLOAD_DIR}\n")
    
    url = input("Tempel Link Di Sini: ").strip()
    if not url:
        print("[!] Link tidak boleh kosong.")
        return

    if is_youtube(url):
        cmd = handle_youtube(url)
    else:
        cmd = handle_direct_file(url)

    print("\n[+] Memulai Download Super Cepat (16 Multi-thread Connections)...\n")
    try:
        subprocess.run(cmd, check=True)
        print(f"\n[✓] BERHASIL! File tersimpan di folder HP: /sdcard/Download")
    except subprocess.CalledProcessError:
        print("\n[!] Download gagal. Periksa kembali link atau koneksi internet.")
    except FileNotFoundError:
        print("\n[!] Program pendukung tidak ditemukan. Pastikan yt-dlp dan aria2 terinstal.")

if __name__ == "__main__":
    main()
