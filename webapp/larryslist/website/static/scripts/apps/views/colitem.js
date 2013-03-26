define(
    ["tools/ajax", "models/cart", "models/user", "models/collector"
        , "text!templates/searchresult.html"
        , "text!templates/searchresult_full.html"]
    , function(ajax, cart, user, Collector, resultTempl, fullResultTempl){

    var
        resultTempl = _.template(resultTempl)
        , resultTemplFull = _.template(fullResultTempl)
        , SearchResults = ajax.Collection.extend({
            model: Collector
            , compField: "rank"
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
                this.each(function(m, idx){m.trigger('sort', m, idx)});
            }
        })

        , ResultView = Backbone.View.extend({
            events: {click:"toggleInCart"}
            , initialize: function(opts){
                this.setElement(opts.template({model: this.model, inCart:opts.inCart}));
                this.listenTo(this.model, "destroy", this.remove);
                this.listenTo(this.model, "cart:added", this.inCart);
                this.listenTo(this.model, "cart:removed", this.outCart);
                this.listenTo(this.model, "sort", this.reInsert);
                this.$button = this.$el.find(".btn");
                if(opts.inCart)this.setSelected(true);
            }
            , inCart: function(){this.setSelected(true)}
            , outCart: function(){this.setSelected(false)}
            , setSelected: function(selected){
                this.$el[selected?'addClass':'removeClass']("selected");
                var btnData = this.$button.data();
                this.$button.html(btnData[selected?'textUnselected':'textSelected'])[selected?'removeClass':'addClass']("btn-primary")[selected?'addClass':'removeClass']("btn-inverse");
                this.$el.trigger("collector:"+(selected?"selected":"unselected"));
            }
            , toggleInCart: function(){
                cart[cart.contains(this.model)?'removeProfile':'addProfile'](this.model);
            }
            , reInsert:function(model, idx){
                var root = this.$el.parent();
                root.append(this.$el.detach());
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
        , getView = function(collector, templ){
            var cls, v;
            if(user.ownsProfile(collector)){
                templ = templ || resultTemplFull;
                cls = FullResultView;
            } else {
                templ = templ || resultTempl;
                cls = ResultView;
            }
            v = new cls({model: collector, inCart: cart.contains(collector), template:templ})
            return v;
        };
    return {SearchResults:SearchResults, ResultView:ResultView, getView: getView};
});