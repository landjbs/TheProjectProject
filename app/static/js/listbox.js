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
        // on back, hide taskbox and render in todo listbox
        } else if (action=='back') {
          taskbox.remove();
          // WARNING: this isnt optimized if ids change etc
          todolistbox = document.getElementById('listbox-todo');
          todolistbox.innerHTML += payload['html'];
          todolistbox.scrollTo(0, todolistbox.scrollHeight);
        // on complete, hide taskbox and render in complete listbox
        } else if (action=='complete') {
          taskbox.remove();
          // WARNING: this isnt optimized if ids change etc
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
      document.getElementById('comment-' + comment_id).style.display = 'none';
    }
  );
}


// QUESTIONS (technically not in a listbox but it hasn't come up yet)
// edit answer to question already in question box (doesn't have to be answered)
function edit_answer(project_id, question_id) {
  url = Flask.url_for(
          'project.edit_answer',
          {
            'project_id'    :   String(project_id),
            'question_id'   :   String(question_id)
          }
  );
  question = document.getElementById('question-' + question_id);
  answer = question.getElementsByName('answer')[0].value;
  console.log(answer);
  data = JSON.stringify({'answer':answer});
  $.ajax(
    url: url,
    type: 'POST',
    dataType: 'json',
    contentType: 'application/json',
    data: data,
  ).done(
    function (payload) {
      if payload['success'] {
        question.style.border_color = 'green';
      }
    }
  );
}
