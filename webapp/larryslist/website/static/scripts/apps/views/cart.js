define(["tools/ajax", "models/cart", "models/user", "text!templates/flyout.html"], function(ajax, cart, user, flyoutTmpl){

    var DropDown = Backbone.View.extend({
        template: _.template(flyoutTmpl)
        , initialize: function(opts){
            var view = this;
            this.$dropdown = this.$(".cart-attach-dropdown");
            this.$total = this.$(".total");
            cart.getItems(function(items){
                view.$dropdown.html(view.template({total: items.length, user: user}));
            });
            this.model = cart;
            this.listenTo(this.model, "item:changed", this.onCartChange);
        }
        , onCartChange: function(collector){
            var view = this;
            cart.getItems(function(items){
                view.$dropdown.html(view.template({total: items.length, credit: 0}));
            });
        }
    });
    return {DropDown: function(opts){
        return new DropDown(opts);
    }};
});