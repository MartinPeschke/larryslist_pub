define(["tools/ajax", "models/cart", "text!templates/cartpage_item.html"], function(ajax, cart, cartItem){

    var
        MODULE_KEY = 'CART_PAGE'
        , instance
        , CartItemView = Backbone.View.extend({
            template: _.template(cartItem)
            , events: {"click .dismiss": "destroy"}
            , initialize: function(opts){
                this.setElement(this.template({model: this.model}));
            }
            , destroy: function(e){
                this.model.destroy();
                this.remove();
            }
        })
        , View = Backbone.View.extend({
            initialize: function(opts){
                var view = this;
                this.model = cart;
                this.$body = this.$el.find(".cart-items");
                cart.getItems(function(items){
                    items.each(function(item){
                        var v = new CartItemView({model: item});
                        view.$body.append(v.$el);
                    });
                });
                this.listenTo(this.model, "Collectors:remove", function(){console.log(arguments)})
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