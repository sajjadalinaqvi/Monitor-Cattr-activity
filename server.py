"""
Cattr Activity Auditor - Local Server & Auto-Enriching Proxy
Fixes relationship naming, proxies API requests and screenshot media cleanly.
"""

import http.server
import socketserver
import urllib.request
import urllib.error
import json
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
TARGET_API = "https://monitor.datalyticsai.win"

def make_remote_request(url, method="POST", body=None, auth_header=""):
    data = json.dumps(body).encode("utf-8") if (body is not None and method == "POST") else None
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": auth_header,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CattrActivityAuditor/2.0"
        },
        method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read()
            return resp.status, content
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 500, json.dumps({"error": str(e)}).encode("utf-8")

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Suppress logging for thumbnail/image requests to keep console clean
        if len(args) > 0 and isinstance(args[0], str) and ("/uploads/" in args[0] or "/thumbs/" in args[0]):
            return
        super().log_message(format, *args)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept")
        self.end_headers()

    def do_GET(self):
        # Proxy uploaded screenshot images if requested
        if self.path.startswith("/uploads/"):
            target_url = f"{TARGET_API}{self.path}"
            auth_header = self.headers.get("Authorization", "")
            if not auth_header and os.path.exists(os.path.join(DIRECTORY, "debug_token.txt")):
                with open(os.path.join(DIRECTORY, "debug_token.txt"), "r", encoding="utf-8") as f:
                    auth_header = f.read().strip()
            
            req = urllib.request.Request(
                target_url,
                headers={"Authorization": auth_header, "User-Agent": "Mozilla/5.0"}
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    content = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", resp.headers.get("Content-Type", "image/jpeg"))
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(content)
                    return
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                return
            except Exception as e:
                try:
                    self.send_response(404)
                    self.end_headers()
                except Exception:
                    pass
                return

        return super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/") or self.path.startswith("/proxy/"):
            target_path = self.path.replace("/proxy", "")
            target_url = f"{TARGET_API}{target_path}"
            
            content_length = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_length)
            auth_header = self.headers.get("Authorization", "")

            # Save token for persistence
            if auth_header:
                with open(os.path.join(DIRECTORY, "debug_token.txt"), "w", encoding="utf-8") as f:
                    f.write(auth_header)

            try:
                body_decoded = json.loads(post_body.decode("utf-8")) if post_body else {}
            except Exception:
                body_decoded = {}

            # Sanitize body: Remove any snake_case "time_interval" to prevent Laravel undefined relation 500 error
            if "with" in body_decoded:
                if isinstance(body_decoded["with"], list):
                    body_decoded["with"] = [w for w in body_decoded["with"] if w != "time_interval"]
                    if "timeInterval" not in body_decoded["with"]:
                        body_decoded["with"].append("timeInterval")

            print(f"\n==================================================")
            print(f"[AUDITOR PROXY] Route: {target_path}")
            print(f"[AUDITOR PROXY] Target: {target_url}")

            # Handle /screenshots/list: attach correct eager loading relationship 'timeInterval'
            if "/screenshots/list" in target_path:
                url_to_try = target_url
                if "with" not in url_to_try:
                    url_to_try += ("&" if "?" in url_to_try else "?") + "with=timeInterval,timeInterval.task,timeInterval.user"
                
                status, res_body = make_remote_request(url_to_try, "POST", body_decoded, auth_header)
                print(f"[AUDITOR PROXY] Screenshots response HTTP {status} ({len(res_body)} bytes)")

                # If query param with= was rejected or empty, retry direct
                if status != 200:
                    print(f"[AUDITOR PROXY] Retrying without query param...")
                    status, res_body = make_remote_request(target_url, "POST", body_decoded, auth_header)

            else:
                # Direct proxy for /time-intervals/dashboard or other routes
                status, res_body = make_remote_request(target_url, "POST", body_decoded, auth_header)
                print(f"[AUDITOR PROXY] Response HTTP {status} ({len(res_body)} bytes)")

            # Send response to browser with permissive CORS
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type, Accept")
                self.end_headers()
                self.wfile.write(res_body)
            except (ConnectionAbortedError, ConnectionResetError, BrokenPipeError):
                pass

        else:
            self.send_response(404)
            self.end_headers()

def run():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), CustomHandler) as httpd:
        print(f"=======================================================", flush=True)
        print(f"🚀 Cattr Activity Auditor Server Running on port {PORT}", flush=True)
        print(f"📍 Open: http://localhost:{PORT}", flush=True)
        print(f"🔄 Auto-enrichment: ACTIVE (Clean Eager Loading & Image Proxy)", flush=True)
        print(f"=======================================================", flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.", flush=True)

if __name__ == "__main__":
    run()
