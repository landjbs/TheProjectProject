function toggleStar(project_id, url, star_id) {
  $.ajax({
    type: 'GET',
    url: url,
    dataType: 'json',
    success: function(data){
      var stars = data['stars']
      var is_starred = data['is_starred']
      if (is_starred==0) {
        document.getElementById(star_id).className = 'fa fa-star-o';
      } else {
        document.getElementById(star_id).className = 'fa fa-star';
      }
    }
  })
}
