$(document).on('click', '#yata-login-submit', function(e){
    e.preventDefault();
    $("#header").load( "/login", {
        key: $("#yata-login-key").val(),
        csrfmiddlewaretoken:  getCookie("csrftoken"),
    });
    $(this).html(spinner);
});

$(document).on('click', '#yata-logout-submit', function(e){
    $(this).html(spinner);
});

$(document).on('click', '#yata-delete-submit', function(e){
    var r = confirm("Are you sure you want to delete your account? All data will be removed from the database.");
    if (r == false) {
        e.preventDefault();
    }
});
