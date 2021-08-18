// show/hide breakdowns
// categories
$(document).on("click", "table.stock-categories td", (e) => {
    e.preventDefault();
	const _href = $(e.target).children("a").attr("href").split("/");
    const l = _href[2];
    const t = _href[3];
    console.log(l);
    console.log(_href);
	$("#content-update").load(`/stock/${l}/${t}`, {
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(`${spinner}&nbsp;&nbsp;Loading ${l}`);
    $("div.error").hide();
});

// open details and prices
$(document).on("click", ".stock-details", (e) => {
    e.preventDefault();
    const tId = $(e.target).attr("href").split("/").pop();
    $("#stock-details").load(`/stock/details/${tId}`, {
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
});
$(document).on("click", ".stock-prices", (e) => {
    e.preventDefault();
    const tId = $(e.target).attr("href").split("/").pop();
    $("#stock-prices").load(`/stock/prices/${tId}`, {
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
});
$(document).on("click", ".graph-period-selector", (e) => {
    e.preventDefault();
	const _val = $(e.target).children("input").val().split("-");
    const tId = _val[0];
    const period = _val[1];
    console.log(tId, period);
    $("#stock-prices-graphs").load(`/stock/prices/${tId}/${period}`, {
        csrfmiddlewaretoken: document.getElementsByName("csrfmiddlewaretoken")[0].value,
    });
    $(e.target).addClass("fas fa-spinner fa-pulse");
});

// $(document).on("click", ".close", (e) => {
//     e.preventDefault();
//     $(e.target).parent("div.container").css("display", "none");
// });
