// // WARNING: deprecated for now


// window.onscroll = function() {scrollFunction()};
//
// function scrollFunction() {
//   if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
//     var disp = $('#nav-expanded').css('display');
//     if (disp=='block') {
//       var h = $('#nav-expanded').height();
//       document.getElementById("nav-expanded").style.display = 'none';
//       window.scrollBy(0, h+100);
//     } else {
//         document.getElementById("nav-expanded").style.display = 'none';
//     }
//   // show
// } else if (document.body.scrollTop==0 || document.documentElement.scrollTop==0) {
//     var disp = $('#nav-expanded').css('display');
//     if (disp=='none') {
//       document.getElementById("nav-expanded").style.display = 'block';
//       var h = $('#nav-expanded').height();
//       window.scrollBy(0, -h-100);
//     } else {
//       document.getElementById("nav-expanded").style.display = 'block';
//     }
//   }
// }
//
// function scrollToTop() {
//   var position =
//       document.body.scrollTop || document.documentElement.scrollTop;
//   if (position) {
//       window.scrollBy(0, -Math.max(1, Math.floor(position / 10)));
//       scrollAnimation = setTimeout("scrollToTop()", 30);
//   } else clearTimeout(scrollAnimation);
// }
