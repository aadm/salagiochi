(function () {
  'use strict';

  var IMG_RE = /\.(jpe?g|png|gif|webp)(\?.*)?$/i;
  var links = document.querySelectorAll('.proof a');
  if (!links.length) {
    return;
  }

  var overlay = document.createElement('div');
  overlay.className = 'lightbox';
  var img = document.createElement('img');
  overlay.appendChild(img);
  document.body.appendChild(overlay);

  function close() {
    overlay.classList.remove('open');
  }

  links.forEach(function (link) {
    if (!IMG_RE.test(link.href)) {
      return;
    }
    link.addEventListener('click', function (event) {
      event.preventDefault();
      img.src = link.href;
      overlay.classList.add('open');
    });
  });

  overlay.addEventListener('click', close);
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      close();
    }
  });
})();