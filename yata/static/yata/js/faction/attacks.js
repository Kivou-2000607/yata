$(document).on("change", "#date-live-attacks", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start").val());
    const live = $(e.currentTarget).prop("checked");
    if (live) {
        $("#date-end").removeClass("is-valid").removeClass("is-invalid").attr("disabled", true).val("");
        if (start) $("#create-report-attacks").show();
        else $("#create-report-attacks").hide();
    } else {
        $("#date-end").addClass("is-invalid").attr("disabled", false).focus();
        $("#create-report-attacks").hide();
    }
});

// create report
$(document).on("click", "#create-report-attacks", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start").val());
    let end = parseInt($("#ts-end").val());
	let live;
    if ($("#date-live-attacks").prop("checked")) {
        live = 1;
        end = 0;
    } else live = 0;
    $(e.currentTarget).html(spinner);
    $("#content-update").load("/faction/attacks/", {
        start, end, live, type: "new",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Creating report");
});

// delete report
$(document).on("click", ".faction-attacks-reports-delete", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    $(e.currentTarget).closest("tr").load("/faction/attacks/manage/", {
        type:"delete", reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// see report
$(document).on("click", ".faction-attacks-reports-see", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    $("#content-update").load(`/faction/attacks/${reportId}`, {
        reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(`/faction/attacks/${reportId}`));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Loading report");
    $("div.error").hide();
});


// show hide
$(document).on("click", ".faction-attacks-report-toggle", e => {
    e.preventDefault();
    const splt = e.currentTarget.id.split("-");
    const factionId = $(e.currentTarget).attr("data-val");
    const page = splt.pop();
    const reportId = splt.pop();
    $("#content-update").load(`/faction/attacks/${reportId}`, {
        reportId, factionId, type: "faction_filter", page,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Reload report");
});

// show hide
$(document).on("click", "a#faction-attacks-report-members", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    $(e.currentTarget).closest("p").load(`/faction/attacks/members/${reportId}`, {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// from when reports were filled by the user
// $(document).on('click', '#faction-attacks-report-update', e=>{
//     e.preventDefault();
//     var reportId = $(e.currentTarget).attr("data-val");
//     $( "#content-update" ).load( "/faction/attacks/" + reportId, {
//         reportId: reportId, update: true,
//         csrfmiddlewaretoken: getCookie("csrftoken")
//     });
//     $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Synchronizing report');
// });

// player filter
$(document).on("click", "table.faction-attacks-list i.filter-player, table.faction-attacks-list i.filter-player-activated", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).attr("data-val").split("-");
    const reportId = splt[0];
    const playerId = splt[1];
    const reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load( "/faction/attacks/list/" + reportId, {
        playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html(`<td>${spinner}</td>`);
});

$(document).on("change", "select.faction-attack-header-filter", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).val().split("-");
    const reportId = splt[0];
    const playerId = splt[1];
    const reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load(`/faction/attacks/list/${reportId}`, {
        playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html(`<td>${spinner}</td>`);
});
