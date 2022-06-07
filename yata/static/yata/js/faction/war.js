// refresh all targets with faction data
$(document).on("click", "#faction-targets-refresh", e => {
    e.preventDefault();
    $("#war-targets").load("/faction/war/targets/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
});

// refresh target from target list by clicking on the row
$(document).on("click", "tr[class='faction-targets-refresh'] > td:not(.dont-touch-me)", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("tr");
    reload.removeClass("old-refresh");
    reload.load("/faction/war/target/", {
        targetId: reload.attr("data-val"),
        type: "update",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html(`<td colspan="13" class="text-center">${spinner}</td>`);
});

// call dibs
$(document).on("click", "a.dibs", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("td");
    reload.load("/faction/war/target/", {
        targetId: reload.attr("data-val"),
        type: 'dibs',
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});
