function toggleStar(project_id, url, action) {
  $.ajax({
    type: 'GET',
    url: url
  })
  if (action==0) {
    $('#star_{{ project_id }}').class = 'fa fa-star'
  } else {
    $('#star_{{ project_id }}').class = 'fa fa-star-o'
  }
}
