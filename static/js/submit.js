(function () {
  'use strict';

  var form = document.getElementById('score-form');
  if (!form) {
    return;
  }

  var repo = form.getAttribute('data-repo');

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    var game = document.getElementById('game').value.trim();
    var score = document.getElementById('score').value.trim();
    var player = document.getElementById('player').value.trim();
    var note = document.getElementById('note').value.trim();

    if (!game || !score || !player) {
      return;
    }

    var digits = score.replace(/\D/g, '');
    if (digits === '') {
      alert('Inserisci un punteggio numerico valido.');
      return;
    }

    var title = '[PUNTEGGIO] ' + game + ' - ' + player + ': ' + digits;

    var body = [
      '**Gioco:** ' + game,
      '**Punteggio:** ' + digits,
      '**Giocatore:** ' + player
    ];
    if (note) {
      body.push('**Nota:** ' + note);
    }

    var url = 'https://github.com/' + repo + '/issues/new?title='
      + encodeURIComponent(title) + '&body=' + encodeURIComponent(body.join('\n'));

    window.open(url, '_blank');
  });
})();