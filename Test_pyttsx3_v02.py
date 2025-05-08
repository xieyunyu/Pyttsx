
# -*- coding: utf-8 -*-
import pyttsx3

try:
    # 初始化語音引擎，指定 SAPI5
    engine = pyttsx3.init('sapi5')

    # 獲取可用語音
    voices = engine.getProperty('voices')

    # 檢查是否有可用語音
    if not voices:
        print("錯誤：沒有找到任何語音，請檢查系統語音設定！")
        exit()

    # 選擇語音並設定語速和音量
    engine.setProperty('rate', 150)  # 稍慢的語速
    engine.setProperty('volume', 0.8)  # 柔和的音量

    # 選擇第一個語音並測試
    engine.setProperty('voice', voices[0].id)
    engine.say("你好，我是聲音索引0，我會講台灣狗語")
    engine.runAndWait()

except Exception as e:
    print(f"發生錯誤：{e}")


#---------------------------------------------------
import librosa
import soundfile as sf
import numpy as np
from scipy.signal import convolve

def adjust_pitch(input_file, output_file, semitones):
    """調整音調"""
    y, sr = librosa.load(input_file, sr=None)  # 保持原始採樣率
    y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
    sf.write(output_file, y_shifted, sr)

def apply_reverb(input_file, output_file, reverb_level=0.2):
    """加入簡單混響"""
    y, sr = librosa.load(input_file, sr=None)
    impulse_response = np.zeros(int(sr * 0.5))  # 0.5 秒的混響
    impulse_response[0] = 1
    impulse_response[int(sr * 0.1)] = reverb_level  # 延遲 0.1 秒
    reverbed_signal = convolve(y, impulse_response, mode='full')[:len(y)]
    sf.write(output_file, reverbed_signal, sr)

# --- 主程式 ---

engine = pyttsx3.init('sapi5')
engine.setProperty('rate', 140)
engine.setProperty('volume', 0.7)
engine.say("你好，這是測試語音。")
engine.save_to_file("input.wav", "你好，這是測試語音。")
engine.runAndWait()

# 調整音調
adjust_pitch("input.wav", "pitched.wav", semitones=2)  # 稍微提高音調

# 加入混響
apply_reverb("pitched.wav", "reverbed.wav", reverb_level=0.15)

print("已生成 pitched.wav 和 reverbed.wav")

