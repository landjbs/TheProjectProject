function toggleStar(project_id, unstar) {
  if unstar {
    url = "{{ url_for('project.like_action', project_id=project.id, action='unlike') }}",
  } else {
    url = "{{ url_for('project.like_action', project_id=project.id, action='like') }}",
  }
  alert(url);
  $.ajax({
    type: 'GET',
    url: url,
  })
  if unstar {
    $('#star_{{ project_id }}').class = 'fa fa-star-o'
  } else {
    $('#star_{{ project_id }}').class = 'fa fa-star'
  }
}
