$(document).on('click', '#yata-login-submit', function(e){
    e.preventDefault();

    // WARNING: IT IS NOT TOLERATED TO MODIFY THIS FUNCTION
    // as it will remove the warning when users enter their API key on non official instances of YATA.
    // Changing it will be seen as making your instance of YATA looks official, thus raising suspicions.
    if (window.location.host != "yata.yt") {
      var c = confirm("This is not the official YATA website which is hosted on https://yata.yt.\nWhere it is allowed to host instances of YATA on personal servers, make sure you know who's hosting it and that they have no malicious intents.\n\nKivou [2000607]");
      if (c == false) {
          return
      }
    }

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
