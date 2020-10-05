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
  document.getElementById('slider_inc_' + field.id).value = val;
}

function set_slider(id, num_id, min, max) {
  var slider = document.getElementById(id);
  var input = Number(document.getElementById(num_id).value);
  slider.value = input;
}

// FORMTABBING
function getCurrentTab() {
  x = document.getElementsByClassName("formtab");
  for (i = 0; i < x.length; i++) {
    if (x[i].style.display=='block') {
      return x[i]
    }
  }
  return false
}

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("formtab");
  x[n].style.display = "block";
  // get element to focus on
  var field = x[n].querySelector("input[type='text']");
  if (field==null) {
    var field = x[n].querySelector("input[type='number']");
  }
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
  // if (n == (x.length - 1)) {
  //   document.getElementById("nextBtn").innerHTML = "Submit";
  // } else {
  //   document.getElementById("nextBtn").innerHTML = "Next";
  // }
}

function nextPrev(n) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("formtab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && !validateForm()) return false;
  // Can't go backwards on first tab
  if (n == -1 && currentTab==0) return false;
  // Modify remaining time
  // var field_seconds = Number(x[currentTab].getAttribute('data-seconds'));
  // var time_inc = document.getElementById('form_time_inc').innerHTML;
  // var time_rem = Number(time_inc) - field_seconds;
  // document.getElementById('form_time_inc').innerHTML = String(time_rem);
  // Hide the current tab:
  x[currentTab].style.display = "none";
  // Increase or decrease the current tab by 1:
  currentTab = currentTab + n;
  // if you have reached the end of the form... :
  if (currentTab >= x.length) {
    //...the form gets submitted:
    // submit_fragment('Add_Type');
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
    for (i=0; i<y.length; i++) {
        elt = y[i];
        if (elt.type=='text') {
          if (elt.value.length<1) {
            return false;
          }
        }
        else if (elt.type=='radio') {
          is_checked = false;
          options = elt.value;
          for (j=0; j<options.length; j++) {
            
          }
        }
    }
    // A loop that checks every input field in the current tab:
    // for (i = 0; i < y.length; i++) {
    //   // If field has input tag
    //   if (y[i].id!="") {
    //     // If a field is empty...
    //     if (y[i].value == "") {
    //       // add an "invalid" class to the field if not interests
    //       y[i].className += " invalid";
    //       // and set the current valid status to false:
    //       valid = false;
    //     }
    //   }
    // }
    return true; // return the valid status
  }


// KEYDOWNS
function default_keypress(e) {
  // tab is clicked
  if (e.keyCode==9) {
    // if shift is also down go backward
    if (e.shiftKey) {
      // click prev button
      document.getElementById('prevBtn').click();
      e.preventDefault();
      // nextPrev(-1);
      return true
    }
    // tab by itself go forward
    else {
      // click next button
      document.getElementById('nextBtn').click();
      e.preventDefault();
      return true
    }
  }
  // enter go forward
  else if (e.keyCode==13) {
    // click next button
    document.getElementById('nextBtn').click();
    e.preventDefault();
    return true
  }
  return false
}


function switch_boolean(field, switch_prefix) {
  var id = field.getAttribute('data-field-id');
  var switch_obj = document.getElementById(switch_prefix + '-' + id);
  if (switch_obj.checked!=true) {
    switch_obj.click();
    return true
  }
  return false
}


function boolean_keypress(e, field) {
  if (e.keyCode==65) {
    switch_boolean(field, 'on');
    return true
  }
  else if (e.keyCode==66) {
    switch_boolean(field, 'off');
    return true
  }
  else {
    return false
  }
}

function select_keypress(e, field) {
  var code = e.keyCode;
  var options = field.getElementsByTagName('input');
  for (i=0; i < options.length; i++) {
    var option = options[i];
    var key = option.getAttribute('data-key').toUpperCase().charCodeAt();
    if (key==code) {
      if (option.checked==false) {
        // set option to checked
        option.click();
        return true
      }
    }
  }
  return false
}

function int_keypress(e, field) {

}


// keypress movement
function field_keydown(e, field) {
  // run through default suite before specialty stuff
  var done = default_keypress(e);
  if (done==false) {
    // determine type of field
    var field_type = field.getAttribute('data-field-type');
    // if boolean field
    if (field_type=='BooleanField') {
      done = boolean_keypress(e, field);
    }
    else if (field_type=='SelectField') {
      done = select_keypress(e, field);
    }
  // if successfully done, move to the next tab
  if (done==true) {
    setTimeout(function(){ nextPrev(1); }, 300);
  }
  }
}


// FIELD SUBMIT
function submit_field(field_id) {
  var url = Flask.url_for('add.next_field');

}


// FRAGMENT SUBMIT
function submit_fragment(form_id) {
  var url = Flask.url_for('add.next_fragment');
  $.ajax({
    type: "POST",
    url: url,
    data: $('#' + form_id).serialize(), // serializes the form's elements.
    success: function (data) {
        // console.log(data)  // display the returned data in the console.
        document.getElementById('fragments').innerHTML += data['html'];
        nextPrev(1);
        nextPrev(-1);
    }
  });
  // Inject our CSRF token into our AJAX request.
  $.ajaxSetup({
      beforeSend: function(xhr, settings) {
          if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
              xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
          }
      }
  });
}


// // TEMP:
function set_type(type) {
  var elts = document.getElementsByClassName('project_type');
  for (i=0; i<elts.length; i++) {
    elts[i].innerHTML = type;
  }
}

function hide_class(cls) {
  document.querySelectorAll('.' + cls).forEach(function(el) {
    // // TODO: used clone to save classes so can go back
    el.remove();
  });
}


function validate_input(field) {
  if (field.type=='text') {
    if (field.value.length<1) {
      alert('bad');
    }
  }
}
