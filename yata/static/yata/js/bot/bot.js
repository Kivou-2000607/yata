// update discord id
$(document).on('click', '#discord-update-id', function(e){
    e.preventDefault();
    var reload = $("#discord-id");
    reload.load( "/bot/updateId/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    });
    reload.html(spinner);
});

// toggle notifications
$(document).on('click', "div.api-notifications", function(e){
    e.preventDefault();
    var reload = $(this);
    reload.load( "/bot/toggleNoti/", {
        type: $(this).attr("data-val"),
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }).html(''+spinner+'');
});

$(document).ready(function() {
  var hash = window.top.location.hash.substr(1);
  if(hash) {
    var h3 = $("#"+hash);
    toggle_h(h3);
  }
});
