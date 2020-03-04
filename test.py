import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS_JSON_PATH
from google.cloud import vision
from google.cloud.vision import types
from order_text import order_text

image_path = "Path / to / image / file"
img = cv2.imread(image_path)
client = vision.ImageAnnotatorClient()
content = cv2.imencode('.jpg', img)[1].tostring()
image = types.Image(content=content)
response = client.document_text_detection(image=image)

print (order_text(response))
