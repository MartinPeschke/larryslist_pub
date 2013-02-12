define(["tools/ajax", "models/cart", "text!templates/cartpage_item.html", "text!templates/cartpage_item_mini.html"], function(ajax, cart, cartItem, miniItem){
    var
        MODULE_KEY = 'CART_PAGE'
        , instance
        , CartItemView = Backbone.View.extend({
            events: {"click .dismiss": "destroy"}
            , initialize: function(opts){
                this.setElement(opts.template({model: this.model}));
            }
            , destroy: function(e){
                this.model.destroy();
                this.remove();
            }
        })
        , View = Backbone.View.extend({
            initialize: function(opts){
                var view = this, t = _.template(opts.mini?miniItem:cartItem);;
                this.model = cart;
                this.$body = this.$el.find(".cart-items");

                cart.getItems(function(items){
                    items.each(function(item){
                        var v = new CartItemView({model: item, template: t});
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