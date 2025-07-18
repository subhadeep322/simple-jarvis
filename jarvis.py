import pyttsx3
import datetime
import webbrowser
import pywhatkit
import os
import sys
import random
import re
import numpy as np
import cv2
import google.generativeai as genai
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip, ImageSequenceClip
from moviepy.editor import (
    VideoFileClip, CompositeVideoClip, TextClip, AudioFileClip,
    ImageClip, concatenate_videoclips, ImageSequenceClip
)
from moviepy.video.fx import all as vfx
from moviepy.video.fx import all as afx
from moviepy.editor import *
# from moviepy.audio.fx.all import audio_speedx  # Removed: not needed, already imported as afx

# Ensure required libraries are installed

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Text-to-speech
engine = pyttsx3.init()
engine.setProperty("rate", 180)

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

def ask_ai(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text or "I'm not sure how to respond to that."
    except Exception as e:
        return "Gemini error: " + str(e)

# ========== Video Editing Functions ==========

def trim_video():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        start = float(input("Start time (seconds): "))
        end = float(input("End time (seconds): "))
        out = input("Output filename (e.g., trimmed.mp4): ")
        clip = VideoFileClip(path).subclip(start, end)
        clip.write_videofile(out)
        speak("Video trimmed successfully.")
    except Exception as e:
        speak(f"Error: {e}")

def add_fade():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        dur = float(input("Fade duration (seconds): "))
        out = input("Output filename: ")
        clip = VideoFileClip(path)
        faded = clip.fx(vfx.fadein, dur).fx(vfx.fadeout, dur)
        faded.write_videofile(out)
        speak("Fade added successfully.")
    except Exception as e:
        speak(f"Error: {e}")

def apply_filter():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        effect = input("Filter (grayscale/invert/mirror): ").strip()
        out = input("Output filename: ")
        clip = VideoFileClip(path)
        if effect == "grayscale":
            clip = clip.fx(vfx.blackwhite)
        elif effect == "invert":
            clip = clip.fx(vfx.invert_colors)
        elif effect == "mirror":
            clip = clip.fx(vfx.mirror_x)
        clip.write_videofile(out)
        speak(f"{effect} filter applied.")
    except Exception as e:
        speak(f"Error: {e}")

def overlay_text():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        text = input("Enter text: ")
        out = input("Output filename: ")
        clip = VideoFileClip(path)
        txt = TextClip(text, fontsize=40, color='white', bg_color='black').set_duration(clip.duration).set_pos('bottom')
        final = CompositeVideoClip([clip, txt])
        final.write_videofile(out)
        speak("Text overlay complete.")
    except Exception as e:
        speak(f"Error: {e}")

def add_logo():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        logo_path = input("Enter logo image path: ")
        out = input("Output filename: ")
        clip = VideoFileClip(path)
        logo = ImageClip(logo_path).resize(height=60).set_duration(clip.duration).set_pos(("right", "top"))
        final = CompositeVideoClip([clip, logo])
        final.write_videofile(out)
        speak("Logo added.")
    except Exception as e:
        speak(f"Error: {e}")

def add_audio():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        audio_path = input("Enter audio file path: ")
        out = input("Output filename: ")
        video = VideoFileClip(path)
        audio = AudioFileClip(audio_path).set_duration(video.duration)
        video.set_audio(audio).write_videofile(out)
        speak("Audio added.")
    except Exception as e:
        speak(f"Error: {e}")

def glitch_effect():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., full_glitch.mp4): ").strip().strip('"').strip("'")

        # Load and speed up video
        clip = VideoFileClip(path).fx(vfx.speedx, factor=1.5)
        fps = clip.fps

        frames = []
        for i, frame in enumerate(clip.iter_frames(fps=fps)):
            frame = frame.astype(np.int16)

            # Dark overlay + flickering
            darkness = np.random.randint(-80, -30)
            frame += darkness

            # RGB flickering
            if i % 3 == 0:
                frame[:, :, 0] += np.random.randint(20, 60)  # R
            elif i % 3 == 1:
                frame[:, :, 2] += np.random.randint(20, 60)  # B
            else:
                frame[:, :, 1] += np.random.randint(20, 60)  # G

            # Noise
            noise = np.random.randint(-25, 25, frame.shape, dtype=np.int16)
            frame += noise

            # Bar glitch effect
            if i % 5 == 0:
                h = frame.shape[0]
                bar_y = np.random.randint(0, h - 10)
                frame[bar_y:bar_y+5, :, :] = np.random.randint(0, 255)

            # Slight shift/glitch
            if i % 10 == 0:
                frame = np.roll(frame, shift=np.random.randint(-15, 15), axis=1)

            # Clip and restore
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            frames.append(frame)

        # Create glitched video and add sped-up audio
        glitched_clip = ImageSequenceClip(frames, fps=fps).set_audio(clip.audio)

        glitched_clip.write_videofile(out, codec="libx264")
        speak("⚡ Full glitch effect applied with 1.5x speed and dark RGB flickers.")
    except Exception as e:
        speak(f"❌ Glitch effect failed: {e}")



