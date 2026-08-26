import webview
import time

LOG = "cam_result.txt"

class Api:
    def report(self, m):
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(m + "\n")

HTML = """
<!doctype html><html><body><script>
window.__status = "JS-RAN";
window.__status += " | mediaDevices=" + (navigator.mediaDevices ? "yes" : "no");
if (navigator.mediaDevices) {
  navigator.mediaDevices.getUserMedia({video:true, audio:false})
    .then(function(s){
      window.__status = "STREAM-OK";
      s.getTracks().forEach(function(t){ t.stop(); });
    })
    .catch(function(e){
      window.__status = "ERR-" + e.name + "-" + e.message;
    });
}
</script></body></html>
"""

def after_start():
    time.sleep(6)
    w = webview.windows[0]
    try:
        status = w.evaluate_js("window.__status || 'NO-JS'")
    except Exception as e:
        status = "EVAL-ERR-" + str(e)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write("POLL=" + str(status) + "\n")
    w.destroy()

open(LOG, "w").close()
webview.create_window("cam test", html=HTML, width=400, height=300, js_api=Api())
webview.start(after_start)
