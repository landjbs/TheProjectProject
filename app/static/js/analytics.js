(function() {
  var img = new Image,
      url = encodeURIComponent(document.location.href),
      title = encodeURIComponent(document.title),
      ref = encodeURIComponent(document.referrer);
  img.src = '%s/a.gif?url=' + url + '&t=' + title + '&ref=' + ref;
})();
