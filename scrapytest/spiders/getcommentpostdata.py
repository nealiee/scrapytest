import base64

from Cryptodome.Cipher import AES


class GetPostData(object):
    def __init__(self, songid, offset=0):
        self.songid = songid
        self.offset = offset

    def get_post_data(self):
        first_param = '{"rid":"R_SO_4_%s","offset":"%s","total":"true","limit":"20",' \
                      '"csrf_token":""}' % (self.songid, self.offset)
        forth_param = b'0CoJUm6Qyw8W8jud'
        params = self._get_params(first_param, forth_param)
        encSecKey = self._get_encSecKey()
        return {'params': params, 'encSecKey': encSecKey}

    def _get_params(self, first_param, forth_param):
        iv = b'0102030405060708'
        first_key = forth_param
        second_key = b'F' * 16
        encText = self._aes_encrypt(first_param, first_key, iv)
        encText = self._aes_encrypt(encText, second_key, iv)
        return encText

    def _get_encSecKey(self):
        return '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca9' \
               '19d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b5' \
               '4e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'

    def _aes_encrypt(self, text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text.encode())
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text.decode()