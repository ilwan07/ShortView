var delete_expired_input = document.getElementById("delete_expired");
var hide_expired_input = document.getElementById("hide_expired");

function change_delete_expired() {
    if (delete_expired_input.checked) {
        hide_expired_input.setAttribute("disabled", "disabled");
        hide_expired_input.checked = true;
    }
    else {
        hide_expired_input.removeAttribute("disabled");
    }
}
