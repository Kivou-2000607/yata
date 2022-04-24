// refresh member from member list by clicking on the row
$(document).on("click", "tr.faction-member-refresh > td:not(.dont-touch-me)", (e) => {
    e.preventDefault();
    const reload = $(e.target).closest("tr");
    const memberId = reload.attr("data-val");
    reload.load("/faction/members/update/", {
        memberId,
        csrfmiddlewaretoken: getCookie("csrftoken")
	}).html(`<td colspan="11" style="text-align: center;">${spinner}</td>`);
});

// toggle member shareE
$(document).on("click", ".faction-member-shareE", e => {
    e.preventDefault();
    $(e.currentTarget.offsetParent).load("/faction/members/toggle/", {
        type: "energy",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// toggle member shareS
$(document).on("click", ".faction-member-shareS", e => {
    e.preventDefault();
    $(e.currentTarget.offsetParent).load("/faction/members/toggle/", {
        type: "stats",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// toggle member shareN
$(document).on("click", ".faction-member-shareN", e => {
    e.preventDefault();
    $(e.currentTarget.offsetParent).load("/faction/members/toggle/", {
        type: "nerve",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// refresh all members from member list by clicking on title refresh button
$(document).on("click", "#member-refresh", e => {
    e.preventDefault();
    $("#faction-members").find("tr.faction-member-refresh-private").each((i, e) => {
        const reload = $(e);
        const memberId = reload.attr("data-val");
        let wait = 0;
        if (i) wait = 1000;
        ((index) => {
            setTimeout(() => {
                reload.load("/faction/members/update/", {
                    memberId,
                    csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
				}).html(`<td colspan="11" style="text-align: center;">${spinner}</td>`);
            }, wait);
        })(i);
    });
});
