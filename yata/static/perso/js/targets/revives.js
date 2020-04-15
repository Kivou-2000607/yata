// toggle revive from revives list button
$(document).on('click', 'a[id^="revives-list-toggle-"]', function(e){
    e.preventDefault();
    var reload = $(this).closest("td");
    var reviveId = $(this).attr("id").split("-").pop();
    reload.load( "/target/revive/", {
        reviveId: reviveId,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<i class="fas fa-spinner fa-pulse"></i>');
});
