#from librapp import models
import random
import string
from Crypto.Cipher import AES

import api_key

class EncryptionHelper(object):
    #TODO use CBC
    def encrypt(self, plaintext=''):
        cipher_obj = AES.new(api_key.SECRET_AES_KEY)
        text_len = len(plaintext)
        # multiple of 16
        rstr = ''.join(random.choice(string.ascii_letters) for x in range(16-text_len%16))
        plaintext = '{0}{1}'.format(plaintext, rstr)
        ciphertext = cipher_obj.encrypt(plaintext)
        cipherbase64 = ciphertext.encode('hex')
        return cipherbase64

    def decrypt(self, tokenbase64=None):
        ciphertext = tokenbase64.decode('hex')
        cipher_obj = AES.new(api_key.SECRET_AES_KEY)
        plaintext = cipher_obj.decrypt(ciphertext)
        return plaintext


if __name__ == '__main__':
    eh = EncryptionHelper()
    #plain_text = 'foo|bar|spam|'
    plain_text = '123456.78|*|90|*|rkx120340@utdallas.edu|*|Rajnikant|*|'

    token = eh.encrypt(plaintext=plain_text)
    print token

    txt = eh.decrypt(tokenbase64=token)
    print txt
