function toggleStar(project_id, url, action, star_id) {
  alert(url);
  $.ajax({
    type: 'GET',
    url: url
  })
  if (action==0) {
    document.getElementById(star_id).className = 'fa fa-star-o';
  } else {
      document.getElementById(star_id).className = 'fa fa-star';
  }
}