def rgb_split():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., rgbsplit_fast.mp4): ").strip().strip('"').strip("'")
        if not out.endswith(".mp4"):
            out += ".mp4"

        clip = VideoFileClip(path)

        # Speed up video and audio
        clip = clip.fx(vfx.speedx, 1.2)

        frames = []
        for frame in clip.iter_frames(fps=clip.fps):
            # Split channels
            b, g, r = cv2.split(frame)

            # Shift channels to create RGB split effect
            r_shifted = np.roll(r, 5, axis=1)
            g_shifted = np.roll(g, -5, axis=0)
            b_shifted = np.roll(b, 3, axis=1)

            # Merge back
            glitched_frame = cv2.merge([b_shifted, g_shifted, r_shifted])
            frames.append(glitched_frame)

        final_clip = ImageSequenceClip(frames, fps=clip.fps).set_audio(clip.audio)
        final_clip.write_videofile(out, codec="libx264")
        speak("✅ RGB Split + Speed effect applied successfully.")
    except Exception as e:
        speak(f"❌ Failed to apply RGB split effect: {e}")

def crossfade():
    try:
        path1 = input("Enter first video path: ")
        path2 = input("Enter second video path: ")
        out = input("Output filename: ")
        duration = float(input("Crossfade duration (seconds): "))
        clip1 = VideoFileClip(path1).crossfadeout(duration)
        clip2 = VideoFileClip(path2).crossfadein(duration)
        final = concatenate_videoclips([clip1, clip2])
        final.write_videofile(out)
        speak("Crossfade complete.")
    except Exception as e:
        speak(f"Error: {e}")

def effect():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., intense_effect.mp4): ").strip().strip('"').strip("'")

        clip = VideoFileClip(path)
        fps = clip.fps
        duration = clip.duration

        # Speed up the clip
        clip = clip.fx(vfx.speedx, factor=1.5)

        frames = []
        for i, frame in enumerate(clip.iter_frames(fps=fps)):
            frame = frame.astype(np.int16)

            # Color flicker: mix red, blue, purple tones
            if i % 3 == 0:
                frame[:, :, 0] += 50  # R
            elif i % 3 == 1:
                frame[:, :, 2] += 50  # B
            else:
                frame[:, :, 0] += 40  # R
                frame[:, :, 2] += 40  # B

            # Add intense noise jitter
            noise = np.random.randint(-30, 30, frame.shape, dtype=np.int16)
            frame += noise

            # Random flips/shifts for chaotic transition
            if i % 10 == 0:
                frame = np.fliplr(frame)
            if i % 15 == 0:
                frame = np.roll(frame, shift=np.random.randint(-20, 20), axis=1)

            # Clip and convert back
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            frames.append(frame)

        intense_clip = ImageSequenceClip(frames, fps=fps).set_audio(clip.audio)

        intense_clip.write_videofile(out, codec='libx264')
        speak("🎬 Intense RGB effect applied with audio speed-up and transitions.")
    except Exception as e:
        speak(f"❌ Error during intense effect processing: {e}")

