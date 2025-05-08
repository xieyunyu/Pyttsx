import pyttsx3
from pydub import AudioSegment
from pydub.playback import play
from pydub.utils import which
from scipy.signal import convolve
import numpy as np
import random
import time
import tempfile
import os

def check_ffmpeg():
    """檢查 ffmpeg 是否可用"""
    if not which("ffmpeg") or not which("ffprobe"):
        raise EnvironmentError(
            "FFmpeg or ffprobe not found. Please install FFmpeg and add it to your system PATH. "
            "Download from https://www.gyan.dev/ffmpeg/builds/ and add the 'bin' folder to PATH."
        )

def adjust_pitch(audio_segment, semitones):
    """
    調整音高，模擬成熟女聲。
    
    參數：
        audio_segment (AudioSegment): 音訊對象。
        semitones (float): 半音數（正數升高，負數降低）。
    
    返回：
        AudioSegment: 調整後的音訊。
    """
    new_sample_rate = int(audio_segment.frame_rate * (2**(semitones/12.0)))
    pitched_sound = audio_segment._spawn(audio_segment.raw_data, overrides={'frame_rate': new_sample_rate})
    return pitched_sound.set_frame_rate(audio_segment.frame_rate)

def apply_reverb(audio_segment, decay=0.2):
    """
    加入輕微混響，增加溫暖感。
    
    參數：
        audio_segment (AudioSegment): 音訊對象。
        decay (float): 混響衰減係數（默認 0.2）。
    
    返回：
        AudioSegment: 加入混響的音訊。
    """
    samples = np.array(audio_segment.get_array_of_samples())
    impulse_response = np.zeros(int(audio_segment.frame_rate * 0.2))
    impulse_response[0] = 1
    for i in range(1, len(impulse_response)):
        impulse_response[i] = impulse_response[i - 1] * decay
    reverbed_samples = convolve(samples, impulse_response, mode='full')[:len(samples)]
    reverbed_samples = np.clip(reverbed_samples, -2**15, 2**15 - 1).astype(np.int16)
    return audio_segment._spawn(reverbed_samples.tobytes())

def natural_tts(text, base_rate=95, base_volume=0.8):
    """生成接近真實成熟女聲的語音，說繁體中文，直接播放，適配 MQTT。"""
    # 檢查 ffmpeg
    try:
        check_ffmpeg()
    except EnvironmentError as e:
        print(e)
        return

    local_engine = pyttsx3.init()
    voices = local_engine.getProperty('voices')
    # 打印可用語音以確認 Hanhan 是否為 voices[0]
    for i, voice in enumerate(voices):
        print(f"Voice {i}: {voice.name}, ID: {voice.id}")
    local_engine.setProperty('voice', voices[0].id)  # 固定 Hanhan

    # 分割句子
    sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
    sentences = [s.strip() for s in sentences if s.strip()]

    for i, sentence in enumerate(sentences):
        # 關鍵詞強調
        emphasis = 1.0
        if any(keyword in sentence for keyword in ['你好', '小智', '歡迎', '試試', '台灣']):
            emphasis = 1.003  # 極微強調，成熟語氣

        # 隨機調整語速（±0.3%）
        rate = int(base_rate * (0.997 + random.uniform(0.0, 0.006)) * emphasis)
        
        # 隨機調整音量（±0.3%）
        volume = base_volume * (0.997 + random.uniform(0.0, 0.006)) * emphasis
        if i == 0:
            volume *= 0.85  # 開頭柔和
        elif i == len(sentences) - 1:
            volume *= 1.05  # 結尾微上揚
        
        # 生成語音到臨時檔案
        try:
            local_engine.stop()  # 停止任何現有任務
            local_engine.setProperty('rate', rate)
            local_engine.setProperty('volume', min(volume, 1.0))
            
            # 使用臨時 WAV 檔案進行波形處理
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                local_engine.save_to_file(sentence, tmp_file.name)
                local_engine.runAndWait()
                temp_file_name = tmp_file.name
            
            # 波形處理
            try:
                audio = AudioSegment.from_wav(temp_file_name)
                if len(audio) < 100:  # 音訊過短，跳過處理
                    print(f"音訊過短 ({len(audio)}ms)，直接播放: {sentence}")
                    play(audio)
                    os.remove(temp_file_name)
                    continue
                
                # 音高調整（+0.3 半音）
                audio = adjust_pitch(audio, 0.3)
                # 低通濾波
                audio = audio.low_pass_filter(4500)
                # 混響
                audio = apply_reverb(audio, decay=0.2)
                # 正規化音量
                audio = audio.normalize()
                
                # 直接播放
                play(audio)
            except Exception as e:
                print(f"音訊處理失敗: {e}")
                play(AudioSegment.from_wav(temp_file_name))  # 播放原始音訊
            
            # 清理臨時檔案
            os.remove(temp_file_name)
        
        except RuntimeError as e:
            print(f"RuntimeError encountered: {e}. Trying to stop and restart.")
            local_engine.stop()
            local_engine.setProperty('rate', rate)
            local_engine.setProperty('volume', min(volume, 1.0))
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                local_engine.save_to_file(sentence, tmp_file.name)
                local_engine.runAndWait()
                temp_file_name = tmp_file.name
            try:
                audio = AudioSegment.from_wav(temp_file_name)
                if len(audio) >= 100:
                    audio = adjust_pitch(audio, 0.3)
                    audio = audio.low_pass_filter(4500)
                    audio = apply_reverb(audio, decay=0.2)
                    audio = audio.normalize()
                play(audio)
            except Exception as e:
                print(f"音訊處理失敗: {e}")
                play(AudioSegment.from_wav(temp_file_name))
            os.remove(temp_file_name)
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            continue
        
        # 句子間停頓（0.5-0.8 秒）
        time.sleep(random.uniform(0.5, 0.8))

if __name__ == "__main__":
    # 測試語音
    test_text = "你好，我是小智，我會講台灣狗已！"
    natural_tts(test_text)
    
    # 測試單獨「你好」
    time.sleep(2)
    natural_tts("你好")