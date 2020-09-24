// TODO: fix csrf integration so this doesnt return 400 error
// function open_single_channel(user_id, token) {
//   var user_data = JSON.stringify({'user_id' : String(user_id)});
//   $.ajax({
//     url: '/open_single_channel',
//     type: 'POST',
//     data: user_data,
//     dataType : 'json',
//     contentType: "application/json",
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


function send_message(channel_id) {
  var text = document.getElementById('messageText').value;
  var form_data = JSON.stringify({'channel_id':channel_id, 'text':text});
  $.ajax({
    url: "/send_message",
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: form_data,
    success: function(data) {
      var messages = document.getElementById('messages');
      document.getElementById('messageText').value = '';
      messages.innerHTML += data['html'];
      messages.scrollTo(0, messages.scrollHeight);
    }
  })
}


function open_channel(channel_id) {
  var channel_data = JSON.stringify({'channel_id':channel_id});
  $.ajax({
    url: '/get_channel',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: channel_data,
    success: function(payload) {
      var messageBox = document.getElementById('messageBox');
      messageBox.innerHTML = payload['html'];
      openForm(payload['channel_id']);
    }
  })
}
