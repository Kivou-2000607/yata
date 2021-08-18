$(document).on("click", ".dashboard-option", e => {
    e.preventDefault();
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget);
    target.closest("div.module-doc").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("click", ".dashboard-option-tr", e => {
    e.preventDefault();
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget);
    target.closest("tr").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("click", ".dashboard-option-li", e => {
    e.preventDefault();
    console.log("triggers dashboard-option-li");
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget).closest("li");
    target.closest("div.module-doc").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("click", ".dashboard-option-span", e => {
    e.preventDefault();
    console.log("triggers dashboard-option-span");
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget).closest("span");
    target.closest("div.module-doc").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        sub: target.attr("data-sub"),
        val: target.attr("data-val"),

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("click", ".dashboard-option-af", e => {
    e.preventDefault();
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget);
    const id = $(target).parents("li.step-2").siblings("li.step-1").children("input.faction-add-id").val();
    if (!$.isNumeric(id)) { console.log("faction id is not numeric:", id); return; }

    target.closest("div.module-doc").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.attr("data-val"),
        fid: id,

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("change", "input.faction-add-id", e => {
    e.preventDefault();
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget);
    const fid = $(target).val();
    const step_2 = $(target).parents("li.step-1").siblings("li.step-2");
    if ($.isNumeric(fid)) {
        $(step_2).slideDown("fast");
        const all_li = $(step_2).children("ul").children("li");
        $(all_li).children("span").removeClass("selected").addClass("unselected");
        $(all_li).children("tt").removeClass("valid");
        $(all_li).each((i, li) => {
            $(li).children("tt.dashboard-settings").each((j, tt) => {
                if(fid == $(tt).attr("data-fid")) {
                    $(li).children("span.unselected").removeClass("unselected").addClass("selected");
                    $(tt).addClass("valid");
                }
            });
        });
    }
});

$(document).on("change", "input.new-message", e => {
    e.preventDefault();
    if ($("#dashboard-readonly").length) return;

    const target = $(e.currentTarget);
    target.closest("div.module-doc").load("/bot/dashboard/option/", {

        // bot /server / module / type (select the section in the configuration)
        bid: target.attr("data-bid"),
        sid: target.attr("data-sid"),
        mod: target.attr("data-mod"),
        typ: target.attr("data-typ"),

        // couple key / value
        key: target.attr("data-key"),
        val: target.val(),

        // ux enhancement
        ux: target.attr("data-ux"),

        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    target.html(spinner);
});

$(document).on("click", "span.dashboard-option-modify-positions", e => {
    e.preventDefault();
    $(e.currentTarget).parent("li").find("div.to-hide").toggle(100);
});
