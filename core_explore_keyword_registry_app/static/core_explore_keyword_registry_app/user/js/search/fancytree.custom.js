clearTree = function(div_tree, link) {
    if (!$(link).hasClass('disabled_refinements')) {
        var root =  $(div_tree).fancytree('getTree');
        if (root.length !== 0) {
            root.visit(function(node){
                node.setSelected(false);
            });
        }
    }
}