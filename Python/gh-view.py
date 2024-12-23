import requests
import threading

def send_request():
    while True:
        requests.head("https://camo.githubusercontent.com/7beb956516c60ec8ba4b4d58847415a271fecc96ca902b1bdb52dfa4442ff3d4/68747470733a2f2f6b6f6d617265762e636f6d2f67687076632f3f757365726e616d653d4d6979616e30303031266c6162656c3d50726f66696c65253230766965777326636f6c6f723d306537356236267374796c653d666c6174")

threads = []
for _ in range(1000):
    t = threading.Thread(target=send_request)
    t.start()
    threads.append(t)

for t in threads:
    t.join()