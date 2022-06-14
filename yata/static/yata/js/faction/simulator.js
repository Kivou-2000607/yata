// modify upgrade tree
$(document).on("change", "select[id^='simu-tree-']", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).attr("id").split("-");

    const modification = splt.pop();
    const shortname = splt.pop();

    const value = e.currentTarget.value;

    $("#faction-upgrade-tree").load("/faction/simulator/", {
        change: true, modification, shortname, value,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget.parentElement).html(spinner);
});

// reset upgrade tree
$(document).on("click", "#faction-tree-reset", e => {
    e.preventDefault();
    $("#faction-upgrade-tree").load("/faction/simulator/", {
        reset: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

$(document).on("click", "#faction-tree-refresh", e => {
    e.preventDefault();
    $("#faction-upgrade-tree").load("/faction/simulator/", {
        refresh: true,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// show upgrades details
$(document).on("click", ".show-upgrade-details", e => {
    e.preventDefault();
    const tr = $(e.currentTarget.parentElement.nextElementSibling);
    const upgradeId = tr.attr("id").split("-").pop();
    tr.load("/faction/simulator/challenge/", {
        upgradeId,
        csrfmiddlewaretoken: getCookie("csrftoken")
	}).show().html(`<td colspan="11">${spinner}</td>`);

});

// hide upgrades details
$(document).on("click", ".upgrade-details", e => {
    e.preventDefault();
    $(e.currentTarget).hide();
});


// select branch
$(document).on("click", "a.faction-simu-select", e => {
    e.preventDefault();
    const selectTree = $(e.currentTarget).attr("data-val");
    console.log(selectTree);
    $("#content-update").load("/faction/simulator/", {
        selectTree: selectTree,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Creating report");
});
