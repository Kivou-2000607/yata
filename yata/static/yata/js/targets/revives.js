// toggle revive from revives list button
$(document).on("click", "a[id^='revives-list-toggle-']", (e) => {
    e.preventDefault();
    const reload = e.target.closest("td");
    reload.load("/target/revive/", {
        reviveId: e.target.getAttribute("id").split("-").pop(),
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// show breakdown
$(document).on("click", "#targets-revives-breakdown", (e) => {
    e.preventDefault();
    $("#revives-breakdown").load("/target/revives/breakdown/", {
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
});
