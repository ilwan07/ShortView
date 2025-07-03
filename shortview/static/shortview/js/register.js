var password_input = document.getElementById("password");
var password_confirm_input = document.getElementById("password_confirm");

// check if the passwords are matching
function check_match() {
    if (password_input.value !== password_confirm_input.value) {
        password_confirm_input.setCustomValidity("Passwords must match");
    }
    else {
        password_confirm_input.setCustomValidity("");
    }
}
