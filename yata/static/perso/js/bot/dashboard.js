$(document).on('click', '.dashboard-option', e=>{
    e.preventDefault();
    const target = $(e.currentTarget)
    target.closest("div.module-doc").load( "/bot/dashboard/option/", {
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),
        did: target.attr("data-did"),
        nam: target.attr("data-nam"),
        sid: target.attr("data-sid"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
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
