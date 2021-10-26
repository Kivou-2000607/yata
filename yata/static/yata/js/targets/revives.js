// toggle revive from revives list button
$(document).on("click", "a[id^='revives-list-toggle-']", (e) => {
    e.preventDefault();
    $(e.target.closest("td")).load("/target/revive/", {
        reviveId: e.currentTarget.getAttribute("id").split("-").pop(),
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
