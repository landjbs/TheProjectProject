function toggleStar(project_id, url, action, star_id) {
  $.ajax({
    type: 'GET',
    url: url
  })
  if (action==0) {
    $(star_id).classList.remove('fa-star');
    $(star_id).classList.add('fa-star-o');
  } else {
    $(star_id).classList.remove('fa-star-o');
    $(star_id).classList.add('fa-star');
  }
}
