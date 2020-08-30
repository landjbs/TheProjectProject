function sendCollab(id) {
  alert(id);
  // $.ajax({
  //   type: 'POST',
  //   url: url,
  //   dataType: 'json',
  //   success: function(data){
  //     var stars = data['stars']
  //     var is_starred = data['is_starred']
  //     document.getElementById(count_id).innerHTML = stars + ' <i class="fa fa-star"></i>';
  //     if (is_starred==0) {
  //       document.getElementById(star_id).className = 'fa fa-star-o';
  //     } else {
  //       document.getElementById(star_id).className = 'fa fa-star';
  //     }
  //   }
  // })
}


// Set up an event listener for the contact form.
$('collab-form-').submit(function(event) {
    // Stop the browser from submitting the form.
    event.preventDefault();

    // TODO
});


// action="{{ url_for('user.collaborate', target_user_id=user.id) }}" method='post'
