var form = document.getElementById("form_to_submit")
var modified = false;

function modify() {
    modified = true;
}

// disable the exit warning if the form is valid
if (form) {
    form.addEventListener("submit", function(e) {
        modified = false;
    });
}

// warn the user before leaving the page if he started filling some data
window.addEventListener("beforeunload", function(e) {
    if (modified) {
        e.preventDefault();
        return "";
    }
});
