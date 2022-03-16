/* chain list */

// combined report
$(document).on("click", "#faction-chain-combined", e => {
    e.preventDefault();
    $("#content-update").load("/faction/chains/combined/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav("/faction/chains/combined/"));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Loading combined report");
    $("div.error").hide();
});

/* chain list button */

// create report
$(document).on("click", ".faction-chains-create", e => {
    e.preventDefault();
    $(e.currentTarget).parents("td").load("/faction/chains/manage/", {
        type: "create",
		chainId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// create report
$(document).on("click", ".faction-chains-cooldown", e => {
    e.preventDefault();
    $(e.currentTarget).parents("td").load( "/faction/chains/manage/", {
        type: "cooldown",
		chainId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// delete report
$(document).on("click", ".faction-chains-delete", e => {
    e.preventDefault();
    // handle n combined
    let n = parseInt($("#n-combined").text());
    if ($(e.currentTarget).siblings("a").children("i").hasClass("fa-toggle-on")) n -= 1;
    $("#n-combined").html(n);

    $(e.currentTarget).parents("td").load( "/faction/chains/manage/", {
        type: "delete",
		chainId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// toggle combine report
$(document).on("click", ".faction-chains-combine", e => {
    e.preventDefault();
    // handle n combined
    let n = parseInt($("#n-combined").text());
    if ($(e.currentTarget).children("i").hasClass("fa-toggle-off")) n += 1;
	else n -= 1;
    $("#n-combined").html(n);

    // handle toggle
    $(e.currentTarget).parents("td").load( "/faction/chains/manage/", {
        type: "combine",
		chainId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// add all combine report
$(document).on("click", "#faction-chains-combine-add-all", e => {
    e.preventDefault();
    $(".faction-chains-combine").each((index, value) => {
      if ($(value).children("i").hasClass("fa-toggle-off")) {
        $(value).parents("td").load("/faction/chains/manage/", {
            type: "combine",
			      chainId: $(value).attr("data-val"),
			      csrfmiddlewaretoken: getCookie("csrftoken")
        }).html(spinner);
        const n = parseInt($("#n-combined").text()) + 1;
        $("#n-combined").html(n);
      }
    });
});

// remove all combine report
$(document).on("click", "#faction-chains-combine-rem-all", e => {
    e.preventDefault();
    $(".faction-chains-combine").each((index, value) => {
      if ($(value).children("i").hasClass("fa-toggle-on")) {
        $(value).parents("td").load("/faction/chains/manage/", {
            type: "combine",
			chainId: $(value).attr("data-val"),
			csrfmiddlewaretoken: getCookie("csrftoken")
        }).html(spinner);
        const n = parseInt($("#n-combined").text()) - 1;
        $("#n-combined").html(n);
      }
    });
});

// see report
$(document).on("click", ".faction-chains-see", e => {
    e.preventDefault();
    const chainId = $(e.currentTarget).attr("data-val");
    $("#content-update").load(`/faction/chains/${chainId}`, {
        chainId, csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(`/faction/chains/${chainId}`));
    $("#content-update h2").addClass("grey").html(spinner + "&nbsp;&nbsp;Loading report");
    $("div.error").hide();
});

/* reports */

// toggle zero-hits
$(document).on("click", "#toggle-zero-hits", e => {
    e.preventDefault();
    $(".zero-hits").slideToggle("fast").promise().done(() => {
        $("#zero-hits-icon").toggleClass("fa-toggle-on fa-toggle-off");
    });
});

// toggle non-members
$(document).on("click", "#toggle-kicked-members", e => {
    e.preventDefault();
    $(".kicked-members").slideToggle("fast").promise().done(() => {
        $("#kicked-members-icon").toggleClass("fa-toggle-on fa-toggle-off");
    });
});

// show individual report
$(document).on("click", "tr[id^='faction-ireport-'] > td:not(.dont-touch-me)", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).closest("tr").attr("id").split("-");
    const memberId = splt.pop();
    const chainId = splt.pop();
    if (!$( "#individal-report-"+memberId ).length) {
        $(`<tr id="individal-report-${memberId}"></tr>`).insertAfter($(e.currentTarget).closest("tr"));
    }
    $(`#individal-report-${memberId}`).load("/faction/chains/individual/", {
        chainId,
        memberId,
        csrfmiddlewaretoken: getCookie("csrftoken")
	}).html(`<td colspan="12" style="text-align: center;">${spinner}</td>`);
});

// close individual report
$(document).on("click", "[id^='individal-report-']", e => {
    e.preventDefault();
    $(e.currentTarget).empty();
});
