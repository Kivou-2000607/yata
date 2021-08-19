// countdown
window.setInterval(() => {
    $(".event-countdown").each((i, e) => {
        const date = parseInt($.trim($(e.target).attr("data-val")));
        const now = parseInt(Date.now() / 1000);
        const countdown = Math.max(date - now, 0);

		const target = $(e.target);
        // transform notations if < 0
        if (countdown === 0) {
            target.addClass("valid");
            target.html("Started");
        } else if (countdown < 3600) {
            target.addClass("error");
            target.closest("div.faction-event").addClass("faction-event-urgent");
            target.html(fancyCountdown(countdown));
        } else if (countdown < 24 * 3600) {
            target.addClass("warning");
            target.html(fancyCountdown(countdown));
            target.closest("div.faction-event").addClass("faction-event-soon");
        } else {
            target.addClass("neutral");
            target.html(fancyCountdown(countdown));
        }
    });
}, 1000);

// share reports
$(document).on("click", "#faction-chain-report-share", e => {
    e.preventDefault();
    $(e.currentTarget).closest("div").load("/faction/chains/manage/", {
        type: "share",
		chainId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});
$(document).on("click", "#faction-attacks-report-share", e => {
    e.preventDefault();
	const span = $(e.currentTarget).closest("div");
    span.load("/faction/attacks/manage/", {
        type: "share",
		reportId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(`<span style="margin-left: 5px; width: ${span.width()}px">${spinner}</span>`);
});
$(document).on("click", "#faction-revives-report-share", e => {
    e.preventDefault();
	const span = $(e.currentTarget).closest("div");
    span.load( "/faction/revives/manage/", {
        type: "share",
		reportId: $(e.currentTarget).attr("data-val"),
		csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(`<span style="margin-left: 5px; width: ${span.width()}px">${spinner}</span>`);
});
