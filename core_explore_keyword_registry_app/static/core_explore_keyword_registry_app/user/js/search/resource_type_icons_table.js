/*
* Resource type icons table javascript file.
*/


/**
 * Called when an icon is selected
 */
var selectIcon = function(event) {
    selectRole(event.data.role);
};

/**
 * Select the role given
 */
var selectRole = function(role) {
    // select the role in the icon's table
    selectRoleInIconTable(role);
    // select the role in the tree
    selectRoleInTree(role);
};

/**
 * Select in the icon's table the role given
 */
var selectRoleInIconTable = function(role) {

    if ($("#cnt_" + role).hasClass("selected_resource")) {
        $("#cnt_" + role).removeClass("selected_resource");
    } else {
        $("#cnt_" + role).addClass("selected_resource");
        if (role != role_custom_resource_type_all) {
             $("#cnt_"+ role_custom_resource_type_all).removeClass('selected_resource')
        }
        if (role == role_custom_resource_type_all || (areAllSelectedInTableExceptAll() && areAllSelectedInTypeTree())) {
            clearTable();
            $("#cnt_"+ role_custom_resource_type_all).addClass('selected_resource');
        }
    }
};

/**
 * Is role selected in the Icon's table?
 */
var isRoleInIconTableIsSelected = function(role) {
    var cnt_id = "#cnt_" + role;
    return $(cnt_id).hasClass("selected_resource");
};

/**
 * Select in the tree the role given
 */
var selectRoleInTree = function(role, cnt_id) {
    var tree = getTypeTree();
    var root =  tree.fancytree('getTree');
    if (role == role_custom_resource_type_all || isIconAllSelectedInTable()) {
        // select all checkbox of the type section
        selectAllCheckboxes(tree, root);
    }
    else {
        if (root.length !== 0) {
            // select or unselect the node in tree
            selectTreeNodeByRole(role, root);
        }
    }
};

/**
 * select / unselect all checkboxes
 */
var selectAllCheckboxes = function(tree, root) {
    var selected = areAllSelectedInTypeTree(tree);
    setSelectedAllCheckboxes(root, !selected);
};

/**
 * unselect all checkboxes
 */
var unselectAllCheckboxes = function(root) {
    setSelectedAllCheckboxes(root, false);
};

/**
 * set setSelected all checkboxes
 */
var setSelectedAllCheckboxes = function(root, selected) {
    if (root.length !== 0) {
        root.visit(function(node){
            node.setSelected(selected);
        });
    }
};

/**
 * Check if all the nodes are selected in type tree
 */
var areAllSelectedInTypeTree = function() {
    var tree = getTypeTree();
    var allCount = tree.fancytree('getRootNode').tree.count();
    var selectedNodes = tree.fancytree('getRootNode').tree.getSelectedNodes();
    return selectedNodes.length == allCount;
};

/**
 * Check if the icon all resource is selected
 */
var isIconAllSelectedInTable = function() {
    return $("#cnt_" + role_custom_resource_type_all).hasClass("selected_resource");
};

/**
 * Check if all the Icons are selected (except 'all')
 */
var areAllSelectedInTableExceptAll = function() {
    var allSelected = true;
    $("div[id^='cnt_']").each(function() {
        if (this.id != 'cnt_' + role_custom_resource_type_all) {
            if (!$(this).hasClass("selected_resource")) {
                allSelected = false;
                // break the loop
                return false;
            }
        }
    });
    return allSelected;
};

/**
 * Get the type section tree
 */
var getTypeTree = function() {
    return $("[id^=id_refinement-type]");
};

/**
 * Called when a Node is selected
 */
var fancyTreeSelectHandler = function(event, data){
    if (data.originalEvent){
        last_parent = getFirstParendNode(data.node);
        select_resource = false;
        targeted_div = null;

        // if the parent contains checked children
        if (last_parent.getSelectedNodes().length > 0
            || last_parent.selected)
            select_resource = true;

        // get the targeted td
        for(var key in dict_category_role) {
            var value = dict_category_role[key];
            if (last_parent.title.includes(key)) {
                targeted_div = $("#cnt_" + value);
                break;
            }
        }

        if (targeted_div) {
            // add or remove the css class
            if (select_resource)
                targeted_div.addClass("selected_resource");
            else
                targeted_div.removeClass("selected_resource");

            if (areAllSelectedInTableExceptAll() && areAllSelectedInTypeTree()){
                // if 'all' is not selected
                clearTable();
                // select all
                $("#cnt_" + role_custom_resource_type_all).addClass("selected_resource");
            } else if(!areAllSelectedInTypeTree()) {
                $("#cnt_" + role_custom_resource_type_all).removeClass("selected_resource");
            }
        }
    }
};

