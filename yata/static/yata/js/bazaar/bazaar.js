// show foreign stocks of one item
$(document).on("click", "tr.abroad-item-stocks > td:not(.items-details)", e => {
    e.preventDefault();
	const tr = $(e.target).parent("tr");
    const item_id = tr.attr("data-ite");
    const country_key = tr.attr("data-cou");
    $("#bazaar-modal").load("/bazaar/abroad/stocks/", {
        item_id, country_key, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
});

// show foreing stocks item details
$(document).on("click", "tr.abroad-item-stocks > td.items-details", e => {
    e.preventDefault();
	const tr = $(e.currentTarget).parent("tr");
    const item_id = tr.attr("data-ite");
    $("#bazaar-modal").load(`/bazaar/prices/`, { item_id: item_id, csrfmiddlewaretoken: getCookie("csrftoken") });
});

// header click
$(document).on("click", ".item-table-header:not(.no-click)", e => {
    e.preventDefault();

    // get item data and DOM
    const action = $(e.currentTarget).attr("data-act");
    const item_table = $(e.currentTarget).parents(".item-table");
    const item_id = $(item_table).attr("data-iid");
    if(action === "update") {
		$(item_table).load(`/bazaar/update/${item_id}`, { csrfmiddlewaretoken: getCookie("csrftoken") });
		$(e.currentTarget).find("button").html(spinner);
    } else if (action === "delete") {
		$(item_table).load(`/bazaar/delete/${item_id}`, { csrfmiddlewaretoken: getCookie("csrftoken") });
		$(e.currentTarget).html(spinner);
    } else if (action === "details") {
		$( "#bazaar-modal" ).load(`/bazaar/details/${item_id}`, { csrfmiddlewaretoken: getCookie("csrftoken") });
    } else if (action === "toggle") {
		$(item_table).load(`/bazaar/toggle/${item_id}`, { csrfmiddlewaretoken: getCookie("csrftoken") });
    } else if (action === "prices") {
		$( "#bazaar-modal" ).load(`/bazaar/prices/`, { item_id: item_id, csrfmiddlewaretoken: getCookie("csrftoken") });
    }
});

// show more/less
$(document).on("click", "tr.show-more", e => {
    e.preventDefault();
    $(e.currentTarget).removeClass("d-table-row").hide();
    $(e.currentTarget).siblings().removeClass("d-none");
    $(e.currentTarget).siblings(".show-less").addClass("d-table-row").show();
});
// show more/less
$(document).on("click", "tr.show-less", e => {
    e.preventDefault();
    $(e.currentTarget).removeClass("d-table-row").hide();
    $(e.currentTarget).siblings().not(".keep-showing").not(".show-more").addClass("d-none");
    $(e.currentTarget).siblings(".show-more").addClass("d-table-row").show();
});

// update type
$(document).on("click", "span.update-type", e => {
    e.preventDefault();
    const type = $(e.currentTarget).attr("data-val");
    let i = 1;
    $("#loop-over-item-sell-table-"+type).find("div.item-table").each((useless, e) => {
        const item_table = $(e);
        const item_id = $(e).attr("data-iid");
        const wait = i * 500 + parseInt(i / 10) * 3000;
        ((index) => {
            setTimeout(() => {
                $(item_table).load(`/bazaar/update/${item_id}`, { csrfmiddlewaretoken:  getCookie("csrftoken") });
                $(item_table).find("button").html(spinner);
             }, wait);
        })(i);
        i++;
    });
});

// refresh timer update
window.setInterval(() => {
    $(".update-timer").each((i, e) => {
        const tsUpdate = parseInt(e.dataset.val);
        const tsNow = Date.now() / 1000;

        if (tsNow - tsUpdate > 300) {
            $(e).html("> 5 min");
            $(e).removeClass("update-timer");
        } else {
            $(e).html(fancyTimeFormat(tsNow - tsUpdate));
        }
    });
}, 1000);


// toggle abroad filters
$(document).on("click", "li.bazaar-toggle-filters", (e) => {
    e.preventDefault();
    const td = $(e.target);
    const filter = td.attr("data-fil");
    const key = td.attr("data-key");
    const reload = $(e.currentTarget).parents("div#bazaar-abroad-stocks-reload");
    // var divspinner = '<div style="text-align: center; height: '+reload.css("height")+';">'+spinner+'</div>'
    reload.load("/bazaar/abroad/", {
        key, filter, csrfmiddlewaretoken: getCookie("csrftoken"),
    });
    td.html(spinner);
    $("table#bazaar-abroad-stocks").find("tr").html(`<td colspan="9" style="text-align: center;">${spinner}</td>`);
    // $("table#bazaar-abroad-stocks").find("tbody").find("td").html('<i class="fas fa-spinner"></i>');
});
