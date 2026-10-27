import urllib.request
import re

url = "https://pulsomundial.onrender.com/analytics"
req = urllib.request.Request(url, headers={"User-Agent": "Check/1.0"})
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode("utf-8", "ignore")

ips = re.findall(r'class="ip-tag">([^<]+)</span>', html)
print("Top / Recent IPs recorded on server:")
for ip in ips[:15]:
    print(" -", ip)
