# 利用刚刚propmtgen得到的生图提示词生成五个图

from volcenginesdkarkruntime import Ark


class ImageGenerator:
    def __init__(self):
        self.client = Ark(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key='81af5701-11b9-4a7c-981b-93f9437f9cc9',
        )
    
    def generate(self, prompt):
        response = self.client.images.generate(
            model="doubao-seedream-4-5-251128",
            prompt=prompt,
            size="2K",
            response_format="url",
            watermark=False
        )
        return response.data[0].url


if __name__ == "__main__":
    generator = ImageGenerator()
    url = generator.generate("一只小猪猪。")
    print(url)
