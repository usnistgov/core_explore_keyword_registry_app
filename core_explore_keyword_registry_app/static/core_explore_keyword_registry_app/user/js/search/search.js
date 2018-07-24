$(document).ready(function() {
    $(".description").shorten({
        showChars: 350,
        ellipsesText: "",
        moreText: "... show more",
        lessText: " show less",
    });

    getRefinementsCount();
});
