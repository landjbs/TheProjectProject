function field_char_counter(field) {
  var char_num = field.value.length;
  counter = document.getElementById('char_inc' + field.id);
  counter.innerHTML = char_num;
}
