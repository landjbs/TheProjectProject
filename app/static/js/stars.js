function toggleStar(project_id, url, action, star_id) {
  $.ajax({
    type: 'GET',
    url: url
  })
  if (action==0) {
    document.getElementById(star_id).className = 'fa fa-star-o';
    // document.getElementById(star_id).classList.remove('fa-star');
    // document.getElementById(star_id).classList.add('fa-star-o');
  } else {
      document.getElementById(star_id).className = 'fa fa-star';
    // document.getElementById(star_id).classList.remove('fa-star-o');
    // document.getElementById(star_id).classList.add('fa-star');
  }
}
