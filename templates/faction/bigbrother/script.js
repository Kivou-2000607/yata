
// big brother
$(document).on('change', '.faction-bb-stats-list', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).val().split("-");
    console.log(splt);
    if(splt.length == 2) {
        var tsB = 0;
        var tsA = splt.pop();
        var type = splt.pop();
    } else if (splt.length == 3) {
        var tsB = splt.pop();
        var tsA = splt.pop();
        var type = splt.pop();
    }

    $("#faction-big-brother-table").load( "/faction/bigbrother/", {
        tsA: tsA,
        tsB: tsB,
        name: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// big brother add
$(document).on('change', '.faction-bb-enter-challenge', e=>{
    e.preventDefault();
    var add = $(e.currentTarget).val();
    $("#content-update").load( "/faction/bigbrother/", {
        add: add,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Adding challenge '+add);


});

// big brother remove
$(document).on('click', '.faction-bb-delete', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).attr("data-val").split("-");
    var tr = $(e.currentTarget).parents("tr");

    tr.load( "/faction/bigbrother/remove/", {
        ts: splt.pop(),
        name: splt.pop(),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();

});
