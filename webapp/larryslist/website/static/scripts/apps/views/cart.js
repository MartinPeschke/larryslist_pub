define(["tools/ajax", "models/cart"], function(ajax, cart){

    var DropDown = Backbone.View.extend({
        initialize: function(opts){
            this.$total = this.$(".total");
            this.$total.html(cart.getItems().length);
            this.model = cart;
            this.listenTo(this.model, "item:changed", this.onCartChange);
        }
        , onCartChange: function(collector){
            this.$total.html(this.model.getItems().length);
        }
    });
    return {DropDown: function(opts){
        return new DropDown(opts);
    }};
});