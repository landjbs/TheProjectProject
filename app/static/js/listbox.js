// TASKS
function change_task_status(project_id, task_id, action) {
  // build endpoint for editing task
  url = Flask.url_for(
          'project.change_task_status',
          {
            'project_id': project_id,
            'task_id'   : task_id,
            'action'    : action
          }
  );
  $.ajax(url).done(
    function (payload) {
      if (action=='delete') {
        document.getElementById.style.display = 'none';
      } else if (action='back') {
        document.getElementById.style.background = 'blue';
      } else if (action='complete') {
        document.getElementById.style.background = 'green';
      } else {
        alert('invalid action' + action);
      }
    }
  )
}


// COMMENTS
function delete_comment(project_id, comment_id) {
  url = Flask.url_for(
          'project.delete_comment',
          {'project_id':String(project_id), 'comment_id':String(comment_id)}
  );
  $.ajax(url).done(
    function (payload) {
      document.getElementById('comment-' + comment_id).style.display = 'none';
    }
  );
}
