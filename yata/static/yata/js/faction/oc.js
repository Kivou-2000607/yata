$(document).on("click", "a.filter-player", e => {
    e.preventDefault();
    const url = $(e.currentTarget).attr("href") === "?" ? "/faction/oc/" : $(e.currentTarget).attr("href");
    $(e.currentTarget).html(spinner);
	// const action = $(e.currentTarget).attr("href") === "?" ? "Removing filters" : "Filtering crimes";
    // $("#content-update div.module").each(function(index, item) {
    //     $(item).html('<div  style="text-align: center; height: '+$(item).css("height")+';">'+spinner+'&nbsp;&nbsp;'+action+'</div>');
    // });
    window.location = url;
});

$(document).on("click", "span.show-team", e => {
    e.preventDefault();
    $("#faction-crimes-team-" + $(e.currentTarget).attr("data-val")).modal("show");
});
