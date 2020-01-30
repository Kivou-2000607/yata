// toggle key
$(document).on('click', '.faction-aa-toggle-key', e=>{
    e.preventDefault();
    $(e.currentTarget).parents("td").load( "/faction/configurations/key/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});


// threshold
$(document).on('change', '#faction-aa-change-threshold', e=>{
    e.preventDefault();
    console.log("coucou");
    var reload = $(e.currentTarget);
    var threshold = reload.children("p").children("select").val();
    reload.load( "/faction/configurations/threshold/", {
        threshold: threshold,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<td colspan="3" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
});

// poster on/off/hold
$(document).on('click', 'a[id^=faction-aa-toggle-poster]', e=>{
    e.preventDefault();
    type = e.currentTarget.id.split("-").pop();
    $(e.currentTarget).parents("div#faction-poster-main").load( "/faction/configurations/poster/", {
        type: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<p>'+spinner+'</p>');
});

// parameters
$(document).on('change', '[id^="faction-poster-"]', e=>{
    e.preventDefault();
    var v = $(e.currentTarget).val();
    var id = $(e.currentTarget).attr("id").split("-");
    var p = id.pop();
    var t = id.pop();
    $(e.currentTarget).parents("div#faction-poster-main").load( "/faction/configurations/poster/", {
        posterConf: 1, t: t, p: p, v: v,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<p>'+spinner+'</p>');
});
