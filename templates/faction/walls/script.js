// delete wall
$(document).on('click', '.wall-delete', function(e){
    e.preventDefault();
    var wallId = $(e.currentTarget).closest("td").attr("data-val");
    $(e.currentTarget).closest("tr").load( "/faction/walls/manage/", {
        type:"delete", wallId: wallId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// toggle wall from list
$(document).on('click', '.wall-toggle', e=>{
    e.preventDefault();
    var td = $(e.currentTarget).closest("td");
    var wallId = td.attr("data-val");
    td.load( "/faction/walls/manage/", {
        type:"toggle", wallId: wallId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});
