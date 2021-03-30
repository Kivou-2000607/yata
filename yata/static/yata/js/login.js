$(document).on('click', '#yata-login-submit', function(e){
    e.preventDefault();
    var reload = $("#yata-login");
    $( "#yata-login" ).load( "/login", {
        key: $("#yata-login-key").val(),
        check: $("#yata-login-remember").is(':checked'),
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.find("td.d").html('<span class="login-message"><i class="fas fa-spinner fa-pulse"></i>&nbsp;&nbsp;Connecting to API (1 API call)</span>');
});

$(document).on('click', '#yata-delete-submit', function(e){
    var r = confirm("Are you sure you want to delete your account? All data will be removed from the database.");
    if (r == false) {
        e.preventDefault();
    }
});

// $(document).ready(function(){
//     $("#badges").load("badges");
// });
