function toggleStar(project_id, action) {
  if (action==1) {
    url = "{{ url_for('project.like_action', project_id=project.id, action='like') }}";
  } else {
    url = "{{ url_for('project.like_action', project_id=project.id, action='unlike') }}";
  }
  alert(url);
  $.ajax({
    type: 'GET',
    url: url,
  })
  if (action==0) {
    $('#star_{{ project_id }}').class = 'fa fa-star'
  } else {
    $('#star_{{ project_id }}').class = 'fa fa-star-o'
  }
}
