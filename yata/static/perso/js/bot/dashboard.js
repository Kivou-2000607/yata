$(document).on('click', '.dashboard-option', e=>{
    e.preventDefault();
    const target = $(e.currentTarget)
    target.closest("div.module-doc").load( "/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on('click', '.dashboard-option-tr', e=>{
    e.preventDefault();
    const target = $(e.currentTarget)
    target.closest("tr").load( "/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});


// $(document).on('change', 'select.dashboard-list', e=>{
//     e.preventDefault();
//     const target = $(e.currentTarget)
//     let splt = target.val().split("-");
//     target.closest("div.module-doc").load( "/bot/dashboard/option/", {
//         mod: target.attr("data-mod"),
//         typ: target.attr("data-typ"),
//         sid: target.attr("data-sid"),
//         did: splt.pop(),
//         nam: splt.pop(),
//         csrfmiddlewaretoken: getCookie("csrftoken")
//     }).html(spinner);
// });
