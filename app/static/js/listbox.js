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
      taskbox = document.getElementById('task' + task_id);
      if (action=='delete') {
        taskbox.style.display = 'none';
      } else if (action='back') {
        taskbox.style.background = 'blue';
      } else if (action='complete') {
        taskbox.style.background = 'green';
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
          {
            'project_id':String(project_id),
            'comment_id':String(comment_id)
          }
  );
  $.ajax(url).done(
    function (payload) {
      document.getElementById('comment-' + comment_id).style.display = 'none';
    }
  );
}
