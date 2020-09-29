// QUESTIONS

// TODO: move ask listener here from macros/cards/question.html

// TODO: move edit_answer listener here from macros/cards/question.html

// delete question
// TODO: consolidate into single delete function
function delete_question(project_id, question_id) {
  url = Flask.url_for(
          'project.delete_question',
          {
            'project_id'    :   String(project_id),
            'question_id'   :   String(question_id)
          }
  );
  $.ajax(url).done(
    function (payload) {
      if (payload['success']==true) {
        document.getElementById('question-' + question_id).remove();
      } else {
        alert('Could not delete.')
      }
    }
  );
}
