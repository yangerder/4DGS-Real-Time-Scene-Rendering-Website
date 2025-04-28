import requests

file_path = "cam1.mp4"
url = "http://localhost:8000/upload_and_extract"

with open(file_path, "rb") as f:
    files = {"file": (file_path, f, "video/mp4")}
    response = requests.post(url, files=files)

print(response.status_code)
print(response.json())
