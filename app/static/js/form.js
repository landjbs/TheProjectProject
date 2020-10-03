// STRING FIELDS
// takes this object of field and updates character count
function field_char_counter(field) {
  var char_num = String(field.value.length);
  counter = document.getElementById('char_inc_' + field.id);
  counter.innerHTML = char_num;
}


// SLIDE FIELDS
function update_slider(field) {
  var val = field.value;
  document.getElementById('slider_inc_' + field.id).innerHTML = val;
}