def intense_glitch_effect():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., intense_glitch.mp4): ").strip().strip('"').strip("'")

        clip = VideoFileClip(path)
        fps = clip.fps
        speed = 1.3
        clip = clip.fx(vfx.speedx, speed)

        if clip.audio:
            audio = clip.audio.set_fps(44100).set_duration(clip.duration)
        else:
            audio = None

        frames = []
        for i, frame in enumerate(clip.iter_frames(fps=fps)):
            frame = frame.astype(np.int16)

            # Vaporwave dark overlay (neon red + blue)
            dark = np.random.randint(-90, -50, frame.shape, dtype=np.int16)
            overlay = np.zeros_like(frame)
            if i % 2 == 0:
                overlay[:, :, 0] = np.random.randint(30, 70)  # Red
            else:
                overlay[:, :, 2] = np.random.randint(30, 70)  # Blue
            frame += dark + overlay

            # Dark outlines (edge detection)
            gray = cv2.cvtColor(np.clip(frame, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            edge_mask = np.stack([edges]*3, axis=-1)
            frame = np.maximum(frame - edge_mask, 0)

            # Random pixel block glitch
            if i % 5 == 0:
                for _ in range(6):
                    x, y = np.random.randint(0, frame.shape[1]-8), np.random.randint(0, frame.shape[0]-8)
                    block = np.random.randint(80, 255, (8, 8, 3))
                    frame[y:y+8, x:x+8] = block

            # Fast horizontal shift
            if i % 7 == 0:
                frame = np.roll(frame, np.random.randint(-20, 20), axis=1)

            frames.append(np.clip(frame, 0, 255).astype(np.uint8))

        result = ImageSequenceClip(frames, fps=fps)
        if audio:
            result = result.set_audio(audio)
        result.write_videofile(out, codec="libx264", audio_codec="aac")

        speak("✅ Intense glitch effect applied with vaporwave, dark outlines, and audio.")
    except Exception as e:
        speak(f"❌ Failed to apply intense glitch effect: {e}")



def apply_dark_pixel_glitch():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., dark_pixel_glitch.mp4): ").strip().strip('"').strip("'")

        # Load and speed up
        clip = VideoFileClip(path)
        speed = 1.3
        clip = clip.fx(vfx.speedx, speed)
        if clip.audio:
            clip = clip.set_audio(clip.audio.set_duration(clip.duration / speed).fx(afx.audio_normalize))

        fps = clip.fps
        frames = []

        for i, frame in enumerate(clip.iter_frames(fps=fps)):
            frame = frame.astype(np.int16)

            # DARK overlay
            darken = np.random.randint(-100, -50)
            frame += darken

            # Pixel block glitch
            if i % 5 == 0:
                h, w, _ = frame.shape
                for _ in range(10):
                    x = np.random.randint(0, w-20)
                    y = np.random.randint(0, h-20)
                    block = np.random.randint(0, 100, (20, 20, 3))
                    frame[y:y+20, x:x+20] = block

            # Black flicker overlay
            if i % 15 == 0:
                frame[:, :, :] = np.maximum(frame[:, :, :] - 80, 0)

            # RGB jitter
            if i % 3 == 0:
                for c in range(3):
                    frame[:, :, c] = np.roll(frame[:, :, c], np.random.randint(-10, 10), axis=np.random.choice([0, 1]))

            # Final touch
            frame = np.clip(frame, 0, 255).astype(np.uint8)
            frames.append(frame)

        final = ImageSequenceClip(frames, fps=fps)
        final = final.set_audio(clip.audio)

        final.write_videofile(out, codec="libx264", audio_codec="aac")
        speak("✅ Dark pixel glitch filter applied with sound and speed-up.")
    except Exception as e:
        speak(f"❌ Failed to apply dark pixel glitch: {e}")
        
def remove_audio():
    try:
        path = input("Enter video path: ").strip().strip('"').strip("'")
        out = input("Output filename (e.g., no_audio.mp4): ").strip().strip('"').strip("'")
        clip = VideoFileClip(path).without_audio()
        clip.write_videofile(out, codec="libx264")
        speak("✅ Audio removed successfully.")
    except Exception as e:
        speak(f"❌ Failed to remove audio: {e}")


# ========== Core Assistant ==========

def play_on_youtube(query):
    speak(f"Playing {query} on YouTube.")
    pywhatkit.playonyt(query)

def wish():
    hour = datetime.datetime.now().hour
    if hour < 12:
        greet = "Good morning!"
    elif hour < 18:
        greet = "Good afternoon!"
    else:
        greet = "Good evening!"
    speak(f"{greet} I am Jarvis. How can I assist you?")

def run_jarvis():
    wish()
    while True:
        command = input("You: ").strip().lower()

        if command == "":
            speak("Please type something.")
            continue

        elif "play" in command:
            song = command.replace("play", "").strip()
            play_on_youtube(song)

        elif "time" in command:
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}.")

        elif "open youtube" in command:
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube.")

        elif "open google" in command:
            webbrowser.open("https://www.google.com")
            speak("Opening Google.")
        elif "open github" in command:
            webbrowser.open("https://www.github.com")
            speak("Opening Google.")
        elif "open coderbong youtube" in command:
            webbrowser.open("https://youtube.com/@coderbong?si=qfqaFifjDCIR8vaT")
            speak("Opening Google.")

        elif "search" in command:
            query = command.replace("search", "").strip()
            speak(f"Searching for {query}")
            pywhatkit.search(query)

        elif "shutdown" in command:
            speak("Shutting down your system.")
            os.system("shutdown /s /t 1")

        elif "restart" in command:
            speak("Restarting your system.")
            os.system("shutdown /r /t 1")

        elif "trim video" in command:
            trim_video()
        elif "add fade" in command:
            add_fade()
        elif "apply filter" in command:
            apply_filter()
        elif "overlay text" in command:
            overlay_text()
        elif "add logo" in command:
            add_logo()
        elif "add audio" in command:
            add_audio()
        elif "glitch effect" in command:
            glitch_effect()
        elif "rgb split" in command:
            rgb_split()
        elif "crossfade" in command:
            crossfade()
        elif "intense filter" in command or "dark theme" in command:
            intense_glitch_effect()

        elif "effect" in command:
             effect()
        elif"dark glitch" in command:
            apply_dark_pixel_glitch()
        elif "remove audio" in command:
            remove_audio()
 

        elif "help" in command:
            speak("I can help you with video editing, play music, search the web, and more. Just ask!")

        elif "joke" in command:
            try:
                response = model.generate_content("Tell me a short and funny joke")
                joke = response.text.strip()
                speak(joke)
            except Exception as e:
                speak("Sorry, I couldn't fetch a joke right now.")
                print("Gemini joke error:", e)


        elif "exit" in command or "quit" in command or "stop" in command:
            speak("Goodbye!")
            sys.exit()

        else:
            speak("Let me think...")
            result = ask_ai(command)
            speak(result)

if __name__ == "__main__":
    try:
        run_jarvis()
    except KeyboardInterrupt:
        speak("Jarvis shutting down. Goodbye!")
        sys.exit()
