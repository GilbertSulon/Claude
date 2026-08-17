/* ==========================================================
   EZ receptionist — maintenance mode switch
   Reads maintenance.txt (content: ON or OFF) and redirects
   between the live site and maintenance.html accordingly.
   Usage: <script src="assets/js/maintenance-check.js" data-mode="site"></script>
          <script src="assets/js/maintenance-check.js" data-mode="maintenance"></script>
   ========================================================== */

(function () {
  var scriptTag = document.currentScript;
  var mode = scriptTag.getAttribute('data-mode');
  var flagUrl = scriptTag.getAttribute('data-flag-url') || 'maintenance.txt';

  fetch(flagUrl + '?t=' + Date.now(), { cache: 'no-store' })
    .then(function (res) { return res.ok ? res.text() : 'OFF'; })
    .then(function (text) {
      var isOn = text.trim().toUpperCase() === 'ON';
      if (mode === 'site' && isOn) {
        window.location.replace('maintenance.html');
      } else if (mode === 'maintenance' && !isOn) {
        window.location.replace('index.html');
      }
    })
    .catch(function () {
      /* Flag unreachable: fail open, leave the current page as-is. */
    });
})();
