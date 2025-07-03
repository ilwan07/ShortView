var modified = false;

function modify() {
    modified = true;
}

function let_confirm() {
    modified = false;
}

// warn the user before leaving the page if he started filling some data
window.addEventListener("beforeunload", function(e) {
    if (modified) {
        e.preventDefault();
        return "";
    }
});
