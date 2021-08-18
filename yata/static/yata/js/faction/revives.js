$(document).on("change", "#date-live-revives", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start-revives").val());
    const live = $(e.currentTarget).prop("checked");
    if (live) {
        $("#date-end-revives").removeClass("is-valid").removeClass("is-invalid").attr("disabled", true).val("");
        if (start) $("#create-report-revives").show();
        else $("#create-report-revives").hide();
    } else {
        $("#date-end-revives").addClass("is-invalid").attr("disabled", false).focus();
        $("#create-report-revives").hide();
    }
});

// create report
$(document).on("click", "#create-report-revives", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start-revives").val());
    let end = parseInt($("#ts-end-revives").val());
	let live;
    if ($("#date-live-revives").prop("checked")) {
        live = 1;
        end = 0;
    } else live = 0;
    $("#content-update").load("/faction/revives/", {
        start, end, live, type: "new",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Creating report");
});

// delete report
$(document).on("click", ".faction-revives-reports-delete", e => {
    e.preventDefault();
    $(e.currentTarget).closest("tr").load("/faction/revives/manage/", {
        type: "delete",
		reportId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// see report
$(document).on("click", ".faction-revives-reports-see", e => {
    e.preventDefault();
    var reportId = $(e.currentTarget).attr("data-val");
    $("#content-update").load(`/faction/revives/${reportId}`, {
        reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(`/faction/revives/${reportId}`));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Loading report");
    $("div.error").hide();
});

// show hide
$(document).on("click", ".faction-revives-report-toggle", e => {
    e.preventDefault();
    const splt = e.currentTarget.id.split("-");
    const factionId = $(e.currentTarget).attr("data-val");
    const order = splt.pop();
    const page = splt.pop();
    const reportId = splt.pop();
    $("#content-update").load(`/faction/revives/${reportId}`, {
        reportId, factionId, type: "toggle", o_pl: order, page,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Reload report");
});

// filters
$(document).on("click", "span[id^='faction-revives-report-']", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    const type = e.currentTarget.id.split("-").pop();
    $("#content-update").load(`/faction/revives/${reportId}`, {
        reportId, type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Recompute report");
});
$(document).on("change", "input[id^='faction-revives-report-']", e => {
    e.preventDefault();
    console.log(e.currentTarget);
    const reportId = $(e.currentTarget).attr("data-val");
    const type = e.currentTarget.id.split("-").pop();
    const value = $(e.currentTarget).val();
    console.log(value);
    $("#content-update").load(`/faction/revives/${reportId}`, {
        reportId, type, value,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Recompute report");
});

$(document).on("click", "table.faction-revives-list i.filter-player, table.faction-revives-list i.filter-player-activated", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).attr("data-val").split("-");
    const reportId = splt[0];
    const playerId = splt[1];
    const reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load(`/faction/revives/list/${reportId}`, {
        playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html(`<td>${spinner}</td>`);
});

$(document).on("change", "select.faction-revive-header-filter", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).val().split("-");
    const reportId = splt[0];
    const playerId = splt[1];
    const reload = $(e.currentTarget).closest("div.pagination-list");
    reload.load(`/faction/revives/list/${reportId}`, {
        playerId, type: "filter",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).closest("table").find("tr").html(`<td>${spinner}</td>`);
});
