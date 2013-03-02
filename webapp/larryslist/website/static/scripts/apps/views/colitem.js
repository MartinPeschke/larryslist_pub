define(
    ["tools/ajax", "models/cart", "models/user", "models/collector"
        , "text!templates/searchresult.html"
        , "text!templates/searchresult_full.html"
        , "text!templates/flyout.html"]
    , function(ajax, cart, user, Collector, resultTempl, fullResultTempl, flyoutTempl){

    var
        resultTempl = _.template(resultTempl)
        , resultTemplFull = _.template(fullResultTempl)
        , SearchResults = ajax.Collection.extend({
            model: Collector
            , compField: "initials"
            , comparator : function(a, b){
                var v1 = a.get(this.compField), v2 = b.get(this.compField);
                if(v1==v2) return 0;
                else if(this.reversed) return v1>v2?-1:1;
                else return v1<v2?-1:1;
            }
            , reSort: function(field, reversed){
                this.compField = field;
                this.reversed = reversed;
                this.sort();
            }
        })

        , ResultView = Backbone.View.extend({
            events: {click:"toggleInCart"}
            , initialize: function(opts){
                this.setElement(opts.template({model: this.model, inCart:opts.inCart}));
                this.listenTo(this.model, "destroy", this.remove);
                this.listenTo(this.model, "cart:added", this.inCart);
                this.listenTo(this.model, "cart:removed", this.outCart);
                this.$button = this.$el.find(".btn");
                if(opts.inCart)this.setSelected(true);
            }
            , inCart: function(){this.setSelected(true)}
            , outCart: function(){this.setSelected(false)}
            , setSelected: function(selected){
                this.$el[selected?'addClass':'removeClass']("selected");
                var btnData = this.$button.data();
                this.$button.html(btnData[selected?'textUnselected':'textSelected'])[selected?'removeClass':'addClass']("btn-primary");
                this.$el.trigger("collector:"+(selected?"selected":"unselected"));
            }
            , toggleInCart: function(){
                cart[cart.contains(this.model)?'removeProfile':'addProfile'](this.model);
            }
            , destroy: function(){
                this.model.destroy();
            }
        })

        , OwnedResultView = Backbone.View.extend({
            initialize: function(opts){
                this.setElement(opts.template({model: this.model, inCart:opts.inCart, owned: opts.owned}));
                this.listenTo(this.model, "destroy", this.remove);

                var owned = this.$el.removeClass("selectable").addClass("owned");
                this.model.set("owned", owned);
                cart.removeProfile(this.model);
                this.$(".btn").replaceWith('<div class="label">Already subscribed</span>')
                this.$(".marked-checkbox").remove();
            }
            , destroy: function(){
                this.model.destroy();
            }
        })

        , FullResultView = Backbone.View.extend({
            events: {click:"gotoProfile"}
            , initialize: function(opts){
                this.setElement(opts.template({model: this.model, inCart:opts.inCart, owned: opts.owned}));
                this.listenTo(this.model, "destroy", this.remove);
            }
            , destroy: function(){
                this.model.destroy();
            }
            , gotoProfile: function(){
                window.location.href="/collector/"+this.model.id+"/"+encodeURIComponent(this.model.getFullName());
            }
        })

        , CartFlyout = Backbone.View.extend({
            template: _.template(flyoutTempl)
            , tagName: "div"
            , className: "cart-flyout"
            , initialize:function(opts){
                this.model = cart;
                this.listenTo(this.model, "item:changed", this.render);
                this.render();
                this.$el.appendTo(opts.root);
                this.offset = opts.root.offset();
                opts.root.on("collector:selected collector:unselected", _.bind(this.adjust, this));
            }
            , render: function(){
                var view = this;
                this.model.getItems(function(items){
                    var show = items.length>0;
                    view.$el.html(view.template({total:items.length, user: user}));
                    view.$el[show?'removeClass':'addClass']("invisi");
                });
            }
            , adjust: function(e){
                var pos = $(e.target).offset();
                this.$el.css({top:pos.top - this.offset.top});
            }
        })

        , getView = function(collector, templ, respectOwned){
            var cls, v;
            if(respectOwned && user.ownsProfile(collector)){
                templ = templ || resultTemplFull;
                cls = FullResultView;
            } else {
                templ = templ || resultTempl;
                cls = user.ownsProfile(collector)?OwnedResultView:ResultView;
            }
            v = new cls({model: cart.getProfile(collector), inCart: cart.contains(collector), template:templ})
            return v;
        };
    return {SearchResults:SearchResults, ResultView:ResultView, CartFlyout:CartFlyout, getView: getView};
});