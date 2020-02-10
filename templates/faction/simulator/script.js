// modify upgrade tree
$(document).on('change', 'select[id^="simu-tree-"]', e=>{
    e.preventDefault();
    var splt = $(e.currentTarget).attr("id").split("-");

    var modification = splt.pop()
    var shortname = splt.pop();

    var value = $(e.currentTarget.selectedOptions).attr("value");

    console.log(modification, shortname, value)

    $("#faction-upgrade-tree").load( "/faction/simulator/", {
        change: true,
        modification: modification,
        shortname: shortname,
        value: value,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
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

// // show/hide upgrades details
// $(document).on('click', '.show-upgrade-details', e=>{
//     e.preventDefault();
//     $(e.currentTarget.parentElement.nextElementSibling).slideToggle();
// });
