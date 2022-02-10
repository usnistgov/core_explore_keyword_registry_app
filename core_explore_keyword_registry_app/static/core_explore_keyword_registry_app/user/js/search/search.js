shortenDescription = function() {
    $.each($(".description"), function(index, item) {
       $(item).shorten({
           showChars: 350,
            moreText: " Show more",
            lessText: " Show less"
       });
    });
};

$(document).ready(function() {
    shortenDescription();
    getRefinementsCount();
});
