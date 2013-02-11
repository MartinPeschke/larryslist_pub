(function (root, root_options) {
    var login = $("#login-pull-down-form")
        , cart = $(".cart-dropdown-section");
    if(login.length){
        require(["tools/ajax"], function(ajax){
            ajax.ifyForm({root:login});
        });
    }

    if(cart.length){
        require(["views/cart"], function(CartViews){
            CartViews.DropDown({el: cart});
        });
    }

    require(["site"]);
})(hnc, window.__options__);