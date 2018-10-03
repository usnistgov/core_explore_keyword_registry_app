/**
 * Clean all tree
 */
var clearAllTrees = function() {
    $(".clearTree").click();
}

/**
 * Check if all the nodes are unselected
 */
var areAllUnselected = function(tree) {
    var nodes = tree.getSelectedNodes();
    return nodes.length == 0;
}

/**
 * Check if all the nodes are selected
 */
var areAllSelected = function(tree) {
    var allCount = tree.count()
    var selectedNodes = tree.getSelectedNodes();
    return selectedNodes.length == allCount;
}

/**
 * When click on 'clear' in the refinement header
 */
var clearTree = function(div_tree, link) {
    if (!$(link).hasClass('disabled_refinements')) {
        var root = $(div_tree).fancytree('getTree');
        if (root.length !== 0) {
            root.visit(function(node){
                node.setSelected(false);
            });
            if (div_tree == "#id_refinement-type")
                // trigger the event clearTypeTree
                $(document).trigger("clearTypeTree", div_tree);
           else
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

/**
 * Add fancy tree select delay handler to all checkbox for data source
 */
var addFancyTreeSelectDelayHandler = function(event) {
    $("#data_sources_selector input:checkbox").on("click", fancyTreeSelectDelaySubmit);
}

// .ready() called.
$(function() {
    // bind event to fancy_tree_ready_event calls
    $(document).on("fancy_tree_select_event", function(event, data){
        fancyTreeSelectDelaySubmit();
    });
    // bind event to clean all button
    $(".clearAll").on("click", clearAllTrees);
    // bind event to all data source selector
    $("#data_sources_selector").on('DOMSubtreeModified', addFancyTreeSelectDelayHandler);
    // bind event to all header
    $("a[data-toggle='collapse']").each(function(index) {
        $(this).click(function(event) {
            if (!event.originalEvent) return;
            // reset the timer when an header is clicked
            // avoiding unwanted submission
            fancyTreeSelectDelaySubmit(false);
        });
    });
});