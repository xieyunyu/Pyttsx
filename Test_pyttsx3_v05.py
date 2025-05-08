import pyttsx3
import random
import time
from pydub import AudioSegment
import os
import tempfile

def natural_tts(text, base_rate=95, base_volume=0.8, pitch_shift=1.05):
    """
    生成自然的溫柔女聲，使用 Voice 0 (Hanhan)，修復發音不自然（如「你好」像「逆好」），在地端執行。
    
    參數：
        text (str): 要轉換為語音的文本。
        base_rate (int): 基礎語速（默認 95，穩定溫柔）。
        base_volume (float): 基礎音量（默認 0.8，柔和）。
        pitch_shift (float): 音高調整倍數（默認 1.05，成熟女聲）。
    
    返回：
        None
    """
    engine = pyttsx3.init()
    
    # 固定使用 Voice 0 (Hanhan)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    
    # 臨時 WAV 檔案
    temp_wav = os.path.join(tempfile.gettempdir(), "temp_tts.wav")
    
    # 分割文本為句子
    sentences = text.replace('。', '。|').replace('！', '！|').replace('？', '？|').split('|')
    sentences = [s.strip() for s in sentences if s.strip()]

    for i, sentence in enumerate(sentences):
        # 關鍵詞強調
        emphasis = 1.0
        if any(keyword in sentence for keyword in ['你好', '歡迎', '試試', '小幫手', '健康']):
            emphasis = 1.005  # 極微強調，沉穩

        # 隨機調整語速（±0.5%）
        rate = int(base_rate * (0.995 + random.uniform(0.0, 0.01)) * emphasis)
        engine.setProperty('rate', rate)
        
        # 隨機調整音量（±0.5%）
        volume = base_volume * (0.995 + random.uniform(0.0, 0.01)) * emphasis
        if i == 0:
            volume *= 0.85  # 開頭柔和
        elif i == len(sentences) - 1:
            volume *= 1.05  # 結尾微上揚
        engine.setProperty('volume', min(volume, 1.0))
        
        # 保存語音到臨時檔案
        engine.save_to_file(sentence, temp_wav)
        engine.runAndWait()
        
        # 波形處理
        try:
            audio = AudioSegment.from_wav(temp_wav)
            if len(audio) < 100:  # 音訊過短，跳過處理
                os.system(f"start {temp_wav}")  # Windows 播放
                continue
            
            # 音高調整
            new_sample_rate = int(audio.frame_rate * pitch_shift)
            audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
            # 正規化音量
            audio = audio.normalize()
            # 低通濾波
            if len(audio) > 0:
                audio = audio.low_pass_filter(4000)  # 提高頻率，保留細節
            
            # 播放處理後音訊
            audio.export(temp_wav, format="wav")
            os.system(f"start {temp_wav}")  # Windows 播放
        except Exception as e:
            print(f"音訊處理失敗: {e}")
            os.system(f"start {temp_wav}")  # 直接播放未處理音訊
        
        # 句子間停頓（0.5-0.9 秒）
        time.sleep(random.uniform(0.5, 0.9))
    
    # 清理臨時檔案
    if os.path.exists(temp_wav):
        os.remove(temp_wav)
    engine.stop()

if __name__ == "__main__":
    # 測試語音
    test_text = "你好！我是小幫手，來試試免費健康測量吧！"
    natural_tts(test_text)
    
    # 可選：測試單獨「你好」發音
    time.sleep(2)  # 等待前次播放完成
    natural_tts("你好")