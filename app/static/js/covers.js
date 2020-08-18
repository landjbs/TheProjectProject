function toggleInput(cover, input) {
  if (document.getElementById(cover).style.display!='none') {
    document.getElementById(cover).style.display = 'none';
    document.getElementById(input).style.display = 'block';
  } else {
    document.getElementById(cover).style.display = 'block';
    document.getElementById(input).style.display = 'none';
  }
}

function showSaveButton(id) {
  document.getElementById(id).style.display = 'inline-block';
}
