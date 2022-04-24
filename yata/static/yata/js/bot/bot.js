// update discord id
$(document).on("click", "#discord-update-id", e => {
    e.preventDefault();
    const reload = $("#discord-id");
    reload.load("/bot/updateId/", {
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
    reload.html(spinner);
});

// toggle notifications
$(document).on("click", "div.api-notifications", e => {
    e.preventDefault();
    const reload = $(e.currentTarget);
    reload.load("/bot/toggleNoti/", {
        type: reload.attr("data-val"),
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    }).html(spinner);
});

$(document).ready(() => {
  const hash = window.top.location.hash.substr(1);
  if (hash) toggle_h($("#"+hash));
});
