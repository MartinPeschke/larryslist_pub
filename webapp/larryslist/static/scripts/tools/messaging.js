define(["tools/hash"], function(hashlib){
    var STORAGE_KEY = 'LS_USER_MESSAGES'
        , sendMessageToUser = function(options){
            require(["tools/ajax"], function(ajax){
                options = options ||{};
                options.url = "/message/add";
                options.data = {UserMessage: [options.data]};
                ajax.submitAuthed(options);
            });
        }
        , replyMessage = function(msg, type){
            require(["models/loginstatus"], function(LoginStatus){
                msg.recipientId = msg.senderId;
                msg.recipientName = msg.senderName;
                msg.senderId = LoginStatus.get("id");
                msg.senderName = LoginStatus.getFullName();
                msg.requestType = msg.requestType+":"+type;
                sendMessageToUser({data:msg});
            });
        }
        , Message = Backbone.Model.extend({
            defaults:{ level : "info", title : null, message : null, added: 0}
            , initialize: function(json){
                var model = this;
                this.set({id: hashlib.fast(JSON.stringify(json))});
                if(this.get("level") == 'error'){
                    setTimeout(function(){model.clear();}, 10000);
                } else {
                    setTimeout(function(){model.clear();}, 5000);
                }
            }
            , isAction: function(){
                return this.get("level") == 'action';
            }
            , clear: function() {
                this.destroy();
            }
            , sync: function(){/*this is not synced anyways*/}
        })
        , Messages = Backbone.Collection.extend({
            model : Message
            , initialize:function () {
                this.on("add", this.save, this);
                this.on("remove", this.save, this);
                this.on("change:added", this.save, this);
            }
            , fetch: function(){
                var data = store.get(STORAGE_KEY), collection = this;
                if(data && data.length){
                    collection.reset(data);
                }
            }
            , save:function(){
                //store.set(STORAGE_KEY, this.toJSON())
            }
        })
        , MessageView = Backbone.View.extend({
            tagName: "div"
            , className: "alert"
            , events: {
                "click .close": "clear"
                ,"click .accept": "accept"
                ,"click .reject": "reject"
                ,"click .later": "later"
                ,"click .call-back": "callBack"
                }

            , template:_.template('<a class="close">×</a>{% if(title){ %}<strong>{{ title }}</strong> {% } %} {{ message }}')
            , actionTemplate:_.template('<span class="actionText">{% if(title){ %}<strong>{{ title }}</strong> {% } %} {{ message }}</span>')
            , number_templ:_.template('<span class="numbering">{{ added }}</span>')
            , initialize: function(){
                this.model.on('change:added', this.changedAdding, this);
                this.model.on('destroy', this.remove, this);
            }
            , accept: function(e){
                replyMessage(this.model.get("msg"), "ACCEPTED");
                this.model.destroy();
            }
            , reject: function(e){
                replyMessage(this.model.get("msg"), "REJECTED");
                this.model.destroy();
            }
            , later: function(e){
                replyMessage(this.model.get("msg"), "LATER");
                this.model.destroy();
            }
            , callBack: function(e){
                replyMessage(this.model.get("msg"), "CALL_BACK");
                this.model.destroy();
            }
            , changedAdding: function(model){
                var added = this.model.get("added");
                if(added>0){
                    if(!this.$el.find(".numbering").html(added+1).length){
                        this.$el.append(this.number_templ({added:added+1}));
                    }
                }
            }
            , render: function() {
                var added = this.model.get("added");
                if(this.model.isAction()){
                    this.$el.html(this.actionTemplate(this.model.toJSON()));
                    if(this.model.get("rejectLink")){
                        this.$el.append('<a class="btn btn-danger pull-right reject link" href="'+this.model.get("rejectLink")+'">Reject</a>');
                        this.$el.append('<a class="btn pull-right later link">Try later</a>');
                        this.$el.append('<a class="btn pull-right call-back link">I\'ll call back</a>');
                    }
                    if(this.model.get("acceptLink")){
                        this.$el.append('<a class="btn btn-primary accept pull-right link" href="'+this.model.get("acceptLink")+'">Accept</a>');
                    }
                } else {
                    this.$el.html(this.template(this.model.toJSON()));
                }
                this.$el.addClass("alert-"+this.model.get("level"));
                var added = this.model.get("added");
                if(added>0){
                  this.$el.append(this.number_templ({added:added+1}));
                }
                return this;
            }
            , clear: function() {
                this.model.clear();
            }
        })
        , View = Backbone.View.extend({
            initialize: function(){
                var view = this;
                this.model = new Messages();
                this.model.on('add', this.addOne, this);
                this.model.on('reset', this.addAll, this);
                this.model.on('all', this.render, this);
                this.model.fetch();
                this.baseOffset = $("header").height();
            }
            , addAll: function(){
                this.model.each(_.bind(this.addOne, this));
            }
            , addOne : function(model){
                var view = new MessageView({model: model});
                view.render().$el.appendTo(this.$el).closest(".message-container").fadeIn();
            }
            , render: function(){
                if(this.model.models.length){
                    this.$el.closest(".message-container").fadeIn();
                } else {
                    this.$el.closest(".message-container").fadeOut;
                }
            }
        })
        , view = new View({el: window.__options__.$messagingContainer})
        , addMessage = function(params){
            var model = new Message(params)
            try {
                view.model.add(model);
            } catch(err) {
                model = view.model.get(model.get("id"));
                model.set({"added": model.get("added")+1});
            }
        }
        , addError = function(params){
            addMessage(_.extend(params, {level:"error"}));
        }
        , addSuccess = function(params){
            addMessage(_.extend(params, {level:"success"}));
        }
        , addActionMessage = function(params){
            addMessage(_.extend(params, {level:"action"}));
        };

        return {view: view
            , addAction:addActionMessage
            , addSuccess:addSuccess
            , addError:addError
            , addMessage: addMessage
            , sendMessageToUser: sendMessageToUser
            , models:{Message:Message, Messages:Messages}
        };
    });
