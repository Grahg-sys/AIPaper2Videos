# coding=utf-8
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode, quote_plus


class TTSError(Exception):
    pass


class BaiduTTS:
    TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'
    TTS_URL = 'http://tsn.baidu.com/text2audio'
    SCOPE = 'audio_tts_post'
    
    def __init__(self, api_key="czlpzjB383wWcTXrR2uVtM8u", secret_key="GhXXnUMqhVS8WvhEsEORnK8jMmLvLRpN", per=4, spd=5, pit=5, vol=5, aue=3, cuid="123456PYTHON"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.per = per
        self.spd = spd
        self.pit = pit
        self.vol = vol
        self.aue = aue
        self.cuid = cuid
    
    def _fetch_token(self):
        params = {'grant_type': 'client_credentials', 'client_id': self.api_key, 'client_secret': self.secret_key}
        req = Request(self.TOKEN_URL, urlencode(params).encode('utf-8'))
        try:
            result = json.loads(urlopen(req, timeout=5).read().decode())
            if 'access_token' not in result or self.SCOPE not in result.get('scope', '').split(' '):
                raise TTSError('API_KEY或SECRET_KEY不正确')
            return result['access_token']
        except URLError as e:
            raise TTSError(f'获取token失败: {e}')
    
    def synthesize(self, text):
        if not text:
            raise TTSError('文本不能为空')
        
        token = self._fetch_token()
        params = {
            'tok': token, 'tex': quote_plus(text), 'per': self.per, 'spd': self.spd,
            'pit': self.pit, 'vol': self.vol, 'aue': self.aue, 'cuid': self.cuid,
            'lan': 'zh', 'ctp': 1
        }
        return f'{self.TTS_URL}?{urlencode(params)}'


if __name__ == '__main__':
    tts = BaiduTTS('czlpzjB383wWcTXrR2uVtM8u', 'GhXXnUMqhVS8WvhEsEORnK8jMmLvLRpN')
    print(tts.synthesize("欢迎使用百度语音合成。"))
