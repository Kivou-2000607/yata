// delete wall
$(document).on("click", ".wall-delete", e => {
    e.preventDefault();
    $(e.currentTarget).closest("tr").load("/faction/walls/manage/", {
        type:"delete", wallId: $(e.currentTarget).closest("td").attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// toggle wall from list
$(document).on("click", ".wall-toggle", e => {
    e.preventDefault();
    const td = $(e.currentTarget).closest("td");
    if (e.ctrlKey) {
        $(`td.buttons[data-fac="${td.attr("data-fac")}"]`).each((index, item) => {
            $(item).load("/faction/walls/manage/", {
                type: "toggle", wallId: $(item).attr("data-val"),
				csrfmiddlewaretoken: getCookie("csrftoken")
            }).html(spinner);
        });
    } else {
        td.load("/faction/walls/manage/", {
            type: "toggle", wallId: td.attr("data-val"),
			csrfmiddlewaretoken: getCookie("csrftoken")
        }).html(spinner);
    }
});


// create report
$(document).on("click", ".wall-report-add", e => {
    e.preventDefault();
    $("#content-update").load("/faction/attacks/", {
        type: "new", wallId: $(e.currentTarget).closest("td").attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav("/faction/attacks/"));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Creating report");
});

// see report
$(document).on("click", ".wall-report-see", e => {
    e.preventDefault();
    const reportId = $(e.currentTarget).attr("data-val");
    $("#content-update").load(`/faction/attacks/${reportId}`, {
        reportId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(`/faction/attacks/${reportId}`));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Loading report");
    $("div.error").hide();
});
