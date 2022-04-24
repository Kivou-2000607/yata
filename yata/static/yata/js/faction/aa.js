// toggle key
$(document).on("click", ".faction-aa-toggle-key", e => {
    e.preventDefault();
    $(e.currentTarget).parents("td").load("/faction/configurations/key/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// threshold
$(document).on("change", "#faction-aa-change-threshold", e => {
    e.preventDefault();
    const reload = $(e.currentTarget).closest("div.faction-aa-threshold");
    reload.load("/faction/configurations/threshold/", {
        threshold: $(e.currentTarget).val(),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html(spinner);
});

// poster on/off/hold
$(document).on("click", "a[id^='faction-aa-toggle-poster']", e => {
    e.preventDefault();
    const type = e.currentTarget.id.split("-").pop();
    const reload = $(e.currentTarget).parents("div#faction-aa-poster");
	const divspinner = `<div style="text-align: center; height: ${reload.css("height")};">${spinner}</div>`;
    reload.load("/faction/configurations/poster/", {
        type,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(divspinner);
});

// parameters
$(document).on("change", "[id^='faction-poster-']", e => {
    e.preventDefault();
    const v = $(e.currentTarget).val();
    const id = $(e.currentTarget).attr("id").split("-");
    const p = id.pop();
    const t = id.pop();
    const reload = $(e.currentTarget).parents("div#faction-aa-poster");
	const divspinner = `<div style="text-align: center; height: ${reload.css("height")};">${spinner}</div>`;
    reload.load("/faction/configurations/poster/", {
        posterConf: 1, t, p, v,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(divspinner);
});

// events delete
$(document).on("click", "a.faction-event-delete", e => {
    e.preventDefault();
    $(e.currentTarget).closest("tr").load("/faction/configurations/event/", {
        type: "delete",
        eventId: e.currentTarget.dataset.val,
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).remove();
});

// events create
$(document).on("click", "button#faction-event-create", e => {
    e.preventDefault();
    const form = $(e.currentTarget).closest("div.row");
    let stack = 0;
    if (form.find("#event-stack").prop("checked")) stack = 1;
    let reset = 0;
    if (form.find("#event-reset").prop("checked")) reset = 1;
    $(e.currentTarget).closest("div.module").load("/faction/configurations/event/", {
        type: "create",
        title: form.find("#event-title").val(),
        description: form.find("#event-description").val(),
        ts: form.find("#event-ts").val(),
        stack,
        reset,
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $(e.currentTarget).html(spinner);
});


// clipboard
$(document).on("click", "#link-poster-clipboard,#link-poster-gym-clipboard", e => {
  const link = $(e.currentTarget).attr("data-val");
  navigator.clipboard.writeText(link);
});
