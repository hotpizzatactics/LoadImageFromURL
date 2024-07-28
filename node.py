import requests
from PIL import Image, ImageOps
import io
import hashlib
import numpy as np
import torch
import folder_paths

class LoadImageFromURL:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"url": ("STRING", {"default": "https://example.com/image.jpg"})},
                }

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    CATEGORY = "image"

    def load_image(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            i = Image.open(io.BytesIO(response.content))
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.mode:
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            return (image, mask)
        except Exception as e:
            raise ValueError(f"Error loading image from URL: {str(e)}")

    @classmethod
    def IS_CHANGED(s, url):
        m = hashlib.sha256()
        m.update(url.encode('utf-8'))
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, url):
        if not url.startswith(('http://', 'https://')):
            return "Invalid URL: must start with http:// or https://"
        return True