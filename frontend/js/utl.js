// UI helper: toggle password visibility on the login and registration forms.
function showPw() {
  var x = document.getElementById("inputPassword3");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}
