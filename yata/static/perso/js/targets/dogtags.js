$(document).on('click', 'table#target-dogtags > tbody > tr > td:not(.dont-touch-me)', function (e) {
    e.preventDefault();
    const tr = $(this).parents("tr");
    const uid = tr.attr("data-uid");
    const los = tr.attr("data-los");
    $("#target-dogtags-compare").load("/target/dogtags/", {
        uid: uid,
        los: los,
        type: "compare",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<div class="container"><div class="overlay close"></div><div class="modal-center-large"><div class="module" ><p>' + spinner + '</p></div></div></div>');
});

// delete target from target list button
$(document).on('click', 'a.target-dogtags-delete', function (e) {
    e.preventDefault();
    const tr = $(this).parents("tr");
    const uid = tr.attr("data-uid");
    tr.load("/target/dogtags/", {
        uid: uid,
        type: "delete",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    tr.remove();
});

// delete target from overlay
$(document).on('click', 'a.target-dogtags-delete-overlay', function (e) {
    e.preventDefault();
    const uid = $(this).attr("data-uid");
    var tr = $(`tr[data-uid='${uid}']`)
    tr.load("/target/dogtags/", {
        uid: uid,
        type: "delete",
        csrfmiddlewaretoken: getCookie("csrftoken")
    });
    $("div.container").remove();
    tr.remove();
});

// add failed attack target from target list button
$(document).on('click', 'a.target-dogtags-add', function (e) {
    e.preventDefault();
    const tr = $(this).parents("tr");
    const uid = tr.attr("data-uid");
    tr.load("/target/dogtags/", {
        uid: uid,
        type: "add",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="9">' + spinner + "</td>");
});

// add failed target from overlay
$(document).on('click', 'a.target-dogtags-add-overlay', function (e) {
    e.preventDefault();
    const uid = $(this).attr("data-uid");
    var tr = $(`tr[data-uid='${uid}']`)
    tr.load("/target/dogtags/", {
        uid: uid,
        type: "add",
        csrfmiddlewaretoken: getCookie("csrftoken")
    }).html('<td colspan="9">' + spinner + "</td>");
    $("div.container").remove();
});