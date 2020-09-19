function open_single_channel(user_id) {
  var data = JSON.stringify({'user_id' : user_id})
  $.ajax({
    url: "{{ url_for('message.open_single_channel' }}",
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: data,
    success: function(data) {
      alert(data['channel'])
      alert('channel opened');
      // var messages = document.getElementById('messages')
      // document.getElementById('messageText').value = '';
      // messages.innerHTML += data['html'];
      // messages.scrollTo(0, messages.scrollHeight);
    }
  })
}
