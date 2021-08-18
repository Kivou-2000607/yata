$(document).on("click", "table.target-categories td", (e) => {
    e.preventDefault();
    const l = $(e.target).children("a").attr("href").split("/")[2];
    $("#content-update").load(`/target/${l}/`, {
        csrfmiddlewaretoken: getCookie("csrftoken")
    }, nav(`/target/${l}`));
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(`${spinner}&nbsp;&nbsp;Loading ${l}`);
    $("div.error").hide();
});
