define(['tools/messaging', "tools/hash"], function(messaging, hashlib){
  var opts = window.__options__
  , ajax = {
      submit: function(options){
              var
              data = _.clone(options.data)
              , params = _.extend({
                  type: "POST"
                  , dataType: "json"
                  , contentType: "application/json; charset=utf-8"
              }, options || {});
              params.success = function (resp, status, xhr) {
                  if (resp.redirect) {
                      xhr.redirection = resp.redirect;
                      window.location.href = resp.redirect;
                  } else if (resp.dbMessage){
                        if(options.error){options.error(resp.dbMessage, resp, data);}
                        else {messaging.addError({message:hnc.translate(resp.dbMessage)})}
                  } else if (resp.errorMessage){
                      messaging.addError({message:hnc.translate(resp.errorMessage)});
                  } else if (options.success) options.success.apply(this, [resp, status, xhr, data]);
                  if(resp.message){
                      messaging[resp.success?'addSuccess':'addError']({message:resp.message})
                  }
              };
              params.error = params.error || function(xhr, status, msg){messaging.addError({message:msg});};
              if (typeof params.data != 'string') { params.data = JSON.stringify(params.data) }
              $.ajax(params);
      }
      , submitPrefixed: function(options){
            options.headers = {'Client-Token': opts.clientToken};
            options.url = '/api/0.0.1' + options.url;
            this.submit(options);
      }
      , submitAuthed: function(options){
        if(!_.isEmpty(opts.fb.user))
            options.data.token = opts.fb.user.token
        return ajax.submitPrefixed(options);
      }
      , resetForm : function(form){
          form = $(form).is("form.form-validated") ? $(form) : $(form).find("form.form-validated");
          form.find("input,textarea").val("");
          form.validate().resetForm();
          form.find(".btn").button("reset");
      }
      , serializeArray : function(list) {
          if(!list)return {};
          var json = {}, len = list.length, i=0, elem, key, value, keys, k, v, pos, j, add_in_fields;
          for(;i<len;i++){
              key = list[i].name;
              if(key){
                  value = list[i].value;
                  elem = json;
                  keys = key.split(".");
                  for(j=0;j<keys.length - 1;j++){
                      k = keys[j];
                      //iterate through indexed list
                      if(!!~k.indexOf("-")){
                          pos = parseInt(k.split("-")[1], 10);
                          k = k.split("-")[0];
                          if(!elem[k]) elem[k] = []
                          elem = elem[k];
                          add_in_fields = pos-elem.length+1;
                          for(var h=0; h<add_in_fields;h++)
                              elem.push({});
                          elem = elem[pos];
                      } else {
                          // this is just your average object
                          if(!elem[k]) elem[k] = {}
                          elem = elem[k];
                      }
                  }
                  //multi fields of same name submitted as array
                  k = keys[keys.length-1];
                  if(!_.isEmpty(elem[k])){
                      if(_.isArray(elem[k]))elem[k].push(value)
                      else elem[k] = [elem[k], value]
                  } else
                    elem[keys[keys.length-1]] = value;
              }
          }
          // filter out holes in indexed arrays
          var clean_empty = function(elem){
              if(_.isArray(elem)){
                  return _.filter(elem, function(e){return !_.isEmpty(e)});
              } else if(_.isObject(elem)){
                  _.each(elem, function(val, key){
                      elem[key] = clean_empty(val);
                  });
                  return elem;
              } else {
                return elem;
              }
          };
          return clean_empty(json);
      }
      , serializeJSON : function(form) {
          if($(form).is("form"))form = $(form)
          else form = $(form).find("form");
          return this.serializeArray(form.serializeArray());
      }
      , ifyForm: function(params, validationParams){
          var form = params.form||params.root
              , noop = function(e){e.preventDefault();e.stopPropagation();return false;}
              , baseFormsOnSubmit = function(form){
                  var $form = $(form), validator = $form.validate()
                      , data = ajax.serializeJSON($form);
                  $form.find("button,a.btn").button("loading");
                  if(params.submit)params.submit($form);
                  ajax.submit({
                      url: params.url||$form.attr("action")
                      , data: data
                      , error: params.error
                      , success: function(resp, status, xhr, data){
                          if(resp.success === false && resp.errors) {
                              var formId = $form.find("[name=type]").val();
                              for(var k in resp.errors) if(/--repetitions$/.test(k))delete resp.errors[k];
                              validator.showErrors(resp.errors);
                              for(var attr in resp.values){
                                  $form.find("#"+formId+"\\."+attr).val(resp.values[attr]);
                              }
                              $form.find(".error-hidden").hide(); // show any additional hints/elems
                              $form.find(".error-shown").fadeIn(); // show any additional hints/elems
                              if(params.error)params.error(resp, status, xhr, data)
                          } else {
                            if(resp.message){
                                messaging[resp.success?'addSuccess':'addError']({message:resp.message});
                            }
                            if(resp.success){
                                $form.trigger('form:saved', resp, status, xhr, data);
                                $form.removeClass("data-dirty");
                            }
                            params.success && params.success(resp, status, xhr, data);
                          }
                      }
                      , complete: function(xhr, status){
                          if(!xhr.redirection){
                            $(".loading").removeClass("loading");
                            $(form).find(".btn").button("reset");
                          }
                          if (params.complete) params.complete.apply(this, arguments);
                      }
                  });
              };
          if($(form).is("form.form-validated"))form = $(form)
          else form = $(form).find("form.form-validated");
          form.on({submit: noop, 'change':function(e, mod){ if(mod!='private')form.addClass("data-dirty")}});
          validationParams = validationParams||{};
          return hnc.validate(_.extend(validationParams, {root: form, submitHandler : baseFormsOnSubmit}));
      }
  };
  ajax.Model = Backbone.Model.extend({
          shallowClear : function(options){
              var clearance = {}, options=options||{};
              options.unset = true;
              for(var attr in this.attributes){
                  if(!_.isObject(this.get(attr))){
                      clearance[attr] = null;
                  }
              }
              this._hashValue = null;
              this.set(clearance, options);
          }
          , deepClear: function(){
              var clearance = {}, options=options||{};
              options.unset = true;
              for(var attr in this.attributes){
                  if(!_.isObject(this.get(attr))){
                      clearance[attr] = null;
                  } else if(_.isFunction(this.get(attr).shallowClear)){
                      this.get(attr).shallowClear();
                  } else if(_.isFunction(this.get(attr).addOrUpdate)){
                      this.get(attr).addOrUpdate([], {'preserve':false});
                  }
              }
              this._hashValue = null;
              this.set(clearance, options);
          }
          , save: function(options) {
              var model = this, data = {}, success = options.success;
              if(!options.data){

                  data[this.apiLabel] = this.toJSON();
                  options.data = data;
              }
              options.url = this.saveURL();
              options.success = function(resp, status, xhr){
                  model.setRecursive(resp[model.apiLabel]);
                  if(success)success(model)
              }
              ajax.submitAuthed(options);
          }
          /* PROXY NESTED EVENTS */
          , destroy: function(options){
              if(!_.isEmpty(this._nested)){
                  var len = this._nested.length, i;
                  for(i;i<len;i++){
                      this.get(this._nested[k]).invoke("destroy");
                  }
              }
              this.trigger('destroy', this, this.collection, options);
          }
          , register: function(models, options){
              var model, attr;
              this._nested = [];
              for(attr in models){
                  model = models[attr];
                  model.on("all", _.bind(this.onModelEvent, this, attr));
                  if(_.isFunction(model.invoke))this._nested.push(attr);
              }
              this.set(models, options);
              this.bind("destroy", _.bind(this._removeOnModelEvents, this, models));
          }
          , onModelEvent: function(attr, ev, evModel, collection, options){
              this.trigger.call(this, attr+":"+ev, evModel, collection, options);
          }
          ,_removeOnModelEvents: function(models) {
              var model, attr;
              for(attr in models){
                  model = models[attr];
                  models[attr].off("all", _.bind(this.onModelEvent, this, attr));
              }
          }
          , setRecursive: function(attrs, options){
              var setAttrs = {}
                  , curHash = this._hashValue
                  , newHash = hashlib.fast(JSON.stringify(attrs))
                  , transl = this.translation
                  , allKeys
                  , deferreds
                  , attr;
              // no need to parse deep, is all same anyways
              if(curHash && curHash == newHash)return;
              allKeys = this.removableKeys;
              for (attr in attrs) {
                  var val = attrs[attr], target = this.get(transl[attr]||attr);

                  if(target && _.isFunction(target.setRecursive)){
                      target.setRecursive(val, options);
                  } else if(target && _.isFunction(target.addOrUpdate)){
                      target.addOrUpdate(val, options);
                  } else {
                      setAttrs[attr] = val;
                  }
                  allKeys = _.without(allKeys, attr);
              }

              if(allKeys.length){
                  var keysToRemoveMap = {}, idx, key, val;
                  for(idx in allKeys){
                      key = allKeys[idx];
                      val = this.get(key);
                      if(val)
                          if(_.isFunction(val['clear']))
                              this.get(key).clear();
                          else
                              keysToRemoveMap[key] = true;
                  }
                  this.set(keysToRemoveMap, {unset: true});
              }

              this.set(this.parseLocal(setAttrs), options);
              this._hashValue = newHash;
          }
          , toJSON: function(){
              var json = {}, attr = this.attributes;
              for(var k in attr){
                    if(attr.hasOwnProperty(k))
                        if(attr[k]['toJSON'])
                            json[k] = attr[k].toJSON()
                        else
                            json[k] = attr[k]
              }
              return json;
          }
          , translation : {}
          , removableKeys : [] /*these will be removed if not present in refresh data */
          , parseLocal: function(model){return model}
  });
  ajax.Collection = Backbone.Collection.extend({
            model: ajax.Model
          , clear: function(opts){
              var i= 0, models = _.clone(this.models), len = models.length, tmp;
              for(;i<len;i++){
                  models[i].destroy(opts);
              }
          }
          , addOrUpdate: function(models, options){
              if(_.isEmpty(models)) models = [];
              options = options || {};
              models = _.isArray(models) ? models.slice() : [models];
              var i= 0, len = models.length, tmp, id, tmpModel, idAttr = this.idAttribute||"id", allIds = this.pluck(idAttr);
              for(;i<len;i++){
                  tmp = models[i];
                  id = tmp[idAttr]||hashlib.UUID();
                  tmpModel = this.get(id);
                  if(tmpModel){
                      tmpModel.setRecursive(tmp, options);
                  } else {
                      tmpModel = new this.model();
                      tmpModel.setRecursive(tmp, options);
                      this.add(tmpModel, options);
                  }
                  allIds = _.without(allIds, id);
              }
              if(!options.preserve){
                  for(i=0;i<allIds.length;i++){
                      tmp = this.get(allIds[i]);
                      if(tmp)tmp.destroy();
                  }
              }
              this.trigger(models.length?"updated":"emptied", this);
          }
          , fetch: function(options) {
              options.headers = options.headers || {};
              options.headers['Client-Token'] =  CLIENT_TOKEN;
              Backbone.Collection.prototype.fetch.call(this, options);
          }
      });
  ajax.View = Backbone.View.extend({
      sortedInsert: function(root, el, sortIndex){
          var i=0
              , tmp, data
              , nodes = root.children()
              , len = nodes.length
              , inserted = false;
          el.data("entitySort", sortIndex);
          for(;i<len;i++){
              tmp = nodes.eq(i);
              if(tmp.data("entitySort")>sortIndex){
                  tmp.before(el);
                  inserted = true;
                  break;
              }
          }
          if(!inserted){
              root.append(el);
          }
      }
  });
  return ajax;
});