/*<![CDATA[*/
function searchsubmit(){
  document.getElementById('searchbar').submit();
}
/*]]>*/
function refresh(){
  var i = 1, re = "";
  while(doc = document.getElementById('f'+i.toString())) {
    var rads = doc.elements['prefs'];
      for(var j = 0; j < rads.length; j++) {
         //console.log(rads[j].value.toString())
         if(rads[j].checked && rads[j].value.toString() != "0") {
         //if(rads[j].checked) {
           // use database ID for read implementation
           re += '\''+doc.elements['dname'].value.toString()+'\':\''+rads[j].value.toString()+'\',';
         }
      }
    i++;
  }
  console.log('Hello Mike');
  console.log('Current Info: '+re.toString());

  document.getElementById('rank_info').value = re;
  document.getElementById('is_tmp').value = false;
  document.getElementById('rankinfo').submit();
}

function tmp_refresh(){
  var i = 1, re = "";
  while(doc = document.getElementById('f'+i.toString())) {
    var rads = doc.elements['prefs'];
      for(var j = 0; j < rads.length; j++) {
         if(rads[j].checked && rads[j].value.toString() != "0") {
           // use database ID for read implementation
           re += '\''+doc.elements['dname'].value.toString()+'\':\''+rads[j].value.toString()+'\',';
         }
      }
    i++;
  }
  console.log('Aloha Mike');
  console.log('Current Info: '+re.toString());

  document.getElementById('rank_info').value = re;
  document.getElementById('is_tmp').value = true;
  document.getElementById('rankinfo').submit();
}

function mdown(radio) {
  console.log('mdown');
  console.log(radio.checked);
  radio.checked = !radio.checked;
  console.log(radio.checked);
}

function elementInDocument(id) {
  element = document.getElementById(id)
  while (element = element.parentNode) {
      if (element == document) {
          return true;
      }
  }
  return false;
}

function essential(){
  // if (elementInDocument("next")) {
  //   document.getElementById("next").addEventListener("click", tmp_refresh());
  // }

  // if (elementInDocument("previous")) {
  //   document.getElementById("previous").addEventListener("click", tmp_refresh());
  // }
  console.log("Events Assigned");
}

function login(){
  document.getElementById('login_name').value = document.getElementById('username').value;
  document.getElementById('login_passw').value = document.getElementById('password').value;
  document.getElementById('login_form').submit();
  console.log("logged in");
}
function register(){
  if (document.getElementById('email').disabled == false) {
    document.getElementById('reg_name').value = document.getElementById('username').value;
    document.getElementById('reg_passw').value = document.getElementById('password').value;
    document.getElementById('reg_email').value = document.getElementById('email').value;
    document.getElementById('user_form').submit();
  }
  else {
    document.getElementById('email').type = "email";
    document.getElementById('email').disabled = false;
  }
  console.log("registed!");
}