/**
 * Get the node with the role given
 */
var selectTreeNodeByRole = function(role, root) {

    // if we have refinements defined for custom resource
    var list_refinements = dict_refinements[role];
    if (list_refinements.length > 0) {
        root.visit(function (node) {
            for (var i = 0; i < list_refinements.length; i++) {
                var refinements = list_refinements[i];
                var title = node.title.split(" <em")[0];
                if (title.startsWith(" ")) { // the sub category starts with a space
                    title = title.substring(1);
                }
                if (title == refinements) {
                    if (areAllSelectedInTypeTree()) {
                        unselectAllCheckboxes(root);
                        $("#cnt_" + role).addClass("selected_resource");
                    }

                    if (isRoleInIconTableIsSelected(role)) {
                        node.setSelected(true);
                    } else {
                        parent_node = getFirstParendNode(node);
                        parent_node.visit(function (node) {
                            node.setSelected(false);
                        });
                    }
                }
            }
        });
    } else { // otherwise, select parent

        var node_title = "";
        for (var key in dict_category_role) {
            var value = dict_category_role[key];
            if (role == value) {
                node_title = key;
                break;
            }
        }
        root.visit(function (node) {
            if (node.title.includes(node_title)) {

                if (areAllSelectedInTypeTree()) {
                    unselectAllCheckboxes(root);
                    $("#cnt_" + role).addClass("selected_resource");
                }

                var parent_node = getFirstParendNode(node);
                if (parent_node == node) {
                    node.setSelected(isRoleInIconTableIsSelected(role));
                } else {
                    parent_node.visit(function (node) {
                        node.setSelected(isRoleInIconTableIsSelected(role));
                    });
                }
            }
        });
    }
};

/**
 * Return the very last Parent of the node given
 */
var getFirstParendNode = function(node) {
    if (node.parent != null) {
        if (node.parent.title != "root") {
            // if is not the root, we continue
            return getFirstParendNode(node.parent);
        } else {
            // otherwise we return it
            return node;
        }
    }
};

/**
 * Unselect all types
 */
var clearTable = function() {
    // if 'all' is not selected
    $("div[id^='cnt_']").each(function() {
        // unselect all
        $(this).removeClass("selected_resource");
    });
};

/**
 * Called when fancy tree is ready
 */
var fancyTreeReadyHandler = function(event, data) {
    var tree = getTypeTree();
    var root = tree.fancytree('getTree');
    if (root == data.tree) {
        // if all Type are selected after a submit
        if (areAllSelectedInTypeTree(tree)) {
            clearTable();
            $("#cnt_" + role_custom_resource_type_all).addClass("selected_resource");
        }
    }
    // We hide the table until the fancy tree is ready
    $("#icons_table").show();
};

// .ready() called.
$(function() {

    $("#icons_banner div").each(function(){
        $(this).on("click", { role: this.id.replace('cnt_', '') }, selectIcon);
    }) ;

    // bind event to clearTree calls
    $(document).on("clearTypeTree", function(event, div_tree){
        clearTable();
    });
    // bind event to fancy_tree_select_event calls
    $(document).on("fancy_tree_select_event", function(event, data){
        fancyTreeSelectHandler(event, data);
    });
    // bind event to fancy_tree_ready_event calls
    $(document).on("fancy_tree_ready_event", function(event, data){
        fancyTreeReadyHandler(event, data);
    });

    // Select the icon when arriving on the page
    for (var j=0; j< refinement_selected_types.length; j++) {
        var refinement = refinement_selected_types[j];
        for(var key in dict_category_role) {
            var value = dict_category_role[key];
            if (refinement == key) {
                $("#cnt_" +value).addClass("selected_resource");
            }
        }
    }
});