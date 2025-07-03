var copy_button = document.getElementById("copylink")
var copy_confirm = document.getElementById("copyconfirm");
function copy_link() {
    navigator.clipboard.writeText(copy_button.innerText);
    copy_confirm.innerHTML = "Link copied!";
    setTimeout(() => { copy_confirm.innerHTML = ""; }, 2000);
}
