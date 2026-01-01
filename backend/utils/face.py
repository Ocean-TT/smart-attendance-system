import base64
import numpy as np
import cv2
import face_recognition

def extract_face_encoding(base64_str: str):
    try:
        # 去掉 base64 前缀 (data:image/jpeg;base64,...)
        if "," in base64_str:
            base64_str = base64_str.split(",")[1]
        
        img_data = base64.b64decode(base64_str)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return None
            
        # 转换颜色空间 (OpenCV 是 BGR, face_recognition 是 RGB)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # 提取特征
        encodings = face_recognition.face_encodings(rgb_img)
        if len(encodings) > 0:
            return encodings[0].tolist()
        return None
    except Exception as e:
        print(f"Face extraction error: {e}")
        return None
