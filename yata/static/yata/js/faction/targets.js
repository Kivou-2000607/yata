// refresh target from target list by clicking on the row
$(document).on("click", "tr[id^='target-list-refresh-'] > td:not(.dont-touch-me)", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("tr");
    // const targetId = reload.attr("id").split("-").pop();
    reload.removeClass("old-refresh");
    reload.load("/faction/target/", {
        targetId: reload.attr("data-val"),
        type: "update",
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
    reload.html(`<td colspan="8" style="text-align: center;">${spinner}</td>`);
});

// delete target from target list button
$(document).on("click", "a.target-list-delete", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("tr");
    reload.load( "/faction/target/", {
        targetId: reload.attr("data-val"),
        type: "delete",
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
    reload.remove();
});

// refresh timer target update
window.setInterval(() => {
    $(".update-timer").each((i, e) => {
        const tr = $(e).closest("tr");
        const status = tr.find(".status");

        const tsRefresh = parseInt($.trim($(e).attr("data-val")));
        const tsStatus = parseInt($.trim(status.attr("data-val")));
        const tsNow = parseInt(Date.now() / 1000);

        // transform notations if > 2 hours
        if (tsNow - tsRefresh > 7200) {
            $(e).html("> 2 hrs");
            tr.addClass("old-refresh");
            $(e).removeClass("need-refresh");
            status.removeClass("need-refresh");
        } else {
            // add/remove flash if tsStatus < tsRefresh
            if (tsStatus && tsRefresh) {
                let statusStr;
                if (tsStatus < tsNow) {
                    statusStr = "Out since " + fancyTimeFormat(tsNow - tsStatus) + " s";
                    status.addClass("need-refresh");
                    $(e.target).addClass("need-refresh");
                } else {
                    status.removeClass("need-refresh");
                    $(e).removeClass("need-refresh");
                    statusStr = status.text().substring(0, 6);
                    statusStr += fancyTimeFormat(tsStatus - tsNow);
                }
                // update hosp time
                status.html(statusStr);
            }
            $(e).html(fancyTimeFormat(tsNow - tsRefresh));
        }
    });
}, 1000);
