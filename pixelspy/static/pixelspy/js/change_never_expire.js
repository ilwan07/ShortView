var days_input = document.getElementById("days");
var hours_input = document.getElementById("hours");
var minutes_input = document.getElementById("minutes");
var seconds_input = document.getElementById("seconds");
var never_expire_input = document.getElementById("never_expire");

function change_never_expire() {
    if (never_expire_input.checked) {
        days_input.setAttribute("disabled", "disabled");
        hours_input.setAttribute("disabled", "disabled");
        minutes_input.setAttribute("disabled", "disabled");
        seconds_input.setAttribute("disabled", "disabled");
    }
    else {
        days_input.removeAttribute("disabled");
        hours_input.removeAttribute("disabled");
        minutes_input.removeAttribute("disabled");
        seconds_input.removeAttribute("disabled");
    }
}
