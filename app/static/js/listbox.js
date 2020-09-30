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
          if (todo_count!==null) {
            todo_count.innerHTML = payload['todo_count'];
          }
        // on back, hide taskbox and render in todo listbox
        } else if (action=='back') {
          taskbox.remove();
          todolistbox = document.getElementById('listbox-todo');
          empty_message = document.getElementById('empty-message-todo');
          if (empty_message!==null) {
            empty_message.remove();
          }
          todolistbox.innerHTML += payload['html'];
          todolistbox.scrollTo(0, todolistbox.scrollHeight);
          // edit number of tasks todo
          todo_count = document.getElementById('n-todo');
          if (todo_count!==null) {
            todo_count.innerHTML = payload['todo_count'];
          }
          // edit number of tasks completed
          complete_count = document.getElementById('n-completed');
          if (complete_count!==null) {
            complete_count.innerHTML = payload['complete_count'];
          }
        // on complete, hide taskbox and render in complete listbox
        } else if (action=='complete') {
          taskbox.remove();
          // hide empty message if there is one
          empty_message = document.getElementById('empty-message-completed');
          if (empty_message!==null) {
            empty_message.remove();
          }
          completelistbox = document.getElementById('listbox-completed');
          completelistbox.innerHTML += payload['html'];
          completelistbox.scrollTo(0, completelistbox.scrollHeight);
          // edit number of tasks todo
          todo_count = document.getElementById('n-todo');
          if (todo_count!==null) {
            todo_count.innerHTML = payload['todo_count'];
          }
          // edit number of tasks completed
          complete_count = document.getElementById('n-completed');
          if (complete_count!==null) {
            complete_count.innerHTML = payload['complete_count'];
          }
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

function pin(comment_id) {
  
}
