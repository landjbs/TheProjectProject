function toggleStar() {
  {% if project_id in g.current_user.stars %}
    url = "{{ url_for('project.like_action', project_id=project.id, action='unlike') }}",
    star = false
  {% else %}
    url = "{{ url_for('project.like_action', project_id=project.id, action='like') }}",
    star = true
  {% endif %}
  alert(url);
  $.ajax({
    type: 'GET',
    url: url,
  })
  if star {
    $('#star_{{ project_id }}').class = 'fa fa-star'
  } else {
    $('#star_{{ project_id }}').class = 'fa fa-star-o'
  }
}
