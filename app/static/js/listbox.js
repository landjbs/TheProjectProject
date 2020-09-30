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
          taskbox.remove();
          // edit number of tasks todo
          todo_count = document.getElementById('n-todo');
          todo_count.innerHTML = payload['count'];
        // on back, hide taskbox and render in todo listbox
        } else if (action=='back') {
          taskbox.remove();
          // WARNING: BACK WILL TEMP MOVE IF ONE PERSON UNCOMPLETES AND OTHERS DONT. SHOULD PROB FIX
          // WARNING: this isnt optimized if ids change etc
          todolistbox = document.getElementById('listbox-todo');
          empty_message = document.getElementById('empty-message-todo');
          if (empty_message!==null) {
            empty_message.remove();
          }
          todolistbox.innerHTML += payload['html'];
          todolistbox.scrollTo(0, todolistbox.scrollHeight);
          // edit number of tasks todo
          todo_count = document.getElementById('n-todo');
          todo_count.innerHTML = payload['count'];
        // on complete, hide taskbox and render in complete listbox
        } else if (action=='complete') {
          taskbox.remove();
          // WARNING: this whole thing isnt optimized if ids change etc
          // hide empty message if there is one
          empty_message = document.getElementById('empty-message-completed');
          if (empty_message!==null) {
            empty_message.remove();
          }
          completelistbox = document.getElementById('listbox-completed');
          completelistbox.innerHTML += payload['html'];
          completelistbox.scrollTo(0, completelistbox.scrollHeight);
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
            'project_id'  :   String(project_id),
            'comment_id'  :   String(comment_id)
          }
  );
  $.ajax(url).done(
    function (payload) {
      document.getElementById('comment-' + comment_id).remove();
    }
  );
}
