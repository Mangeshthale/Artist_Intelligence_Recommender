import os
import base64
from typing import List, Dict, Any
from PIL import Image
import cv2
from mutagen import File as MutagenFile

class MediaProcessor:
    """
    Selective media processor that samples keyframes from video
    and inspects technical metadata from audio/images without heavy processing.
    """
    @staticmethod
    def encode_image_base64(image_path: str, max_size=(512, 512)) -> str:
        with Image.open(image_path) as img:
            img.thumbnail(max_size)
            img = img.convert("RGB")
            temp_path = image_path + ".thumb.jpg"
            img.save(temp_path, format="JPEG", quality=80)
        
        with open(temp_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return encoded

    @staticmethod
    def sample_video_keyframes(video_path: str, num_samples: int = 3) -> List[Dict[str, Any]]:
        """Samples up to 3 distributed frames instead of decoding the entire stream."""
        frames = []
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        
        if total_frames <= 0:
            cap.release()
            return frames

        step = max(1, total_frames // (num_samples + 1))
        for i in range(1, num_samples + 1):
            frame_idx = i * step
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if ret:
                timestamp = f"{frame_idx / fps:.1f}s"
                temp_frame_path = f"{video_path}_frame_{i}.jpg"
                cv2.imwrite(temp_frame_path, frame)
                b64 = MediaProcessor.encode_image_base64(temp_frame_path)
                if os.path.exists(temp_frame_path):
                    os.remove(temp_frame_path)
                frames.append({"timestamp": timestamp, "base64": b64})
        cap.release()
        return frames

    @staticmethod
    def extract_audio_metadata(audio_path: str) -> Dict[str, Any]:
        """Extracts technical signals from audio without heavy audio ML dependencies."""
        try:
            audio = MutagenFile(audio_path)
            if audio is not None and audio.info:
                return {
                    "duration_seconds": round(audio.info.length, 2),
                    "bitrate_kbps": getattr(audio.info, "bitrate", None),
                    "sample_rate_hz": getattr(audio.info, "sample_rate", None),
                    "channels": getattr(audio.info, "channels", None)
                }
        except Exception as e:
            return {"error": f"Failed to read audio metadata: {str(e)}"}
        return {"status": "metadata_unavailable"}