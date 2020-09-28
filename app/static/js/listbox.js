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
