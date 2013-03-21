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
            cart.each(function(idx, elem){
                CartViews.DropDown({el: $(elem)});
            });


        });
    }


    $(".add-to-cart-link").on({
        click: function(e){
            require(["models/cart"], function(cart){
                var profile = $(e.currentTarget).data("profile");
                profile.updated = profile.updated||"2013-01-01T10:12:59Z100";
                profile.ranking = profile.ranking||0;
                profile.completness = profile.completness||0;
                profile.followers = profile.followers||0;
                if(_.isEmpty(profile.initials)){
                    profile.initials = _.map([profile.firstName, profile.lastName], function(w){return w[0]+"."}).join(" ");
                }

                cart.addProfile(profile);
            });
        }
    });


    require(["site"]);
})(hnc, window.__options__);