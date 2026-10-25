"""Temporary LAN download of the APK only; no source or credential access."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
APK=Path(__file__).resolve().parents[1]/'releases/HiperMeal-phone-test.apk'
class Download(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path!='/hipermeal.apk':
   self.send_error(404);return
  data=APK.read_bytes()
  self.send_response(200)
  self.send_header('Content-Type','application/vnd.android.package-archive')
  self.send_header('Content-Disposition','attachment; filename="HiperMeal-phone-test.apk"')
  self.send_header('Content-Length',str(len(data)))
  self.send_header('Cache-Control','no-store')
  self.end_headers();self.wfile.write(data)
 def log_message(self,*args):pass
if __name__=='__main__':
 server=ThreadingHTTPServer(('0.0.0.0',4184),Download)
 timer=threading.Timer(7200,server.shutdown);timer.daemon=True;timer.start()
 print('APK download available on port 4184 for two hours.',flush=True)
 try:server.serve_forever()
 finally:server.server_close()
