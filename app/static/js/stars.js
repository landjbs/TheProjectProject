function toggleStar(project_id, url, action, star_id) {
  alert(url);
  $.ajax({
    type: 'GET',
    url: url,
    success: function(data){
      var stars = data['stars']
      var is_starred = data['is_starred']
    }
  })
  if (action==0) {
    document.getElementById(star_id).className = 'fa fa-star-o';
  } else {
      document.getElementById(star_id).className = 'fa fa-star';
  }
}
