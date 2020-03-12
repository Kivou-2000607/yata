$(document).on('click', '#toggle-awards-done', function(e){
    e.preventDefault();
    var cat = $('i[id^="award-category-"]:not(".fa-toggle-off")');
    $("tr.award-done").promise().done(function() {
        var icon = $("#awards-done-icon");
        if (icon.hasClass("fas fa-toggle-on")) {
            icon.removeClass("fas fa-toggle-on");
            icon.addClass("fas fa-toggle-off");
            $('#toggle-awards-done-txt').html("Show");
            $("tr.award-done").slideUp('fast', function() {});
        } else {
            icon.removeClass("fas fa-toggle-off");
            icon.addClass("fas fa-toggle-on");
            $('#toggle-awards-done-txt').html("Hide");
            if(cat.attr('id') == null) {
                $("tr.award-done").slideDown('fast', function() {});
            } else {
                $("tr.award-done."+cat.attr('id')).slideDown('fast', function() {});
            }
        }
    });
});

$(document).on('click', 'span[id^="award-category-"]', function(e){
    e.preventDefault();
    // *********************** //
    // HANDLE CATEGORY BUTTONS //
    // *********************** //

    // select award category and toggleButton
    var awardCategory = $(this).attr("id");
    var toggleButton = $("#"+awardCategory).children("i");

    // check if toggle button was already on and change to Allawards if so
    if (toggleButton.hasClass("fas fa-toggle-on")) {
        awardCategory = "award-category-Allawards"
        toggleButton = $("#"+awardCategory).children("i");
    }
    // put all buttons to off and current button to on
    $('[id^="award-category-"]').children("i").removeClass("fas fa-toggle-on");
    $('[id^="award-category-"]').children("i").addClass("fas fa-toggle-off");
    toggleButton.removeClass("fas fa-toggle-off")
    toggleButton.addClass("fas fa-toggle-on")

    // *********************** //
    // HANDLE AWARDS SHOW/HIDE //
    // *********************** //

    // get all awards container and hide all awards
    var allAwardsContainer = $('table#awards-list').children("tbody");
    allAwardsContainer.find("tr").hide();

    // create selector with award category
    var selector = 'tr.'+awardCategory

    // add to selector todo if not show awards done
    if ($("#awards-done-icon").hasClass("fas fa-toggle-off")) {
        selector += '.award-todo'
    }

    // select awards to show and show them
    allAwardsContainer.find(selector).show('fast', function() {});
});

$(document).on('click', 'table.awards-categories td', function(e){
    e.preventDefault();
    $( "#content-update" ).load( "/awards/"+$(this).children("a").attr("href").split("/")[2]+"/", {
        csrfmiddlewaretoken: document.getElementsByName('csrfmiddlewaretoken')[0].value,
    }, nav("/awards/"+$(this).children("a").attr("href").split("/")[2]));
    $("#content-update h2").addClass("grey");
    $("#content-update h2").html(spinner+'&nbsp;&nbsp;Loading awards')
    $("div.error").hide();
});
