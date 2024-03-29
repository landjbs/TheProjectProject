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


// open up channel of channel_id
function open_channel(channel_id) {
  var channel_data = JSON.stringify({'channel_id':channel_id});
  $.ajax({
    url: '/get_channel',
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: channel_data,
    success: function(payload) {
      if (window.poller) {
        clearInterval(window.poller);
      }
      var messageBox = document.getElementById('messageBox');
      messageBox.innerHTML = payload['html'];
      clearInterval();
      openForm(payload['channel_id']);
    }
  })
}


// update channel last_read for current_user to now
function update_last_read(channel_id) {
  const data = {'channel_id' :   String(channel_id)};
  const searchParams = new URLSearchParams(data);
  // update and hide unread badge if it exists
  $.ajax(Flask.url_for('message.update_last_read') + '?' + searchParams).done(
    function() {
      var badge = document.getElementById('badge-' + String(channel_id));
      badge.style.display = 'none';
    }
  );
}


// open form for message
// // TODO: fix terrible name and ids. maybe make channel specific so multiple can render
function openForm(channel_id) {
  var messages = document.getElementById('messages');
  document.getElementById("myForm").style.display = "block";
  document.getElementById('openBtn').style.display = 'none';
  // scroll to bottom of messages
  messages.scrollTo(0, messages.scrollHeight);
  // update last read for channel
  update_last_read(channel_id);
  // start polling
  var since = 0;
  var poller = setInterval(
      // poll channel of channel_id for new messages. since is start time
      function poll_channel() {
        const data = {
          'since'   :   String(since),
          'channel' :   String(channel_id)
        };
        const searchParams = new URLSearchParams(data);
        $.ajax(Flask.url_for('message.check_messages') + '?' + searchParams).done(
            function(message_data) {
                since = message_data['since'];
                var new_messages = message_data['new_messages'];
                for (var i = 0; i < new_messages.length; i++) {
                    messages.innerHTML += new_messages[i];
                    messages.scrollTo(0, messages.scrollHeight);
            }
          }
        );
        return since;
      },
      1000
  );
  window.poller = poller;
}


// closes message form
// // TODO: fix terrible name and ids. maybe make channel specific so multiple can render
function closeForm() {
  document.getElementById("myForm").style.display = "none";
  document.getElementById('openBtn').style.display = 'block';
  // clear channel poller running in window
  clearInterval(window.poller);
}


// completely clears messageBox and stops poller if running
function clearChat() {
  document.getElementById('messageBox').innerHTML = '';
  if (window.poller) {
    clearInterval(window.poller);
  }
}


// poll big message badge
var n_message_badge = document.getElementById('nMessageBadge');
function poll_new_messages() {
  $.ajax(Flask.url_for('message.new_messages')).done(
    function(payload) {
      var n = payload['n'];
      if (n>0) {
        n_message_badge.style.display = 'inline-block';
        n_message_badge.innerHTML = n;
      } else {
        n_message_badge.style.display = 'none';
      }
    }
  );
}


// render html for messages in message dropdown
var channel_list = document.getElementById('channelList');
function open_message_dropdown() {
  $.ajax(Flask.url_for('message.get_channel_list')).done(
    function(payload) {
      channel_list.innerHTML = payload['html'];
    }
  );
}
