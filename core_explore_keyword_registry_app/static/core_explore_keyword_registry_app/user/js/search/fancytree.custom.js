clearTree = function(div_tree, link) {
    if (!$(link).hasClass('disabled_refinements')) {
        var root =  $(div_tree).fancytree('getTree');
        if (root.length !== 0) {
            root.visit(function(node){
                node.setSelected(false);
            });
            // trigger the event clearTree
            $(document).trigger("clearTree", div_tree);
        }
    }
}

/**
 * Get refinement count.
 */
var getRefinementsCount = function(){
    $.ajax({
        url: data_source_count,
        type : "GET",
        data: {
            'query_id': $('#id_query_id').val()
        },
        beforeSend: function( xhr ) {
            $(".occurrences").each(function(){
                $(this).html("(-)");
                $(this).closest('span').fadeTo(100, 0.2);
            });
            $('.clearTree').addClass('disabled_refinements');
        },
        success: function(data){
            $(".occurrences").each(function(){
                    $(this).html("(0)");
            });
            // Update count (add number)
            var items = jQuery.parseJSON(data);
            for (x in items) {
                $('#'+items[x]._id).html('('+items[x].count+')');
                if(items[x].count > 0)
                    $('#'+items[x]._id).closest('span').fadeTo(100, 1);
                else
                    $('#'+items[x]._id).closest('span').fadeTo(100, 0.2);
            }
        },
        error: function(data){
        },
        complete: function(){
            // Enable clear
            $('.clearTree').removeClass('disabled_refinements');
        }
    });
};