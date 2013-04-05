define(["tools/ajax", "models/cart", "models/user", "text!templates/flyout.html"], function(ajax, cart, user, flyoutTmpl){

    var DropDown = Backbone.View.extend({
        initialize: function(opts){
            var view = this, templ = this.$el.data("template");
            if(templ){
                require(["text!"+templ], function(template){
                    view.template =_.template(template);
                    view.render();
                })
            } else {
                view.template = _.template(flyoutTmpl);
                view.render();
            }
        }
        , render: function(){
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
                view.$dropdown.html(view.template({total: items.length, user: user}));
                view.$(".cart-total").html(items.length);
            });
        }
    })
    , FlyoutView = Backbone.View.extend({
        template: _.template(flyoutTmpl)
        , tagName: "div"
        , className: "cart-flyout"
        , initialize:function(opts){
            this.model = cart;
            this.alignTo = opts.root.children(".container").filter(":visible");
            this.$el.appendTo("body");

            this.render();
            this.listenTo(this.model, "item:changed", this.render);
        }
        , show:function(){
            this.$el.removeClass("invisi");
            this.adjust(this.$el, this.alignTo, $(window));
            $(window).on("scroll.cartflyout resize.cartflyout", _.bind(this.adjust, this, this.$el, this.alignTo, $(window)));
        }
        , hide: function(){
            this.$el.addClass("invisi");
            $(window).off("scroll.cartflyout resize.cartflyout");
        }
        , adjust : function($el, alignTo, $w){
            $el.css({top:$w.scrollTop() + $w.height() - $el.height() - 40, left: alignTo.offset().left + alignTo.width() + 20});
        }
        , render: function(){
            var view = this;
            this.model.getItems(function(items){
                var show = items.length>0;
                view.$el.html(view.template({total:items.length, user: user}));
                view[show?'show':'hide']();
            });
            this.$el.addClass("highlighted");
            _.delay(function($el){$el.removeClass("highlighted")}, 200, this.$el);
        }
    }), Flyout = new FlyoutView({root: $(".page-wrapper")});

    return {DropDown: function(opts){
        return new DropDown(opts);
    }, Flyout: Flyout};
});