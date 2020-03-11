// modify upgrade tree
$(document).on('change', 'select[id^="simu-tree-"]', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).attr("id").split("-");

    var modification = splt.pop()
    var shortname = splt.pop();

    var value = $(e.currentTarget.selectedOptions).attr("value");

    $("#faction-upgrade-tree").load( "/faction/simulator/", {
        change: true,
        modification: modification,
        shortname: shortname,
        value: value,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget.parentElement).html(spinner);
});

// reset upgrade tree
$(document).on('click', '#faction-tree-reset', e=>{
    e.preventDefault();
    $("#faction-upgrade-tree").load( "/faction/simulator/", {
        reset: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

$(document).on('click', '#faction-tree-refresh', e=>{
    e.preventDefault();
    $("#faction-upgrade-tree").load( "/faction/simulator/", {
        refresh: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// show upgrades details
$(document).on('click', '.show-upgrade-details', e=>{
    e.preventDefault();
    var tr = $(e.currentTarget.parentElement.nextElementSibling);
    var upgradeId = tr.attr("id").split("-").pop();
    tr.load( "/faction/simulator/challenge/", {
        upgradeId: upgradeId,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).show().html('<td colspan="11">' + spinner + '</td>');

});

// hide upgrades details
$(document).on('click', '.upgrade-details', e=>{
    e.preventDefault();
    $(e.currentTarget).hide();
});
