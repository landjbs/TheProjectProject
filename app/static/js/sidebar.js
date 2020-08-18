function readySidebar() {
    $("#sidebar").mCustomScrollbar({
         theme: "minimal"
    });
    $('#sidebarCollapse').on('click', function () {
        // open or close navbar
        $('#sidebar').toggleClass('active');
        // close dropdowns
        $('.collapse.in').toggleClass('in');
        // and also adjust aria-expanded attributes we use for the open/closed arrows
        // in our CSS
        $('a[aria-expanded=true]').attr('aria-expanded', 'false');
    });

    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $(this).toggleClass('active');
    });

    if (sessionStorage.openTab) {
      document.getElementById(sessionStorage.openTab).click();
    } else {
      document.getElementById("Activity").click();
    }
}
