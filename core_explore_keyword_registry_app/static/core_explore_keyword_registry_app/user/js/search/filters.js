/**
 * Initialize filter tags
 */
var initTagFilters = function () {
    $("#category-filters").tagit({
        readOnly: false,
        singleFieldNode: false,
        beforeTagRemoved: function(event, ui) {
            if(!ui.tag.hasClass('disabled_refinements'))
                clearTree("#"+ ui.tag.attr("custom_id"), ui.tag);
            else
                return false;
        },
        afterTagRemoved: function(event, ui) {
            if(!$("#category-filters").tagit("hasTag"))
                hideFilters();
        },
    });
    $(".filters-refinements").find(".ui-autocomplete-input").prop('readonly', true);
}

/**
 * Manage Filters
 */
var manageFilters = function (tree) {
    treeId = $(tree.$div[0]).attr("id");
    treeName = $(tree.$div[0]).attr("name");
    if(areAllUnselected(tree))
        $("#category-filters").tagit("removeTagByLabel", treeName);
    else if ($("#category-filters").tagit("isNew", treeName))
    {
        $("#category-filters").tagit("createTag", treeName, undefined, undefined, custom_id=treeId);
        showFilters();
    }
}

/**
 * Show filters
 */
var showFilters = function () {
    $("#filters_refinements").show();
}

/**
 * Hide filters
 */
var hideFilters = function () {
    $("#filters_refinements").hide();
}

/**
 * Called when fancy tree select event is triggered
 */
var filterFancyTreeSelectHandler = function(event, data){
    manageFilters(data.tree);
};

/**
 * Create tags from an initial list
 */
var createTagsFromList = function(event, data){
    category_list = $(".category-list").html().split(",");
    category_created = false;
    for (index in category_list) {
        if (category_list[index]) {
            category = category_list[index].split('|');
            category_display_name = category[0];
            category_id = category[1];
            $("#category-filters").tagit("createTag",
                                         category_display_name,
                                         undefined,
                                         undefined,
                                         custom_id="id_refinement-" + category_id);
            category_created = true;
        }
    }

    if (!category_created)
       hideFilters();
};

// .ready() called.
$(function() {
    // init tag filters
    initTagFilters();
    // bind event to fancy_tree_select_event calls
    $(document).on("fancy_tree_select_event", function(event, data){
        filterFancyTreeSelectHandler(event, data);
    });
    // select tags
    createTagsFromList();
});