$(document).on("click", ".merits-button", e => {
    e.preventDefault();

    const button = $(e.currentTarget);
    const simu_lvl = button.hasClass("le") ? button.attr("data-lvl") - 1 : button.attr("data-lvl");
    const simu_name =  button.parent("td").attr("data-mer");
    const n_merits = $("tr#merit-count").attr("data-ini");
    const merits = [];
    $(".merits-button.le").each((it, el) => {
        merits.push([$(el).parent("td.merits-bar").attr("data-mer"), $(el).attr("data-lvl"), $(el).parent("td.merits-bar").attr("data-fix")]);
    });

    $("#player-merits").load("/player/merits/", {
        n_merits, merits: JSON.stringify(merits), simu: JSON.stringify([simu_name, simu_lvl]),
        csrfmiddlewaretoken: getCookie("csrftoken")
    });

    // fancy
    if (button.hasClass("gt")) {
        const prev = $($(e.currentTarget).prevAll(".gt").get().reverse());
        const dt = 100 / prev.length;
        let t = 0;
        prev.each((it, el) => {
            setTimeout(() => $(el).removeClass("add").removeClass("gt").addClass("le-flash"), t);
            setTimeout(() => $(el).removeClass("le-flash").addClass("le"), t + 2 * dt);
            setTimeout(() => $(e.currentTarget).removeClass("add").removeClass("gt").addClass("le-flash-2"), 100);
            t += dt;
        });
    } else {
        const next = $(e.currentTarget).nextAll(".le");
        const dt = 100 / next.length;
        let t = 0;
        next.each((it, el) => {
            setTimeout(() => $(el).removeClass("le").addClass("gt-flash"), t);
            setTimeout(() => $(el).removeClass("gt-flash"), t + 2 * dt);
            setTimeout(() => $(e.currentTarget).removeClass("rem").removeClass("le").addClass("gt-flash-2"), 100);
            t += dt;
        });
    }
});


// show/hide command
$(document).on("click", ".player-personalstats-header", (e) => {
    e.preventDefault();
    // get h2 and div
    const h = $(e.target);
    const d = h.next("div");
    const i = h.find("i[class^='fas fa-caret']");
    d.slideToggle("fast", () => {
        if (d.css("display") === "none") i.removeClass("fa-rotate-90");
        else i.addClass("fa-rotate-90");
    });
});
