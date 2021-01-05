import sys
import os
from PIL import Image
import requests
from io import BytesIO
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from twocaptcha import TwoCaptcha

url = "https://captcha.nid.naver.com/nhncaptchav3.gif?key=OXAVrYSnoXgaLNVQ"
response = requests.get(url)
img = Image.open(BytesIO(response.content))

img.save('captcha.jpg')

api_key = os.getenv('APIKEY_2CAPTCHA', '51dfd4e96025f2921f2a695c6023e7f6')

solver = TwoCaptcha(api_key)

try:
    result = solver.normal('captcha.jpg')

except Exception as e:
    sys.exit(e)

else:
    sys.exit('solved: ' + str(result))