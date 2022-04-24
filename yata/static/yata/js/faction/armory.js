// drop down armory record
$(document).on("click", ".faction-armory-toggle-view", e => {
    e.preventDefault();
    $(e.currentTarget).next("table").slideToggle("fast", () => {
        $(e.currentTarget).find("i.fa-caret-right").toggleClass("fa-rotate-90");
    });
});

// show/hide breakdown
$(document).on("click", "h1.faction-armory-type", (e) => {
    e.preventDefault();
    const h = $(e.target);
    const d = h.next("div");
    const i = h.find("i[class^='fas fa-caret']");
    d.slideToggle("fast", () => {
        if (d.css("display") === "none") i.removeClass("fa-rotate-90");
        else i.addClass("fa-rotate-90");
    });
});

// // filter by member
// $(document).on('click', 'form.news > i.filter-player,form.news > i.filter-player-activated', e=>{
//     e.preventDefault();
//     console.log("news")
//     var member = $(e.currentTarget).attr("data-val");
//     var start = $(e.currentTarget).attr("data-start");
//     var end = $(e.currentTarget).attr("data-end");
//     var reload = $(e.currentTarget).closest("div.pagination-list");
//     reload.load( "/faction/armory/news/", {
//         member: member, type: "filter", start: start, end: end,
//         csrfmiddlewaretoken: getCookie("csrftoken")
//     });
//     $(e.currentTarget).closest("table").find("tr").html('<td>'+spinner+'</td>');
// });
//
// $(document).on('change', 'select.faction-armory-header-filter', e=>{
//     e.preventDefault();
//     $("#content-update").load( "/faction/armory/", {
//         member: $(e.currentTarget).val(), type: "filter",
//         csrfmiddlewaretoken: getCookie("csrftoken")
//     });
//     $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Filtering armory');
// });
//
// $(document).on('click', '#faction-armory-reset-filters', e=>{
//     e.preventDefault();
//     $("#content-update").load( "/faction/armory/", {
//         resetFilters: 1,
//         csrfmiddlewaretoken: getCookie("csrftoken")
//     });
//     $("#content-update h2").addClass("grey").html(spinner + '&nbsp;&nbsp;Reset armory filters');
// });

// make live
$(document).on("change", "#date-live-armory", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start-armory").val());
    const live = $(e.currentTarget).prop("checked");
    if (live) {
        $("#date-end-armory").removeClass("is-valid").removeClass("is-invalid").attr("disabled", true).val("");
        if (start) $("#create-report-armory").show();
		else $("#create-report-armory").hide();
    } else {
        $("#date-end-armory").addClass("is-invalid").attr("disabled", false).focus();
        $("#create-report-armory").hide();
    }
});

// create report
$(document).on("click", "#create-report-armory", e => {
    e.preventDefault();
    const start = parseInt($("#ts-start-armory").val());
    let end = parseInt($("#ts-end-armory").val());
    let live;
    if ($("#date-live-armory").prop("checked")) {
        live = 1;
        end = 0;
    } else live = 0;
    $("#content-update").load("/faction/armory/", {
        start, end, live, type: "new",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Creating report");
});

// delete report
$(document).on("click", ".faction-armory-reports-delete", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    $(e.currentTarget).closest("tr").load("/faction/armory/", {
        type:"delete", reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});
