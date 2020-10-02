// sessionStorage.setItem('n', 0);
var select_box = document.getElementById('select-box');
var subject_tags = select_box.getElementsByClassName('subject-tag');
var select = document.getElementById('hidden-select');
// start selected subjects as selected
var prev_selected = select_box.getElementsByClassName('selected-subjects')[0];
for(var i=0; i<prev_selected.lenght; i++) {
  var id = prev_selected[i].getAttribute("data");
  select.getElementsByTagName('option')[id-1].selected = true;
}
var subject_click = function () {
  var subject_id = this.getAttribute("data");
  var selected = this.getAttribute('selected');
  this.remove();
  if (selected=='false') {
    $('.selected-subjects').append(this);
    this.setAttribute('selected', 'true');
    select.getElementsByTagName('option')[subject_id-1].selected = true;
    // sessionStorage.setItem('n', sessionStorage.getItem('n')+1);
  } else {
    $('.unselected-subjects').append(this);
    this.setAttribute('selected', 'false');
    select.getElementsByTagName('option')[subject_id-1].selected = false;
    // sessionStorage.setItem('n', sessionStorage.getItem('n')-1);
  }
}
for(var i=0;i<subject_tags.length;i++){
    var tag = subject_tags[i];
    tag.addEventListener('click', subject_click, false);
    var prev_selected = tag.parentElement.classList.contains('selected-subjects');
    if (prev_selected) {
      var subject_id = tag.getAttribute("data");
      tag.setAttribute('selected', 'true');
      select.getElementsByTagName('option')[subject_id-1].selected = true;
    }
}
