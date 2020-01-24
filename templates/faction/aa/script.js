// toggle key
$(document).on('click', '.faction-aa-toggle-key', e=>{
    e.preventDefault();
    $(e.currentTarget).parents("tr").load( "/faction/configurationsKey/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="3" style="text-align: center;">'+spinner+'</td>');
});


// threshold
$(document).on('change', '#faction-aa-change-threshold', e=>{
    e.preventDefault();
    console.log("coucou");
    var reload = $(e.currentTarget);
    var threshold = reload.children("p").children("select").val();
    reload.load( "/faction/configurationsThreshold/", {
        threshold: threshold,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html('<td colspan="3" style="text-align: center;"><i class="fas fa-spinner fa-pulse"></i></td>');
});

// poster
$(document).on('click', 'a[id^=chain-aa-toggle-poster]', e=>{
    e.preventDefault();
    type = e.currentTarget.id.split("-").pop();
    $(e.currentTarget).parents("form").load( "/faction/configurationsPoster/", {
        type: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="3" style="text-align: center;">'+spinner+'</td>');
});
