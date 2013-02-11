(function (root, root_options) {
    var login = $("#login-pull-down-form")
    if(login.length){
        require(["tools/ajax"], function(ajax){
            ajax.ifyForm({root:login});
        });
    }
    require(["site"]);
})(hnc, window.__options__);