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

$(document).on('click', '.dashboard-option-li', e=>{
    e.preventDefault();
    const target = $(e.currentTarget).closest("li");
    console.log(target);
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

$(document).on('click', '.dashboard-option-af', e=>{
    e.preventDefault();
    const target = $(e.currentTarget);
    const id = $(target).parents("li.step-2").siblings("li.step-1").children("input.faction-add-id").val()
    if(!$.isNumeric(id)) { console.log("faction id is not numeric:", id); return }

    target.closest("div.module-doc").load( "/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),
        fid: id,

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on('change', 'input.faction-add-id', e=>{
    e.preventDefault();
    const target = $(e.currentTarget);
    if($.isNumeric($(target).val())) {
        $(target).parents("li.step-1").siblings("li.step-2").slideDown("fast");
    }
});
