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
    var reload = $(e.currentTarget);
    var threshold = reload.children("p").children("select").val();
    reload.load( "/faction/configurations/threshold/", {
        threshold: threshold,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<td colspan="3" style="text-align: center;">'+spinner+'</i></td>');
});

// poster on/off/hold
$(document).on('click', 'a[id^=faction-aa-toggle-poster]', e=>{
    e.preventDefault();
    type = e.currentTarget.id.split("-").pop();
    var reload = $(e.currentTarget).parents("div#faction-aa-poster");
    var divspinner = '<div style="text-align: center; height: '+reload.css("height")+';">'+spinner+'</div>'
    reload.load( "/faction/configurations/poster/", {
        type: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(divspinner);
});

// parameters
$(document).on('change', '[id^="faction-poster-"]', e=>{
    e.preventDefault();
    var v = $(e.currentTarget).val();
    var id = $(e.currentTarget).attr("id").split("-");
    var p = id.pop();
    var t = id.pop();
    var reload = $(e.currentTarget).parents("div#faction-aa-poster");
    var divspinner = '<div style="text-align: center; height: '+reload.css("height")+';">'+spinner+'</div>'
    reload.load( "/faction/configurations/poster/", {
        posterConf: 1, t: t, p: p, v: v,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(divspinner);
});

// events delete
$(document).on('click', 'a.faction-event-delete', e=>{
    e.preventDefault();
    $(e.currentTarget).closest("tr").load( "/faction/configurations/event/", {
        type: "delete",
        eventId: $(e.currentTarget).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// events create
$(document).on('click', 'input#faction-event-create', e=>{
    e.preventDefault();
    var form = $(e.currentTarget).closest("form");
    var stack = 0;
    if(form.find("#event-stack").prop('checked')) stack = 1
    var reset = 0;
    if(form.find("#event-reset").prop('checked')) reset = 1
    $(e.currentTarget).closest("div.module").load( "/faction/configurations/event/", {
        type: "create",
        title: form.find("#event-title").val(),
        description: form.find("#event-description").val(),
        ts: form.find("#event-ts").val(),
        stack: stack,
        reset: reset,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});
