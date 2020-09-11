function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" active", "");
  }
  // hide tooltips
  $('[data-toggle="tooltip"]').tooltip('hide');
  document.getElementById(tabName).style.display = "block";
  // show tooltip in selected tab
  $('#' + tabName + ' [data-toggle="tooltip"]').tooltip('show');
  evt.currentTarget.className += " active";
  sessionStorage.setItem(
    (window.location.href + '_opened'), (tabName + '_Button')
  );
  Glider(document.querySelector('.glider')).refresh();
}
