// toggle target from attack list button
$(document).on("click", ".attack-list-target", (e) => {
    e.preventDefault();
    const targetId = $(e.target).closest("tr").attr("data-tId");
    const attackId = $(e.target).closest("tr").attr("data-aId");
    const reload = $(`.catch-buttons-attack-${targetId}`);
    reload.load("/target/attack/", {
        targetId, attackId, type: "toggle",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    reload.html(spinner);
});

// toggle attacks from revives list button
$(document).on("click", ".attack-list-paid", (e) => {
    e.preventDefault();
    const attackId = $(e.target).closest("tr").attr("data-aId");
    $(e.target).closest("td").load("/target/attack/", {
        attackId, type: "paid",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html(spinner);
});

// pay losses
$(document).on("click", ".targets-attacks-losses-payall", (e) => {
    e.preventDefault();
    $("#attack-losses").load("/target/attacks/losses/", {
        payall: $(e.target).attr("data-val"),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
});

// send losses
$(document).on("click", "#target-losses-send-all-cash", (e) => {
    e.preventDefault();
    $("a.targets-attacks-losses-payall").each((index, element) => {
        const tid = $(element).attr("data-val");
        if (!isNaN(parseInt(tid))) window.open(`https://www.torn.com/sendcash.php#/XID=${tid}&losses=${$(element).attr("data-los")}`, "_blank");
    });
});
