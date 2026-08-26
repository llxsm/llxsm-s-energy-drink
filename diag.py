import webview, time

LOG = "diag_result.txt"

class Api:
    def hello(self, name):
        return "hi " + name

HTML = """
<!doctype html><html><body>
<script>
window.__d = [];
window.__d.push("t0 pywebview=" + typeof window.pywebview + " api=" + (window.pywebview ? typeof window.pywebview.api : "none"));
setTimeout(function(){
  var a = window.pywebview && window.pywebview.api;
  var keys = a ? Object.keys(a) : [];
  window.__d.push("t1500 api=" + typeof a + " keys=" + JSON.stringify(keys));
}, 1500);
setTimeout(function(){
  var a = window.pywebview && window.pywebview.api;
  var keys = a ? Object.keys(a) : [];
  window.__d.push("t4000 api=" + typeof a + " keys=" + JSON.stringify(keys));
  if (a && a.hello) {
    a.hello("world").then(function(r){
      window.__d.push("call-result=" + JSON.stringify(r));
    }).catch(function(e){ window.__d.push("call-err=" + e.message); });
  }
}, 4000);
</script>
</body></html>
"""

def after_start():
    time.sleep(6)
    w = webview.windows[0]
    try:
        res = w.evaluate_js("JSON.stringify(window.__d)")
    except Exception as e:
        res = "EVAL-ERR-" + str(e)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write(str(res) + "\n")
    w.destroy()

webview.create_window("diag", html=HTML, width=400, height=300, js_api=Api())
webview.start(after_start)
