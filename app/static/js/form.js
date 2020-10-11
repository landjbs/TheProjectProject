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

function getTabById(id) {
  // TODO: actually move to tab using showTab()
  formtab = document.getElementById(id + '_segment');
  return formtab
}

function showTab(n) {
  // This function will display the specified tab of the form ...
  var x = document.getElementsByClassName("formtab");
  x[n].style.display = "block";
  // refresh gliders if relevant
  var gliders = x[n].getElementsByClassName('glider');
  for (i=0; i<gliders.length; i++) {
    Glider(gliders[i]).refresh();
  }
  // get element to focus on
  var field = x[n].querySelector("input[type='text']");
  if (field==null) {
    var field = x[n].querySelector("input[type='number']");
  }
  if (field==null) {
    var field = x[n].getElementsByTagName('textarea')[0];
  }
  if (field==null) {
    var field = x[n].getElementsByTagName('password')[0];
  }
  if (field) {
    field.focus();
  }
  else {
    x[n].focus();
  }
  // ... and fix the Previous/Next buttons:
  if (x[n].id=='start_segment' || x[n].id=='end_segment') {
    document.getElementById("prevBtn").style.display = "none";
    document.getElementById("nextBtn").style.display = "none";
  }
  else if (n==0) {
    document.getElementById("prevBtn").style.display = "none";
  }
  else {
    document.getElementById("prevBtn").style.display = "inline";
    document.getElementById("nextBtn").style.display = "inline";
  }
  // if (n == (x.length - 1)) {
  //   document.getElementById("nextBtn").innerHTML = "Submit";
  // } else {
  //   document.getElementById("nextBtn").innerHTML = "Next";
  // }
}

function nextPrev(n, validate=true) {
  // This function will figure out which tab to display
  var x = document.getElementsByClassName("formtab");
  // Exit the function if any field in the current tab is invalid:
  if (n == 1 && validate && !validateForm()) return false;
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

    return false;
  }
  // Otherwise, display the correct tab:
  if (x[currentTab].classList.contains('hidden')==true) {
    if (n<0) {
      nextPrev(-1);
    }
    else if (n>0) {
      nextPrev(1, validate=false);
    }
    else {
      showTab(currentTab);
    }
  }
  else {
    showTab(currentTab);
  }
}

function validateForm() {
    // This function deals with validation of the form fields
    var x, y, i, valid = true;
    x = document.getElementsByClassName("formtab");
    tab = x[currentTab];
    type = tab.getAttribute('data-field-type');
    optional = Boolean(tab.getAttribute('data-field-optional')=='true');
    if (optional==true) {
      return true;
    }
    else if (type=='SelectField' || type=='BooleanField') {
      if (!validate_breakpoint(x[currentTab])) {
        errorbox = tab.getElementsByClassName('errorbox')[0];
        errorbox.innerHTML = 'Please select one.';
        return false
      }
      return true
    }
    else if (type=='StringField') {
      input = tab.getElementsByTagName('input')[0];
      var val = input.value;
      var min = Number(input['min']);
      var max = Number(input['max']);
      if (validate_string_field(val, min, max)==false) {
        errorbox = tab.getElementsByClassName('errorbox')[0];
        errorbox.innerHTML = 'Response must be between ' + min + ' and ' + max + ' characters long.';
        return false
      }
      return true
    }
    else if (type=='TextAreaField') {
      input = tab.getElementsByTagName('textarea')[0];
      var val = input.value;
      var min = 0; // NOTE: Number(input.minLength) defaults to -1 but if you want a minlength in future implement some logic to avoid this
      var max = Number(input.maxLength);
      if (!validate_string_field(val, min, max)) {
        errorbox = tab.getElementsByClassName('errorbox')[0];
        errorbox.innerHTML = 'Response must be between ' + min + ' and ' + max + ' characters long.';
        return false
      }
      return true
    }
    else if (type=='IntegerField') {
      input = tab.querySelector('input.select-clean');
      var val = Number(input.value);
      var min = Number(input['min']);
      var max = Number(input['max']);
      if (!validate_slide_field(val, min, max)) {
        errorbox = tab.getElementsByClassName('errorbox')[0];
        errorbox.innerHTML = 'Please select a number between ' + min + ' and ' + max + '.';
        return false
      }
    }
    else if (type=='PasswordField') {
      input = tab.getElementsByTagName('input')[0];
      var val = input.value;
      var min = Number(input['min']);
      var max = Number(input['max']);
      if (validate_string_field(val, min, max)==false) {
        errorbox = tab.getElementsByClassName('errorbox')[0];
        errorbox.innerHTML = 'Response must be between ' + min + ' and ' + max + ' characters long.';
        return false
      }
      return true
    }
    else {
      return true;
    }
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

// FORM SUBMIT
function submit_form(id, url) {
  $.ajax({
    type: "POST",
    url: url,
    data: $('#' + id).serialize(), // serializes the form's elements.
    success: function(data) {
      if (data['path']!=undefined) {
        window.location.href = data['path'];
      } else {
        alert(data['errors']);
      }
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

function set_type(type) {
  var elts = document.getElementsByClassName('project_type');
  for (i=0; i<elts.length; i++) {
    elts[i].innerHTML = type;
  }
}

function hide_class(cls) {
  document.querySelectorAll('.' + cls).forEach(function(el) {
    el.classList.add('hidden');
  });
}

function show_class(cls) {
  document.querySelectorAll('.' + cls).forEach(function(el) {
    el.classList.remove('hidden');
  });
}

// field validators
function validate_breakpoint(field) {
  var box = field.getElementsByClassName('input-control')[0];
  any_checked = false;
  box.querySelectorAll('input').forEach(function(el) {
    if (el.checked) {
      any_checked = true;
    }
  });
  return any_checked
}

function validate_string_field(val, min, max) {
  len = val.length;
  return (len>min && len<=max)
}

function validate_slide_field(val, min, max) {
  return (val>=min && val<=max)
}
