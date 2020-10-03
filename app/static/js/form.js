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


// keydown listeners


// FORMTABBING
function getCurrentTab() {
  x = document.getElementsByClassName("formtab");
  for (i = 0; i < x.length; i++) {
    if (x[i].classList.contains('active'))
  }
  return false
}

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("formtab");
  x[n].style.display = "block";
  // get element to focus on
  var field = x[n].getElementsByTagName('input')[0];
  if (field==null) {
    var field = x[n].getElementsByTagName('textarea')[0];
  }
  if (field) {
    field.focus();
  }
  else {
    x[n].focus();
  }
  // ... and fix the Previous/Next buttons:
  if (n == 0) {
    document.getElementById("prevBtn").style.display = "none";
  } else {
    document.getElementById("prevBtn").style.display = "inline";
  }
  if (n == (x.length - 1)) {
    document.getElementById("nextBtn").innerHTML = "Submit";
  } else {
    document.getElementById("nextBtn").innerHTML = "Next";
  }
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("formtab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Can't go backwards on first tab
  if (n == -1 && currentTab==0) return false;
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form... :
  if (currentTab >= x.length) {
    //...the form gets submitted:
    submit();
    return false;
  }
  // Otherwise, display the correct tab:
  showTab(currentTab);
}

function validateForm() {
    // This function deals with validation of the form fields
    var x, y, i, valid = true;
    x = document.getElementsByClassName("formtab");
    y = x[currentTab].getElementsByTagName("input");
    // A loop that checks every input field in the current tab:
    for (i = 0; i < y.length; i++) {
      // If field has input tag
      if (y[i].id!="") {
        // If a field is empty...
        if (y[i].value == "") {
          // add an "invalid" class to the field if not interests
          y[i].className += " invalid";
          // and set the current valid status to false:
          valid = false;
        }
      }
    }
    return true; // return the valid status
  }



function default_keypress(e) {
  // tab is clicked
  if (e.keyCode==9) {
    // if shift is also down go backward
    if (e.shiftKey) {
      e.preventDefault();
      nextPrev(-1);
      return true
    }
    // tab by itself go forward
    else {
      e.preventDefault();
      nextPrev(1);
      return true
    }
  }
  // enter go forward
  else if (e.keyCode==13) {
    nextPrev(1);
    return true
  }
  return false
}


function boolean_keypress(e) {
  if (e.keyCode==65) {
    alert('yes');
    return true
  }
  else if (e.keyCode==66) {
    alert('no');
    return true
  }
  else {
    return false
  }
}


// keypress movement
function field_keydown(field_type, e) {
  // run through suite before specialty stuff
  var done = default_keypress(e);
  if (done==false) {
    if (field_type=='BooleanField') {
      boolean_keypress(e);
    }
  }
}
