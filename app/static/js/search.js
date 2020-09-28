function filterFunction(searchId, dropdownId) {
  var input, filter, ul, li, a, i;
  input = document.getElementById(searchId);
  filter = input.value.toUpperCase();
  div = document.getElementById(dropdownId);
  a = div.getElementsByClassName('searchable');
  for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
      a[i].style.display = "";
    } else {
      a[i].style.display = "none";
    }
  }
}
