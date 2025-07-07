var copy_button = document.getElementById("copylink");
var copy_confirm = document.getElementById("copyconfirm");

function copy_link() {
    navigator.clipboard.writeText(copy_button.innerText);
    copy_confirm.innerHTML = "Link copied!";
    setTimeout(() => { copy_confirm.innerHTML = ""; }, 2000);
}

// ask confirmation to delete
var delete_form = document.getElementById("delete_form");

function delete_link() {
    var confirm_delete = confirm("Do you really want to continue?\nThis will permanently delete this link!");
    if (confirm_delete) {
        // add the post data as a confirmation by submitting the hidden form
        delete_form.submit();
    }
}

// submit form when changing notification preference
var notify_form = document.getElementById("link_notify_form");

function change_notify() {
    notify_form.submit();
}
