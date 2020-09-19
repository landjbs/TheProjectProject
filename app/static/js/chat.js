$.ajaxSetup({
  headers: {'X-CSRFToken': '{{ csrf_token() }}'}
})

function open_single_channel(x) {
  $.ajax({
    url: '/test',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    success: function(data) {
      alert(data['boop']);
    }
  })
}

// function open_single_channel(user_id) {
//   var user_data = JSON.stringify({'user_id' : String(user_id)});
//   alert(user_data);
//   $.ajax({
//     url: '/open_single_channel',
//     type: 'POST',
//     dataType: 'json',
//     contentType: 'application/json',
//     data: user_data,
//     success: function(data) {
//       // var modal = document.getElementById(modal_id);
//       // modal.classList.remove('fade');
//       // modal.hide();
//       // add chat to document html
//       document.body.innerHTML += data['html'];
//       // TODO: open chat
//       openForm();
//       // var messages = document.getElementById('messages')
//       // document.getElementById('messageText').value = '';
//       // messages.innerHTML += data['html'];
//       // messages.scrollTo(0, messages.scrollHeight);
//     }
//   })
// }
