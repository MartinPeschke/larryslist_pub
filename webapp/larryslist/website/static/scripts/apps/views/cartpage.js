define(["tools/ajax", "models/cart", "models/user", "views/colitem", "text!templates/searchresult.html"], function(ajax, cart, user, colItem, cartItem){
    var
        MODULE_KEY = 'CART_PAGE'
        , instance
        , templ = _.template(cartItem)
        , ItemView = colItem.ResultView.extend({
            outCart: function(){this.remove();}
        })
        , View = Backbone.View.extend({
            initialize: function(opts){
                var view = this;
                this.model = cart;
                this.$results = this.$(".cart-items");
                this.listenTo(this.model, "Collectors:add", this.add);
                this.listenTo(this.model, "Collectors:remove", this.remove);
                this.model.getItems(function(models){
                    models.each(this.add, this);
                }, this);
            }
            , add: function(collector){
                this.$results.append(new ItemView({model: collector, template: templ, inCart: true}).$el);
                this.$results.removeClass("is-empty");
            }
            , remove: function(){
                var empty = this.model.get("Collectors").length==0;
                this.$results[empty?'addClass':'removeClass']("is-empty");
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