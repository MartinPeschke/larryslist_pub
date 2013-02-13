define(["tools/ajax", "models/cart", "models/user", "text!templates/cartpage_item.html", "text!templates/cartpage_item_mini.html"], function(ajax, cart, user, cartItem, miniItem){
    var
        MODULE_KEY = 'CART_PAGE'
        , instance

        , View = Backbone.View.extend({
            events : {'click .dismiss': "remove"}
            , initialize: function(opts){
                var view = this;
                this.model = cart;
            }
            , remove: function(e){
                var view = this, id = $(e.target).data("entityId");
                this.model.removeProfile({id: id});
                $(e.target).closest(".search-results-row").remove();
                var btn = this.$el.find(".js-spend-credit");
                cart.canSpend(user, function(canSpend){
                    btn.prop("disabled", !canSpend);
                    if(canSpend){
                        view.$(".insufficient-credits").fadeOut();
                    } else {
                        view.$(".insufficient-credits").fadeIn();
                    }
                });
            }
        })
        , init = function(opts){
            if(!instance){
                var opts = opts.pageconfig[MODULE_KEY];
                instance = new View(opts);
            }
            return instance;
        };
    return {init:init, View:View};
});