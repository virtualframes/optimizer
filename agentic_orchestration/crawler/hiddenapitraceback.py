import requests
import re
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class HiddenAPITraceback:
    def __init__(self, targets):
        self.targets = targets
        self.session = requests.Session()
        self.trace = []

    def fetch_html(self, url):
        try:
            r = self.session.get(url, timeout=10)
            return r.text if r.status_code == 200 else ""
        except Exception:
            return ""

    def extractjslinks(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        return [urljoin(base_url, script['src']) for script in soup.find_all("script", src=True)]

    def extractapipatterns(self, js_code):
        patterns = [
            r'https://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?',
            r'/[a-zA-Z0-9\-\./_]+',
            r'["\']/[a-zA-Z0-9\-\./_]+["\']'
        ]
        endpoints = []
        for pattern in patterns:
            endpoints += re.findall(pattern, js_code)
        return list(set(endpoints))

    def trace_site(self, url):
        html = self.fetch_html(url)
        jslinks = self.extractjslinks(html, url)
        for jsurl in jslinks:
            jscode = self.fetch_html(jsurl)
            endpoints = self.extractapipatterns(jscode)
            self.trace.append({
                "source": jsurl,
                "endpoints": endpoints,
                "timestamp": time.time()
            })

    def run(self):
        for url in self.targets:
            self.trace_site(url)

    def export(self, path="hiddenapitrace.json"):
        with open(path, "w") as f:
            json.dump(self.trace, f, indent=2)