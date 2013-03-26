define(["tools/messaging", "tools/ajax"], function(messaging, ajax){
    var
        getRec = hnc.getRecursive
        , UserModel = ajax.Model

        , View = Backbone.View.extend({
            template : _.template($("#user-result-template").html())
            , events : {
                "click .close":"close"
            }
            , initialize: function(opts){
                var view = this;
                this.model = new UserModel();
                this.$resultsRoot = this.$(".results-wrapper")
                this.$el.find("input").eq(0).focus();
                ajax.ifyForm({
                    url:'/api/0.0.1/admin/search/userEmail'
                    , root: this.$el
                    , error: _.bind(this.onError, this)
                    , success: _.bind(this.onSuccess, this)
                })
            }
            , close: function(){
                this.$resultsRoot.empty().addClass("hide");
            }
            , onError : function(){
                this.$resultsRoot.html('<div class="control-group"><div class="controls error"><div class="empty">No user found</div></div></div>');
                this.$resultsRoot.removeClass("hide");
            }
            ,

            onSuccess: function(resp, status, xhr){
                if(!_.isEmpty(resp.User)){
                    this.$resultsRoot.find(".free-credits-form").off();
                    this.model.shallowClear();
                    this.model.setRecursive(resp.User);
                    this.$resultsRoot.html(this.template({user: this.model}))
                    var view = this;
                    var validator = ajax.ifyForm(
                        {
                            url:"/api/0.0.1/admin/feeder/freecredit"
                              , root: this.$resultsRoot.find(".free-credits-form")
                              , success: function(){
                               messaging.addSuccess({"message": $('#freeCredit').val() +  " credits added to " + view.model.get("email") + " users account!"})
                               view.onSuccess.apply(view, arguments);
                                }
                           }
                        );

                    this.$resultsRoot.removeClass("hide");
                } else {
                    this.onError();
                }
            }
        });
    return View;
});
