// show/hide breakdowns
$(document).on('click', 'tr.h-a', function (e) {
    e.preventDefault();
    $(this).find("i.fa-caret-right").toggleClass("fa-rotate-90")
    $(this).parents("table").find(".h-b").toggle()
});