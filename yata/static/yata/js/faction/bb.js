// big brother
$(document).on("change", ".faction-bb-stats-list", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).val().split("-");
    console.log(splt);
	let tsA, tsB, type;
    if (splt.length === 2) {
        tsB = 0;
        tsA = splt.pop();
        type = splt.pop();
    } else if (splt.length === 3) {
        tsB = splt.pop();
        tsA = splt.pop();
        type = splt.pop();
    }
    $("#faction-big-brother-table").load("/faction/bigbrother/", {
        tsA, tsB, name: type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// big brother add
$(document).on("change", ".faction-bb-enter-challenge", e => {
    e.preventDefault();
    const add = $(e.currentTarget).val();
    $("#content-update").load("/faction/bigbrother/", {
        add,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("#content-update h2").addClass("grey").html(`${spinner}&nbsp;&nbsp;Adding challenge ${add}`);
});

// big brother remove
$(document).on("click", ".faction-bb-delete", e => {
    e.preventDefault();
    const splt = $(e.currentTarget).attr("data-val").split("-");
    const tr = $(e.currentTarget).parents("div.challenge");
    tr.load("/faction/bigbrother/remove/", {
        ts: splt.pop(),
        name: splt.pop(),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// big toggle challenges view
$(document).on("click", "tr[id^='faction-bb-challenges-toggle-']", e => {
    e.preventDefault();
    const tog = $(e.currentTarget);
    const stat = tog.attr("id").split("-").pop();
    const toshow = $(".faction-bb-challenges-catch-" + stat);
    toshow.toggle();

    const i = tog.find("i.fa-caret-right");
    if (toshow.css("display") === "none") i.removeClass("fa-rotate-90");
    else i.addClass("fa-rotate-90");

});

$(document).on("click", "i.show-stats", e => {
    e.stopPropagation();
    $("#faction-bb-statistics-" + $(e.currentTarget).attr("data-val")).modal("show");
});
