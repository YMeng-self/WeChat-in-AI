
import requests
import uuid
import json
from pathlib import Path
from datetime import datetime
import logging


class SiliconFlowGenerator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.siliconflow.com/v1"
        self.output_dir = Path("generated_content")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化日志系统
        self.log_file = self.output_dir / "info.log"
        self._init_log()

    def _init_log(self):
        """初始化日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            # filename=self.log_file,
            filemode='a'
        )
        # 示例日志记录
        self.logger = logging.getLogger(__name__)

    def _api_request(self, method, endpoint, payload):
        """通用API请求方法"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=payload
                # timeout=300
            )
            # response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error("API Error", "", "Failed", str(e))
            return None

    def _download_image(self, url, filename):
        # 发送GET请求
        response = requests.get(url)
        
        # 检查请求是否成功
        if response.status_code == 200:
            # 打开一个文件用于保存图片
            with open(filename, 'wb') as f:
                f.write(response.content)
            self.logger.info("图片下载成功")
        else:
            self.logger.info("图片下载失败，状态码：", response.status_code)

    def generate_text(self, prompt):
        """生成文本内容"""
        # 生成唯一标识符
        uid = uuid.uuid4().hex[:8]
        filename = self.output_dir / f"text_{uid}.md"
       
        payload = {
            "model": 'deepseek-ai/DeepSeek-V3',
            "messages": [
                {"role": "system", "content": prompt}
            ],
            "stream": False,
            "max_tokens": 2000,
            "stop": ["null"],
            "temperature": 1.3,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"},
        }
        
        response = self._api_request("POST", "/chat/completions", payload)
        if not response:
            return None
            
        result = response.json()
        with open(filename, "w") as f:
            f.write(result['choices'][0]['message']['content'])
        
        self.logger.info(f"Text {filename} Success")
        return filename

    def generate_image(self, prompt, resolution="1024x1024"):
        """生成图片内容"""
        uid = uuid.uuid4().hex[:8]
        filename = self.output_dir / f"image_{uid}.png"
        
        payload = {
            "model": "deepseek-ai/Janus-Pro-7B",
            "prompt": prompt,
            "seed": 4999999999
        }
        
        response = self._api_request("POST", "/images/generations", payload)
        if not response:
            return None
            
        img_url = response.json()['images'][0]['url']
        self._download_image(img_url, filename)
        self.logger.info(f"Image {filename} Success")
        return filename


    def upload_audio(self, audio, customName):
        """上传音频"""
        uid = uuid.uuid4().hex[:8]
        filename = self.output_dir / f"audio_{uid}.mp3"

        payload = {
            "audio": audio,
            "model": "RVC-Boss/GPT-SoVITS",
            "customName": customName,
            "text": "在一无所知中, 梦里的一天结束了，一个新的轮回便会开始"
        }
        response = self._api_request("POST", "/uploads/audio/voice", payload)
        if not response:
            return None
        
        result = response.json()
        self.logger.info(f"Audio upload {customName} Success")
        return result['uri']

    def generate_audio(self, text):
        """生成音频内容"""
        uid = uuid.uuid4().hex[:8]
        filename = self.output_dir / f"audio_{uid}.mp3"
        
        payload = {
            "model": "RVC-Boss/GPT-SoVITS",
            "input": text,
            "voice": "RVC-Boss/GPT-SoVITS:alex",
            "response_format": "mp3",
            "sample_rate": 32000,
            "stream": True,
            "speed": 1,
            "gain": 0
        }
        
        response = self._api_request("POST", "/audio/speech", payload)
        if not response:
            return None
        
        with open(filename, "wb") as f:
            f.write(response.content)
        
        self.logger.info(f"Audio {filename} Success")
        return filename

    def batch_generate(self, tasks):
        """批量生成多类型内容"""
        results = {}
        for task in tasks:
            if task["type"] == "text":
                results[task["id"]] = self.generate_text(task["prompt"])
            elif task["type"] == "image":
                results[task["id"]] = self.generate_image(task["prompt"])
            elif task["type"] == "audio":
                results[task["id"]] = self.generate_audio(task["text"])
        return results


if __name__ == "__main__":
    # 初始化（从环境变量获取API密钥）
    # import os
    # api_key = os.getenv("SILICONFLOW_API_KEY")

    # 硅基流动的 API 密钥
    api_key = "sk-"
    
    generator = SiliconFlowGenerator(api_key)
    
    # 示例生成流程
    text_file = generator.generate_text(
        "请用Markdown格式写一篇关于人工智能的科普文章"
    )
    
    image_file = generator.generate_image(
        "未来城市与人工智能共生的场景，赛博朋克风格"
    )
    
    audio_file = generator.generate_audio(
        "欢迎来到智能时代，人工智能超乎你的想想"
    )
