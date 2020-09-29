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
      if (payload['success']) {
        taskbox = document.getElementById('task-' + task_id);
        // on delete, simply remove taskbox
        if (action=='delete') {
          // hide taskbox
          taskbox.style.display = 'none';
        // on back, hide taskbox and render in todo listbox
        } else if (action=='back') {
          taskbox.style.display = 'none';
          // render html in todo listbox
          // WARNING: this isnt optimized if ids change etc
          todolistbox = document.getElementById('');
        // on complete, hide taskbox and render in complete listbox
        } else if (action=='complete') {
          taskbox.style.display = 'none';
          // WARNING: this isnt optimized if ids change etc

        } else {
          alert('Invalid action: ' + action);
        }
      } else {
        alert('Could not modify task.');
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
