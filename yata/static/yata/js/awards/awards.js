$(document).on("click", "#toggle-awards-done", (e) => {
    e.preventDefault();
    const cat = $('i[id^="award-category-"]:not(".fa-toggle-off")');
    $("tr.award-done").promise().done(() => {
        const icon = $("#awards-done-icon");
        if (icon.hasClass("fas fa-toggle-on")) {
            icon.removeClass("fas fa-toggle-on");
            icon.addClass("fas fa-toggle-off");
            $("#toggle-awards-done-txt").html("Show");
            $("tr.award-done").slideUp("fast", () => {});
        } else {
            icon.removeClass("fas fa-toggle-off");
            icon.addClass("fas fa-toggle-on");
            $('#toggle-awards-done-txt').html("Hide");
            if (cat.attr("id") == null) {
                $("tr.award-done").slideDown('fast', () => {});
            } else {
                $("tr.award-done." + cat.attr("id")).slideDown("fast", () => {});
            }
        }
    });
});

//
$(document).on("click", "div[id^='award-category-']", (e) => {
    e.preventDefault();
    // *********************** //
    // HANDLE CATEGORY BUTTONS //
    // *********************** //

    // select award category and toggleButton
    let awardCategory = e.target.getAttribute("id");
    let toggleButton = $("#"+awardCategory).children("i");

    // check if toggle button was already on and change to Allawards if so
    if (toggleButton.hasClass("fas fa-toggle-on")) {
        awardCategory = "award-category-Allawards";
        toggleButton = $("#"+awardCategory).children("i");
    }
    // put all buttons to off and current button to on
    $('[id^="award-category-"]').children("i").removeClass("fas fa-toggle-on").addClass("fas fa-toggle-off");
    toggleButton.removeClass("fas fa-toggle-off").addClass("fas fa-toggle-on");

    // *********************** //
    // HANDLE AWARDS SHOW/HIDE //
    // *********************** //

    // get all awards container and hide all awards
    const allAwardsContainer = $("table#awards-list").children("tbody");
    allAwardsContainer.find("tr").hide();

    // create selector with award category
    let selector = "tr." + awardCategory;

    // add to selector todo if not show awards done
    if ($("#awards-done-icon").hasClass("fas fa-toggle-off")) {
        selector += ".award-todo";
    }

    // select awards to show and show them
    allAwardsContainer.find(selector).show("fast", () => {});
});

// toggle pin
$(document).on("click", ".awards-toggle-pin", (e) => {
    e.preventDefault();

    // $.when( $(this).closest("td").load( "/awards/pin/", {
    //     awardId: $(this).attr("data-val"),
    //     csrfmiddlewaretoken: getCookie("csrftoken")
    // }).html(spinner) ).done(
    //     $(".pinned.awards-toggle-pin").closest("td").each(function() {
    //         $(this).load( "/awards/pin/", {
    //             awardId: $(this).find("form > a > i").attr("data-val"),
    //             check: 1,
    //             csrfmiddlewaretoken: getCookie("csrftoken")
    //         }).html("?");
    //     }));

    event.target.closest("td").load("/awards/pin/",
        {
            awardId: event.target.getAttribute("data-val"),
            csrfmiddlewaretoken: getCookie("csrftoken")
        },
        () => {
            $(".pinned.awards-toggle-pin").closest("td").each((i, e) => {
                $(e).load("/awards/pin/",
                {
                    awardId: $(e).find("form > a > i").attr("data-val"),
                    check: 1,
                    csrfmiddlewaretoken: getCookie("csrftoken")
                }).html(spinner);
            })
			.promise()
			.done(() => {
                $(".awards-pinned-spin")
                .each((i, e) => {
					$(e).html(`<div style="height: ${$(e).css("height")};">${spinner}</div>`);
                })
                .promise()
                .done(() => {
					$("#awards-show-pinned").load( "/awards/pinned/", {csrfmiddlewaretoken: getCookie("csrftoken")});
				});
            });
        }
	);
});
