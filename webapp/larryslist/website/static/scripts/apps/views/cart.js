define(["tools/ajax", "models/cart"], function(ajax, cart){

    var DropDown = Backbone.View.extend({
        initialize: function(opts){
            var view = this;
            this.$total = this.$(".total");
            cart.getItems(function(items){
                view.$total.html(items.length);
            });

            this.model = cart;
            this.listenTo(this.model, "item:changed", this.onCartChange);
        }
        , onCartChange: function(collector){
            var view = this;
            cart.getItems(function(items){
                view.$total.html(items.length);
            });
        }
    });
    return {DropDown: function(opts){
        return new DropDown(opts);
    }};
});