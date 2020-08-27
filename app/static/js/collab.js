function sendCollab(url) {
  $.ajax({
    type: 'POST',
    url: url,
    dataType: 'json',
    success: function(data){
      var stars = data['stars']
      var is_starred = data['is_starred']
      document.getElementById(count_id).innerHTML = stars + ' <i class="fa fa-star"></i>';
      if (is_starred==0) {
        document.getElementById(star_id).className = 'fa fa-star-o';
      } else {
        document.getElementById(star_id).className = 'fa fa-star';
      }
    }
  })
}
