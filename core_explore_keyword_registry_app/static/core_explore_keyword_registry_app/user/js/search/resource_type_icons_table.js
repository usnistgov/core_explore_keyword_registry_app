/*
* Resource type icons table javascript file.
*/

/**
 * Resource type enumeration
 */
var resourceTypes = {
    All: "all",
    Organization: "organization",
    DataCollection: "dataCollection",
    ServiceAPI: "serviceAPI",
    Dataset: "dataset",
    WebSite: "webSite",
    Software: "software",
};

/**
 * Called when an icon is selected
 */
var selectIcon = function(event) {
    selectRole(event.data.role);
}

/**
 * Select the role given
 */
var selectRole = function(role) {
    var td_id = "#td_" + role;
    // select the role in the icon's table
    selectRoleInIconTable(role, td_id);
    // select the role in the tree
    selectRoleInTree(role);
};

/**
 * Select in the icon's table the role given
 */
var selectRoleInIconTable = function(role, td_id) {
    if (role == resourceTypes.All) {
        // if 'all' is selected
        if ($(td_id).hasClass("selected_resource")) {
            // unselect
            $(td_id).removeClass("selected_resource");
        } else {
            // if 'all' is not selected
            clearTable();
            // select all
            $(td_id).addClass("selected_resource");
        }
    } else {
        // unselect 'all'
        $("#td_all").removeClass("selected_resource");
        if ($(td_id).hasClass("selected_resource")){
            // unselect if already selected
            $(td_id).removeClass("selected_resource");
        } else {
            // select
            $(td_id).addClass("selected_resource");
        }
    }
}

/**
 * Is role selected in the Icon's table?
 */
var isRoleInIconTableIsSelected = function(role) {
    var td_id = "#td_" + role;
    return $(td_id).hasClass("selected_resource");
}

/**
 * Select in the tree the role given
 */
var selectRoleInTree = function(role, td_id) {
    var tree = getTypeTree();
    var root =  tree.fancytree('getTree');
    if (role == resourceTypes.All){
        // select all checkbox of the type section
        selectAllCheckboxes(tree, root);
    }
    else {
        if (root.length !== 0) {
            // select or unselect the node in tree
            selectTreeNodeByRole(role, root);
        }
    }
}

/**
 * select / unselect all checkboxes
 */
var selectAllCheckboxes = function(tree, root) {
    var selected = areAllSelectedInTypeTree(tree);
    if (root.length !== 0) {
        root.visit(function(node){
            node.setSelected(!selected);
        });
    }
}

/**
 * Check if all the nodes are selected in type tree
 */
var areAllSelectedInTypeTree = function() {
    var tree = getTypeTree();
    var allCount = tree.fancytree('getRootNode').tree.count()
    var selectedNodes = tree.fancytree('getRootNode').tree.getSelectedNodes();
    return selectedNodes.length == allCount;
}

/**
 * Check if all the Icons are selected (except 'all')
 */
var areAllSelectedInTableExceptAll = function() {
    var allSelected = true;
    $("td[id^='td_']").each(function() {
        if (this.id != 'td_all') {
            if (!$(this).hasClass("selected_resource")) {
                allSelected = false;
                // break the loop
                return false;
            }
        }
    });
    return allSelected;
}

/**
 * Get the type section tree
 */
var getTypeTree = function() {
    return $("#id_refinement-type");
}

/**
 * Called when a Node is selected
 */
var fancyTreeSelectHandler = function(event, data){
    if (data.originalEvent){
        last_parent = getFirstParendNode(data.node);
        select_resource = false;
        targeted_td = null;

        // if the parent contains checked children
        if (last_parent.getSelectedNodes().length > 0
            || last_parent.selected)
            select_resource = true;

        // get the targeted td
        if (last_parent.title.includes("Organization")) {
            targeted_td = $("#td_" + resourceTypes.Organization);
        }
        if (last_parent.title.includes("Collection")) {
            targeted_td = $("#td_" + resourceTypes.DataCollection);
        }
        if (last_parent.title.includes("Dataset")) {
            targeted_td = $("#td_" + resourceTypes.Dataset);
        }
        if (last_parent.title.includes("Service")) {
            targeted_td = $("#td_" + resourceTypes.ServiceAPI);
        }
        if (last_parent.title.includes("Software")) {
            targeted_td = $("#td_" + resourceTypes.Software);
        }
        if (last_parent.title.includes("Web Site")) {
            targeted_td = $("#td_" + resourceTypes.WebSite);
        }

        if (targeted_td) {
            // add or remove the css class
            if (select_resource)
                targeted_td.addClass("selected_resource");
            else
                targeted_td.removeClass("selected_resource");

            if (areAllSelectedInTableExceptAll() && areAllSelectedInTypeTree()){
                // if 'all' is not selected
                clearTable();
                // select all
                $("#td_" + resourceTypes.All).addClass("selected_resource");
            }
        }
    }
};

/**
 * Get the node with the role given
 */
var selectTreeNodeByRole = function(role, root) {
    node_title = "";
    if (role == resourceTypes.Organization)
        node_title = "unspecified Organization";
    if (role == resourceTypes.DataCollection)
        node_title = "unspecified Collection";
    if (role == resourceTypes.Dataset)
        node_title = "unspecified Dataset";
    if (role == resourceTypes.ServiceAPI)
        node_title = "unspecified Service";
    if (role == resourceTypes.WebSite)
        node_title = "unspecified Web Site";
    if (role == resourceTypes.Software)
        node_title = "Software";

    root.visit(function(node){
        if (node.title.includes(node_title)) {
            if (isRoleInIconTableIsSelected(role)) {
                if (areAllSelectedInTypeTree()){
                    // unselected all except the targeted node
                    root.visit(function(root_node){
                        if (root_node.key != node.key)
                            root_node.setSelected(false);
                        else
                            root_node.setSelected(true);
                    });
                } else {
                    node.setSelected(true);
                }
            } else {
                parent_node = getFirstParendNode(node);
                parent_node.visit(function(node){
                    node.setSelected(false);
                });
            }
        }
    });
}

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
}

/**
 * Unselect all types
 */
var clearTable = function() {
    // if 'all' is not selected
    $("td[id^='td_']").each(function() {
        // unselect all
        $(this).removeClass("selected_resource");
    });
}

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
            $("#td_all").addClass("selected_resource");
        }
    }
    // We hide the table until the fancy tree is ready
    $("#icons_table").show();
}

// .ready() called.
$(function() {
    // bind all click event to table's buttons
    $("#td_" + resourceTypes.All).on("click", {role: resourceTypes.All}, selectIcon);
    $("#td_" + resourceTypes.Organization).on("click", {role: resourceTypes.Organization}, selectIcon);
    $("#td_" + resourceTypes.DataCollection).on("click", {role: resourceTypes.DataCollection}, selectIcon);
    $("#td_" + resourceTypes.ServiceAPI).on("click", {role: resourceTypes.ServiceAPI}, selectIcon);
    $("#td_" + resourceTypes.Dataset).on("click", {role: resourceTypes.Dataset}, selectIcon);
    $("#td_" + resourceTypes.WebSite).on("click", {role: resourceTypes.WebSite}, selectIcon);
    $("#td_" + resourceTypes.Software).on("click", {role: resourceTypes.Software}, selectIcon);
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
});