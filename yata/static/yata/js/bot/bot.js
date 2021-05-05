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
